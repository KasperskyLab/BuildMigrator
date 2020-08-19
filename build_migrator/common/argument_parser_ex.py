from argparse import Namespace
from copy import copy, deepcopy
from functools import partial
import logging
import traceback
import uuid

logger = logging.getLogger(__name__)


class SavepointContextManager(object):
    def __init__(self, savepoint_id, all_savepoints, state):
        if savepoint_id in all_savepoints:
            raise ValueError("Savepoint already exists: %r" % savepoint_id)
        self._dismissed = False
        self._savepoint = all_savepoints.setdefault(savepoint_id, {})
        self._state_dict = state.__dict__
        self._id = savepoint_id
        self._savepoints = all_savepoints

    def dismiss(self):
        self._dismissed = True

    # TODO: come up with a meaningful name
    def get_token_diff(self, state):
        """
        Get tokens that were removed or modified between currently saved state
        and state provided in the argument.
        """
        cur_tokens = state._tokens
        old_tokens = self._savepoint.get("_tokens")
        if old_tokens:
            diff = len(old_tokens) - len(cur_tokens)
            if diff == 0 and old_tokens[0] != cur_tokens[1]:
                # leading token was modified
                diff = 1
            return old_tokens[0:diff]
        else:
            return []

    def load(self):
        self._state_dict.update(self._savepoint)

    def cleanup(self):
        self._savepoints.pop(self._id)
        self._savepoint = None
        self._id = None

    def __enter__(self):
        return self

    def __exit__(self, *exception_args):
        if not self._dismissed:
            self.load()
        self.cleanup()


class TokenParserState(object):
    def __init__(self, tokens, namespace=None):
        if namespace is None:
            namespace = Namespace()
        self._namespace = namespace
        self._tokens = tokens
        self._savepoints = {}
        self._storage = {}

    def next_tokens(self, n):
        if len(self._tokens) >= n:
            self._save_attribute("_tokens")
            tokens = self._tokens[0:n]
            self._tokens = self._tokens[n:]
            return tokens
        return None

    def get_tokens_length(self):
        return len(self._tokens)

    def get_token(self, idx):
        return deepcopy(self._tokens[idx])

    def set_token(self, idx, value, savepoint=True):
        if savepoint:
            self._save_attribute("_tokens")
        self._tokens[idx] = value

    def get_attribute(self, name, default):
        return deepcopy(getattr(self._namespace, name, default))

    def set_attribute(self, name, value, savepoint=True):
        if savepoint:
            self._save_attribute("_namespace")
        setattr(self._namespace, name, value)

    def set_attribute_first(self, name, value, savepoint=True):
        if savepoint:
            self._save_attribute("_namespace")
        if isinstance(value, list):
            value = value[0]
        setattr(self._namespace, name, value)

    def append_attribute(self, name, value, savepoint=True):
        cur_value = self.get_attribute(name, [])
        cur_value.append(value)
        if savepoint:
            self._save_attribute("_namespace")
        setattr(self._namespace, name, cur_value)

    def extend_attribute(self, name, value, savepoint=True):
        cur_value = self.get_attribute(name, [])
        cur_value.extend(value)
        if savepoint:
            self._save_attribute("_namespace")
        setattr(self._namespace, name, cur_value)

    def append_or_extend_attribute(self, name, value, savepoint=True):
        if len(value) <= 1:
            self.extend_attribute(name, value, savepoint=savepoint)
        else:
            self.append_attribute(name, value, savepoint=savepoint)

    def fetch(self, context, key, default=None):
        return deepcopy(self._storage.get(self._get_full_key(context, key), default))

    def store(self, context, key, value):
        self._save_attribute("_storage")
        self._storage[self._get_full_key(context, key)] = value

    def save(self, context):
        return SavepointContextManager(str(id(context)), self._savepoints, self)

    def finalize(self):
        if len(self._savepoints):
            raise ValueError("Orphaned savepoints found")
        if len(self._tokens):
            raise ValueError("Cannot finalize, tokens left: %r" % self._tokens)
        return self._namespace

    def _get_full_key(self, context, key):
        if context is not None:
            key = str(id(context)) + "." + key
        return key

    def _save_attribute(self, name):
        for _id, dict in self._savepoints.items():
            if name not in dict:
                dict[name] = deepcopy(self.__dict__[name])


class TokenParser(object):
    def __init__(self, rules=None, validators=None):
        if rules is None:
            rules = []
        if validators is None:
            validators = []
        self._rule = Any(*rules)
        self._validators = validators

    def parse(self, tokens, namespace=None, strict=True, unknown_dest=None):
        state = TokenParserState(tokens, namespace)

        unparsed_tokens = []
        while state.get_tokens_length() > 0:
            if self._rule(state):
                continue
            skip_n = 1
            if strict:
                skip_n = state.get_tokens_length()
            tokens = state.next_tokens(skip_n)
            if unknown_dest is not None:
                if isinstance(unknown_dest, list):
                    dests = unknown_dest
                else:
                    dests = [unknown_dest]
                for dest in dests:
                    state.extend_attribute(dest, tokens, savepoint=False)
            unparsed_tokens.extend(tokens)

        if len(unparsed_tokens) > 0 and strict:
            raise ValueError("Unparsed tokens: %r" % unparsed_tokens)

        namespace = state.finalize()
        for validator in self._validators:
            try:
                validator(namespace)
            except Exception:
                if strict:
                    raise
                else:
                    logger.warning(traceback.format_exc())

        if strict:
            return namespace
        else:
            return namespace, unparsed_tokens


class Skip(object):
    def __init__(self, n=1):
        self._n = n

    def __call__(self, state):
        return state.next_tokens(self._n) is not None


class Check(object):
    def __init__(self, function):
        self._condition = function

    def __call__(self, state):
        if state.get_tokens_length() == 0:
            return False
        return self._condition(state.get_token(0))


class IsEmpty(Check):
    def __init__(self):
        super(IsEmpty, self).__init__(lambda t: len(t) == 0)


class IsIn(Check):
    def __init__(self, *values, **kwargs):
        ignore_case = kwargs.get("ignore_case")
        if ignore_case:
            values = [v.lower() for v in values]
            super(IsIn, self).__init__(lambda t: t.lower() in values)
        else:
            super(IsIn, self).__init__(lambda t: t in values)


class Not(object):
    def __init__(self, rule):
        self._rule = rule

    def __call__(self, state):
        with state.save(self) as savepoint:
            if self._rule(state):
                return False
            savepoint.dismiss()
        return True


class Transform(object):
    def __init__(self, function):
        self._transform = function

    def __call__(self, state):
        if state.get_tokens_length() == 0:
            return False
        try:
            token = self._transform(state.get_token(0))
            if token is not None:
                state.set_token(0, token)
                return True
        except Exception:
            logger.debug(traceback.format_exc())
        return False


class RemovePrefix(Transform):
    def __init__(self, *prefixes):
        super(RemovePrefix, self).__init__(partial(self._remove_prefix, prefixes))

    @staticmethod
    def _remove_prefix(prefixes, token):
        for p in prefixes:
            if token.startswith(p):
                return token[len(p) :]
        return None


class RemovePrefixCaseInsensitive(Transform):
    def __init__(self, *prefixes):
        super(RemovePrefixCaseInsensitive, self).__init__(
            partial(self._remove_prefix, prefixes)
        )

    @staticmethod
    def _remove_prefix(prefixes, token):
        token_lower = token.lower()
        for p in prefixes:
            if token_lower.startswith(p.lower()):
                return token[len(p) :]
        return None


class Nargs:
    OPTIONAL = "?"
    ZERO_OR_MORE = "*"
    ONE_OR_MORE = "+"


def nargs_to_min_max(nargs):
    if nargs == Nargs.OPTIONAL:
        return 0, 1
    elif nargs == Nargs.ZERO_OR_MORE:
        return 0, None
    elif nargs == Nargs.ONE_OR_MORE:
        return 1, None
    else:
        return int(nargs), int(nargs)


class All(object):
    def __init__(self, *rules):
        self._rules = rules

    def __call__(self, state):
        with state.save(self) as savepoint:
            for rule in self._rules:
                if not rule(state):
                    return False
            savepoint.dismiss()
            return True


class Any(object):
    def __init__(self, *rules):
        self._rules = rules

    def __call__(self, state):
        with state.save(self) as savepoint:
            for rule in self._rules:
                if rule(state):
                    savepoint.dismiss()
                    return True
            return False


class Limiter(object):
    def __init__(self, nargs):
        unused_, self._limit = nargs_to_min_max(nargs)

    def __call__(self, state):
        counter = state.fetch(self, "counter", 0)
        if self._limit is not None and counter >= self._limit:
            return False
        state.store(self, "counter", counter + 1)
        return True


class SetAttribute(object):
    @staticmethod
    def get_default_handler(nargs):
        if not nargs:  # 0 or None
            return TokenParserState.set_attribute_first
        else:
            return TokenParserState.set_attribute

    def __init__(
        self,
        dest,
        nargs=None,
        const=None,
        choices=None,
        type=None,
        regexp=None,
        prefix_chars=None,
        handler=None,
    ):
        if nargs is not None:
            self._min, self._max = nargs_to_min_max(nargs)
        else:
            self._max = 1
            self._min = 1
        if handler is None:
            handler = self.get_default_handler(nargs)
        self._choices = choices
        self._const = const
        self._dest = dest
        self._prefix_chars = prefix_chars
        self._regexp = regexp
        self._type = type
        self._handler = handler

    def _get_tokens(self, state):
        tokens = []
        with state.save(self) as savepoint:
            while self._max is None or len(tokens) < self._max:
                if state.get_tokens_length() == 0:
                    break
                token = state.get_token(0)
                if self._regexp:
                    if not self._regexp.match(token):
                        break
                if self._choices:
                    if token not in self._choices:
                        break
                if token.startswith(self._prefix_chars) and len(tokens) >= self._min:
                    # break at tokens that look like flags when enough values has already been collected
                    break
                if self._const is not None:
                    token = self._const
                elif self._type:
                    try:
                        token = self._type(token)
                    except Exception:
                        logger.debug(traceback.format_exc())
                        break
                tokens.append(token)
                state.next_tokens(1)
            if len(tokens) < self._min:
                return None
            savepoint.dismiss()
        if self._const is not None and self._max == 0:
            # special case for boolean flags like --enable-something
            tokens = [self._const]
        return tokens

    def __call__(self, state):
        tokens = self._get_tokens(state)
        if tokens is None:
            return False
        self._handler(state, self._dest, tokens)
        return True


class AppendToAttribute(SetAttribute):
    @staticmethod
    def get_default_handler(nargs):
        if not nargs:  # 0 or None
            return TokenParserState.extend_attribute
        else:
            return TokenParserState.append_attribute

    def __call__(self, state):
        tokens = self._get_tokens(state)
        if tokens is None:
            return False
        self._handler(state, self._dest, tokens)
        return True


class AppendTokensConsumedByRule(object):
    @staticmethod
    def get_default_handler(*args):
        return TokenParserState.append_or_extend_attribute

    def __init__(self, dest, rule, format=None, handler=None):
        if handler is None:
            handler = self.get_default_handler()
        self._dest = dest
        self._rule = rule
        self._format = format
        self._handler = handler

    def __call__(self, state):
        with state.save(self) as savepoint:
            if not self._rule(state):
                return False
            diff = savepoint.get_token_diff(state)
            if self._format:
                diff = self._format(diff)
            savepoint.dismiss()
            if diff:
                # TODO: HACK: list support in raw_dest is temporary until a better solution comes up
                if isinstance(self._dest, list):
                    dests = self._dest
                else:
                    dests = [self._dest]
                for dest in dests:
                    self._handler(state, dest, diff)
        return True


class RequireAttribute(object):
    def __init__(self, dest, context=None):
        self._dest = dest
        self._context = context

    def __call__(self, namespace):
        if getattr(namespace, self._dest, None) is None:
            msg_context = ""
            if self._context and self._dest != self._context:
                msg_context = " (%s)" % self._context
            raise ValueError(
                "Required attribute not found: %s%s" % (self._dest, msg_context)
            )


class SetDefaultAttributeValue(object):
    def __init__(self, dest, value):
        self._dest = dest
        self._value = value

    def __call__(self, namespace):
        if getattr(namespace, self._dest, None) is None:
            setattr(namespace, self._dest, deepcopy(self._value))


class RemoveAttribute(object):
    def __init__(self, dest):
        self._dest = dest

    def __call__(self, namespace):
        if hasattr(namespace, self._dest):
            delattr(namespace, self._dest)


class ValidateAttributeValueCount(object):
    def __init__(self, dest, nargs, context=None):
        self._dest = dest
        self._min, self._max = nargs_to_min_max(nargs)
        self._context = context

    def __call__(self, namespace):
        values = getattr(namespace, self._dest, None)
        if values is not None:
            if not isinstance(values, list):
                values = [values]
            msg_context = ""
            if self._context:
                msg_context = " (%s)" % self._context
            if self._min is not None and len(values) < self._min:
                raise ValueError(
                    "Not enough values (<%d) were found for "
                    "attribute %s%s: %r" % (self._min, msg_context, self._dest, values)
                )
            if self._max is not None and len(values) > self._max:
                # Is this even possible?
                raise ValueError(
                    "Too many values (>%d) were found for "
                    "attribute %s%s: %r" % (self._max, msg_context, self._dest, values)
                )


class ArgumentParserEx(object):
    def __init__(
        self,
        prefix_chars="-",
        prog=None,
        usage=None,
        description=None,
        epilog=None,
        parents=None,
        formatter_class=None,
        fromfile_prefix_chars=None,
        argument_default=None,
        conflict_handler=None,
        add_help=None,
    ):
        self._kwargs = {"prefix_chars": prefix_chars}

        self._action_to_rule = {
            None: self._get_store_rule,
            "store": self._get_store_rule,
            "store_const": self._get_store_const_rule,
            "store_true": self._get_store_true_rule,
            "store_false": self._get_store_false_rule,
            "append": self._get_append_rule,
            "append_const": self._get_append_const_rule,
            "msvc_flag": self._get_msvc_flag_rule,
            "msvc_flag_with_value": self._get_msvc_flag_with_value,
        }

        self._rules = []
        self._validators = []
        self._invalidate_parser()

    def add_argument(self, *args, **kwargs):
        kwargs.pop("help", None)
        kwargs.pop("metavar", None)
        _kwargs = copy(self._kwargs)
        _kwargs.update(kwargs)
        kwargs = _kwargs

        for c in kwargs.get("dest") or "":
            if c != "_" and not str.isalnum(c):
                raise ValueError("Invalid dest: %r" % kwargs.get("dest"))

        if args and args[0][0] in kwargs["prefix_chars"]:
            kwargs = self._get_optional_kwargs(*args, **kwargs)
        elif "prefixes" in kwargs or "flags" in kwargs:
            kwargs = self._get_optional_kwargs(*args, **kwargs)
        else:
            kwargs = self._get_positional_kwargs(*args, **kwargs)

        get_rule = self._action_to_rule[kwargs.get("action")]
        if "action" in kwargs:
            del kwargs["action"]
        rule, validators = get_rule(**kwargs)
        self._rules.append(rule)
        self._invalidate_parser()
        self._validators.extend(validators)
        return rule

    def parse_args(self, args, namespace=None):
        self._ensure_parser_is_ready()
        return self._parser.parse(args, strict=True, namespace=namespace)

    def parse_known_args(self, args, namespace=None, unknown_dest=None):
        self._ensure_parser_is_ready()
        return self._parser.parse(
            args, strict=False, namespace=namespace, unknown_dest=unknown_dest
        )

    def set(self, **kwargs):
        self._kwargs.update(kwargs)

    def set_defaults(self, **kwargs):
        for dest, default in kwargs.items():
            self._validators.append(SetDefaultAttributeValue(dest, default))

    def _get_append_rule(self, **kwargs):
        kwargs["append"] = True
        return self._get_store_rule(**kwargs)

    def _get_append_const_rule(self, **kwargs):
        if kwargs.get("const") is None:
            raise ValueError("const is required")
        kwargs["nargs"] = 0
        return self._get_append_rule(**kwargs)

    def _get_msvc_flag_rule(self, **kwargs):
        kwargs["const"] = True
        flags = kwargs["flags"]
        msvc_false_suffix = "-"
        if "msvc_false_suffix" in kwargs:
            msvc_false_suffix = kwargs["msvc_false_suffix"]
            del kwargs["msvc_false_suffix"]
        msvc_true_suffix = ""
        if "msvc_true_suffix" in kwargs:
            msvc_true_suffix = kwargs["msvc_true_suffix"]
            del kwargs["msvc_true_suffix"]
        kwargs["flags"] = [f + msvc_true_suffix for f in flags]
        kwargs["nargs"] = 0
        del kwargs["prefixes"]
        rule1, validators1 = self._get_rule(**kwargs)
        kwargs["const"] = False
        kwargs["flags"] = [f + msvc_false_suffix for f in flags]
        rule2, validators2 = self._get_rule(**kwargs)
        return Any(rule1, rule2), validators1 + validators2

    def _get_msvc_flag_with_value(self, **kwargs):
        kwargs["prefixes"] = [f + ":" for f in kwargs["flags"]]
        del kwargs["flags"]
        return self._get_rule(**kwargs)

    def _get_store_rule(self, **kwargs):
        if "default" not in kwargs:
            kwargs["default"] = None
        return self._get_rule(**kwargs)

    def _get_store_const_rule(self, **kwargs):
        if kwargs.get("const") is None:
            raise ValueError("const is required")
        kwargs["nargs"] = 0
        return self._get_store_rule(**kwargs)

    def _get_store_false_rule(self, **kwargs):
        kwargs["const"] = False
        kwargs["default"] = True
        return self._get_store_const_rule(**kwargs)

    def _get_store_true_rule(self, **kwargs):
        kwargs["const"] = True
        kwargs["default"] = False
        return self._get_store_const_rule(**kwargs)

    class _Default(object):
        pass

    @staticmethod
    def _get_rule(
        flags=None,
        prefixes=None,
        args_regexp=None,
        name=None,
        dest=None,
        nargs=None,
        required=None,
        const=None,
        type=None,
        choices=None,
        default=_Default(),
        append=None,
        ignore_case=None,
        prefix_chars=None,
        raw_dest=None,
        raw_format=None,
        handler=None,
        raw_handler=None,
    ):
        remove_dest_after_validation = dest is None
        if remove_dest_after_validation:
            dest = "@anonymous_" + uuid.uuid4().hex[:8]
        validation_error_context = None
        rule = None
        validators = []

        if flags or prefixes:
            # optional argument
            value_isolation_rules = []
            if flags:
                validation_error_context = flags[0]
                value_isolation_rules.append(
                    All(IsIn(*flags, ignore_case=ignore_case), Skip())
                )
            else:
                validation_error_context = prefixes[0]
            # nargs == 0 means that the flag doesn't expect a value.
            # In this case we don't have to handle suffix values like
            # -arg=value or -fvalue
            if nargs != 0 and prefixes:
                # rule for suffix values
                remove_prefix = RemovePrefix
                if ignore_case:
                    remove_prefix = RemovePrefixCaseInsensitive
                value_isolation_rules.append(
                    All(remove_prefix(*prefixes), Not(IsEmpty()))
                )
            setter = SetAttribute
            if append:
                setter = AppendToAttribute
            rule = All(
                Any(*value_isolation_rules),
                setter(
                    dest,
                    nargs,
                    const=const,
                    type=type,
                    choices=choices,
                    regexp=args_regexp,
                    prefix_chars=prefix_chars,
                    handler=handler,
                ),
            )
        else:
            # positional argument
            validation_error_context = name
            setter = AppendToAttribute
            limiter_nargs = nargs or Nargs.ZERO_OR_MORE
            if not append:
                if nargs is None:
                    limiter_nargs = 1
                    setter = SetAttribute
                else:
                    validators.append(
                        ValidateAttributeValueCount(
                            dest, nargs, context=validation_error_context
                        )
                    )
                nargs = None

            rule = All(
                Not(RemovePrefix(*prefix_chars)),
                Limiter(limiter_nargs),
                setter(
                    dest,
                    nargs,
                    type=type,
                    choices=choices,
                    regexp=args_regexp,
                    prefix_chars=prefix_chars,
                    handler=handler,
                ),
            )
        if not isinstance(default, ArgumentParserEx._Default):
            validators.append(SetDefaultAttributeValue(dest, default))
        if required:
            validators.append(RequireAttribute(dest, context=validation_error_context))
        if remove_dest_after_validation:
            validators.append(RemoveAttribute(dest))
        if raw_dest:
            rule = AppendTokensConsumedByRule(
                raw_dest, rule, format=raw_format, handler=raw_handler
            )
        return rule, validators

    def _invalidate_parser(self):
        self._parser = None

    def _ensure_parser_is_ready(self):
        if not self._parser:
            self._parser = TokenParser(self._rules, self._validators)

    def _get_positional_kwargs(self, name, **kwargs):
        """Prepare kwargs for positional arguments"""
        required = False
        if kwargs.get("nargs") not in [Nargs.OPTIONAL, Nargs.ZERO_OR_MORE]:
            required = True
        if kwargs.get("nargs") == Nargs.OPTIONAL:
            kwargs["default"] = None
        if kwargs.get("nargs") == Nargs.ZERO_OR_MORE:
            kwargs["default"] = []
        if "dest" in kwargs:
            dest = kwargs.pop("dest")
        else:
            dest = name
        return dict(kwargs, name=name, dest=dest, required=required)

    def _get_optional_kwargs(self, *args, **kwargs):
        """Prepare kwargs for optional arguments (flags)"""
        flags = kwargs.get("flags") or []
        prefixes = kwargs.get("prefixes") or []
        prefix_chars = kwargs["prefix_chars"]
        enable_suffix_value = None
        if "prefix" in kwargs:
            enable_suffix_value = kwargs["prefix"]
            del kwargs["prefix"]

        # long flag: --flag value or --flag=value
        long_flags = []
        # short flag: -f value of -fvalue
        short_flags = []
        for flag in args:
            if not flag[0] in prefix_chars:
                raise ValueError(
                    "Invalid flag '%r': must start with [%r]" % (flag, prefix_chars)
                )

            if len(flag) > 2:
                long_flags.append(flag)
            else:
                short_flags.append(flag)

        if "dest" not in kwargs:
            # infer destination, '--foo-bar' -> 'foo_bar' and '-x' -> 'x'
            if long_flags:
                dest_flag = long_flags[0]
            elif short_flags:
                dest_flag = short_flags[0]
            elif flags:
                dest_flag = flags[0]
            elif prefixes:
                dest_flag = prefixes[0]
            if not dest_flag:
                raise ValueError("Unable to infer 'dest'")
            dest = dest_flag.lstrip(prefix_chars)
            if not dest:
                raise ValueError("Invalid flag: '%r'" % dest_flag)
            dest = "".join([c if str.isalnum(c) else "_" for c in dest])
        else:
            dest = kwargs.pop("dest")

        # extend flags to all prefix chars:
        # flags = [-a, -b], prefix_chars = '-/'
        # result = [-a, /a, -b, /b]
        if len(prefix_chars) > 1:
            _long_flags_single_prefix_char = set(
                [s[1:] for s in long_flags if s[1] not in prefix_chars]
            )
            _long_flags_double_prefix_char = set(
                [s[2:] for s in long_flags if s[1] in prefix_chars]
            )
            _short_flags = set([s[1:] for s in short_flags])
            long_flags = []
            short_flags = []
            for pc in prefix_chars:
                long_flags += [pc + s for s in _long_flags_single_prefix_char]
                long_flags += [pc * 2 + s for s in _long_flags_double_prefix_char]
                short_flags += [pc + s for s in _short_flags]

        flags = long_flags + short_flags + flags
        if enable_suffix_value is False:
            _prefixes = None
        else:
            if not enable_suffix_value:
                _prefixes = [f + "=" for f in long_flags]
            else:
                _prefixes = long_flags
            for f in short_flags:
                # multicharacter flags should not accept suffix values by default
                # i.e. '-longflagvalue' should be invalid
                if len(f) <= 2 or enable_suffix_value:
                    _prefixes.append(f)
            _prefixes += prefixes

        # return the updated keyword arguments
        return dict(kwargs, dest=dest, flags=flags, prefixes=_prefixes)
