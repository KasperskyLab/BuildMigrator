import os
import re
import subprocess
from build_migrator.modules import Parser


# Regular expression should provide the following capture groups (in order):
# * Double-quoted string
# * Single-quoted string
# * Escape characters
# * Pipe operator
# * Word
# * Whitespace
# * Fail
# 
# Each match is appended to an accumulator string until Pipe, Whitespace or Fail is found.
# * Whitespace/Pipe/End: accumulated string is considered a full argument and appended
#                        to the resulting list.
# * Fail: ValueError is raised.

POSIX_RX = re.compile(
    r""""((?:\\["\\]|[^"])*)"|'([^']*)'|(\\.)|(&&?|\|\|?|\d?\>|[<])|([^\s'"\\&|<>]+)|(\s+)|(.)"""
)
WINDOWS_RX = re.compile(
    r""""((?:""|\\["\\]|[^"])*)"?()|(\\\\(?=\\*")|\\")|(&&?|\|\|?|\d?>|[<])|([^\s"&|<>]+)|(\s+)|(.)"""
)
# Posix parser with Windows flavour
POSIX_ON_WINDOWS_RX = re.compile(
    r""""((?:\\"|[^"])*)"?()|(\\["\\&|<>*])|(&&?|\|\|?|\d?\>|[<])|((?:[^\s"\\&|<>]|\\(?!["\\&|<>*]))+)|(\s+)|(.)"""
)


class Platforms:
    Windows = "windows"
    Posix = "posix"
    PosixOnWindows = "posix_on_windows"


class CommandTokenizer(Parser):
    # see https://www.gnu.org/software/bash/manual/html_node/Redirections.html
    redirection_re = re.compile(
        r'(?P<src>\d|&)?(?P<op>(?:>>|>|<)(?:\||&)?)\s*["\']?(?P<dst>\d|[^\s"\']+)?["\']?$'
    )
    command_split_win32_re = re.compile(
        r"\b(?:\s+;\s*|\s*;\s+)(?:else|then|fi)?(\b|$)|&&|\|\|"
    )
    # Handle subshell commands: `(cd dir && gcc subdir/a.c -o a.o)`
    command_split_posix_re = re.compile(
        r"((?:^|\s)\([^\(\)]+\)(?:\s|$))|\b(?:\s+;\s*|\s*;\s+)(?:else|then|fi)?(\b|$)|&&|\|\|"
    )
    subcommand_split_re = re.compile(r"`(.+)`|\$\((.+)\)")

    priority = 4

    @staticmethod
    def add_arguments(arg_parser):
        arg_parser.add_argument(
            "--tokenizer_ruleset",
            choices=[Platforms.Windows, Platforms.Posix, Platforms.PosixOnWindows],
            help="Change command tokenization rules. Default is inferred from --platform. "
            "It is recommended to use {} to correctly parse make/ninja logs from Windows builds.".format(Platforms.PosixOnWindows),
        )
        arg_parser.add_argument(
            "--command_substitution",
            action="store_true",
            help="Enable command substitution in Posix-style (e.g. Makefile) "
            "logs. "
            "Examples: 'gcc `pwd`/a.c' or 'gcc $(pwd)/a.c' "
            "will expand into 'gcc <current working dir>/a.c'. "
            "WARNING: command is executed via Popen(shell=True), "
            "this may be a security hazard. Use at your own risk.",
        )

    @staticmethod
    def is_applicable(log_type=None):
        return log_type in ["make", "ninja", "msbuild"]

    def __init__(
        self, context, tokenizer_ruleset=None, command_substitution=None
    ):
        if command_substitution is None:
            command_substitution = False
        self.context = context
        self.parameters = {}
        self.platform = tokenizer_ruleset
        self.command_substitution = command_substitution
        if self.platform is None:
            self.platform = context.platform_name
        if self.platform == Platforms.Windows:
            self.regex = WINDOWS_RX
        elif self.platform == Platforms.PosixOnWindows:
            self.regex = POSIX_ON_WINDOWS_RX
        else:
            self.regex = POSIX_RX

    def parse(self, target):
        line = target.get("line")

        if not line:
            return target

        if self.platform != Platforms.Windows and self.command_substitution:
            res = self.subcommand_split_re.split(line)
            if len(res) >= 2:
                line = ""
                for literal, cmd1, cmd2 in zip(res[::3], res[1::3], res[2::3]):
                    subcommand = cmd1 or cmd2
                    prcs = subprocess.Popen(
                        subcommand,
                        shell=True,
                        cwd=self.context.working_dir,
                        stdout=subprocess.PIPE,
                    )
                    result = prcs.stdout.read().decode("utf-8")
                    result = re.sub(r"[\r\n]", "", result)
                    line += literal + result
                line += res[-1]

        if self.platform == Platforms.Windows:
            lines = self.command_split_win32_re.split(line)
        else:
            lines = self.command_split_posix_re.split(line)
        working_dir_stack = [target.get("working_dir")]
        targets = []
        for line in lines:
            if line is None:
                continue

            line = line.strip()
            if not line:
                continue

            if self.platform != Platforms.Windows:
                # Process subshell commands recursively
                if line.startswith("(") and line.endswith(")"):
                    targets.extend(
                        self.parse(
                            {"line": line[1:-1], "working_dir": working_dir_stack[-1]}
                        )
                    )
                    continue

            redirection = None
            while True:
                match = self.redirection_re.search(line)
                if match:
                    line = line[: match.start()].strip()
                    value = {
                        "src": match.group("src"),
                        "op": match.group("op"),
                        "dst": match.group("dst"),
                    }
                    if redirection:
                        redirection.insert(0, value)
                    else:
                        redirection = [value]
                else:
                    break

            # From https://www.gnu.org/software/bash/manual/bash.html#Definitions:
            # token: A sequence of characters considered a single unit by the shell. It is either a word or an operator.
            tokens = self.cmdline_split(line)
            if tokens and self.platform == Platforms.Windows and tokens[0] == "set":
                # set VAR=VALUE
                tokens = tokens[1:]
            last_parameter_token_idx = -1
            # see https://www.gnu.org/software/bash/manual/bash.html#Shell-Parameters
            for idx, token in enumerate(tokens):
                res = token.split("=", 1)
                if len(res) == 2:
                    last_parameter_token_idx = idx
                    self.parameters[res[0]] = res[1]
                else:
                    break

            tokens = tokens[last_parameter_token_idx + 1:]
            if not tokens:
                continue

            parameters = self.parameters
            self.parameters = {}

            # Handle directory manipulators
            if tokens[0] == "cd":
                path = os.path.join(working_dir_stack[-1], tokens[-1])
                working_dir_stack[-1] = path
                continue

            if tokens[0] == "pushd":
                working_dir_stack.append(
                    os.path.join(working_dir_stack[-1], tokens[-1])
                )
                continue

            if tokens[0] == "popd":
                working_dir_stack.pop()
                continue

            targets.append(
                {
                    "parameters": parameters,
                    "redirection": redirection,
                    "tokens": tokens,
                    "working_dir": working_dir_stack[-1],
                }
            )

        return targets

    # Current implementation is mostly taken from here:
    # https://stackoverflow.com/revisions/35900070/2 (by user kxr)
    def cmdline_split(self, s):
        """Multi-platform variant of shlex.split() for command-line splitting.
        """
        args = []
        accu = None  # collects pieces of one arg
        for qs, qss, esc, pipe, word, white, fail in self.regex.findall(s):
            if word:
                pass  # most frequent
            elif esc:
                word = esc[1]
            elif white or pipe:
                if accu is not None:
                    args.append(accu)
                if pipe:
                    args.append(pipe)
                accu = None
                continue
            elif fail:
                raise ValueError("invalid or incomplete shell string")
            elif qs:
                if self.platform == Platforms.Windows:
                    word = word.replace('""', '"')
                word = qs.replace('\\"', '"').replace("\\\\", "\\")
            else:
                word = qss  # may be even empty; must be last

            accu = (accu or "") + word

        if accu is not None:
            args.append(accu)

        return args


__all__ = ["CommandTokenizer"]
