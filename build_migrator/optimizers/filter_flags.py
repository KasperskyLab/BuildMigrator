import logging
import re
import sys
from build_migrator.modules import Optimizer
from build_migrator.common.algorithm import add_unique_stable
from build_migrator.common.argparse_actions import Extend


if sys.version_info[0] >= 3:
    unicode = str


logger = logging.getLogger(__name__)


class FilterFlags(Optimizer):
    priority = 1

    @staticmethod
    def add_arguments(arg_parser):
        arg_parser.add_argument(
            "--keep_flags",
            metavar="REGEX",
            nargs="+",
            help="Keep only matching compiler and linker flags in Build Object Model. "
            "By default, all flags are kept.",
            action=Extend,
        )
        arg_parser.add_argument(
            "--delete_flags",
            metavar="REGEX",
            nargs="+",
            help="Delete matching compiler and linker flags. "
            "This option comes into effect after --keep_flags. "
            "Keep in mind, that this option is processed after build log object "
            "model has already been constructed. Which means that if some flag "
            "introduces an unwanted dependency into targets, this option will "
            "not delete that dependency. If this behavior is not desired, "
            "--ignore_compile_flags and --ignore_link_flags should be used.",
            action=Extend,
        )
        arg_parser.add_argument(
            "--replace_flag",
            metavar=("REGEX", "REPL"),
            nargs=2,
            action="append",
            dest="replace_flags",
            help="Replace matching compiler and linker flags. "
            "This option comes into effect after --delete_flags.",
        )

    def __init__(
        self,
        context,
        keep_flags=None,
        delete_flags=None,
        replace_flags=None,
        platform=None,
    ):
        self._keep_compile_flags_rxs = []
        self._delete_compile_flags_rxs = []
        self._keep_link_flags_rxs = []
        self._delete_link_flags_rxs = []
        self._compile_flags_replacements = []
        self._link_flags_replacements = []

        for s in keep_flags or []:
            self._keep_compile_flags_rxs.append(re.compile(s))
            self._keep_link_flags_rxs.append(re.compile(s))

        if self._keep_compile_flags_rxs:
            # Keep all include dirs by default. Include dirs
            # can only be explicitly deleted via --delete-flags.
            self._keep_compile_flags_rxs.append(re.compile(r"^[-/]I"))

        if delete_flags:
            for s in delete_flags:
                self._delete_compile_flags_rxs.append(re.compile(s))
                self._delete_link_flags_rxs.append(re.compile(s))

        for pattern, repl in replace_flags or []:
            self._compile_flags_replacements.append((re.compile(pattern), repl))
            self._link_flags_replacements.append((re.compile(pattern), repl))
        self.context = context

    @staticmethod
    def _filter_flags(keep_rxs, delete_rxs, flags, include_dir_mode=False):
        filtered_flags = []
        for f in flags:
            if isinstance(f, str) or isinstance(f, unicode):
                value = f
            else:
                # multiargument flag
                value = " ".join(f)

            if include_dir_mode:
                value = "-I" + value

            remove = False
            for r in delete_rxs:
                if r.search(value):
                    remove = True
                    break

            if not remove and len(keep_rxs) > 0:
                remove = True
                for r in keep_rxs:
                    if r.search(value):
                        remove = False
                        break

            if not remove:
                filtered_flags.append(f)
            else:
                logger.debug(" * FilterFlags: removed: %r" % f)

        return filtered_flags

    @classmethod
    def _replace_flags(cls, repls, flags):
        replaced_flags = []
        for f in flags:
            for r, repl in repls:
                if isinstance(f, str):
                    f = r.sub(repl, f)
                else:
                    f = cls._replace_flags(repls, f)

            replaced_flags.append(f)

        return replaced_flags

    def optimize(self, targets):
        for target in targets:
            if target["type"] != "module":
                continue

            for src in target.get("sources") or []:
                logger.debug(src["path"])

                src["compile_flags"] = add_unique_stable(list(), *src["compile_flags"])
                src["include_dirs"] = add_unique_stable(list(), *src["include_dirs"])

                src["compile_flags"] = self._filter_flags(
                    self._keep_compile_flags_rxs,
                    self._delete_compile_flags_rxs,
                    src["compile_flags"],
                )
                src["compile_flags"] = self._replace_flags(
                    self._compile_flags_replacements, src["compile_flags"]
                )

                src["include_dirs"] = self._filter_flags(
                    self._keep_compile_flags_rxs,
                    self._delete_compile_flags_rxs,
                    src["include_dirs"],
                    True,
                )
                src["include_dirs"] = self._replace_flags(
                    self._compile_flags_replacements, src["include_dirs"]
                )

            logger.debug(target["output"])

            target["compile_flags"] = add_unique_stable(
                list(), *target["compile_flags"]
            )
            target["include_dirs"] = add_unique_stable(list(), *target["include_dirs"])
            target["link_flags"] = add_unique_stable(list(), *target["link_flags"])

            target["compile_flags"] = self._filter_flags(
                self._keep_compile_flags_rxs,
                self._delete_compile_flags_rxs,
                target["compile_flags"],
            )
            target["compile_flags"] = self._replace_flags(
                self._compile_flags_replacements, target["compile_flags"]
            )

            target["include_dirs"] = self._filter_flags(
                self._keep_compile_flags_rxs,
                self._delete_compile_flags_rxs,
                target["include_dirs"],
                True,
            )
            target["include_dirs"] = self._replace_flags(
                self._compile_flags_replacements, target["include_dirs"]
            )

            if target.get("link_flags"):
                target["link_flags"] = self._filter_flags(
                    self._keep_link_flags_rxs,
                    self._delete_link_flags_rxs,
                    target["link_flags"],
                )
                target["link_flags"] = self._replace_flags(
                    self._link_flags_replacements, target["link_flags"]
                )

        return targets


__all__ = ["FilterFlags"]
