from collections import OrderedDict
from functools import partial
from operator import getitem
import argparse
import enum
import functools
import inspect
import json
import os
import sys


def unwrapped(func):
    if isinstance(func, partial):
        return unwrapped(func.func)
    elif hasattr(func, "__wrapped__"):
        return unwrapped(func.__wrapped__)
    else:
        return func


def try_get_argcomplete():
    try:
        import argcomplete
        return argcomplete
    except ImportError:
        if os.environ.get("_ARC_DEBUG"):
            print("_ARC_DEBUG: argcomplete not installed")
        return None


def try_autocomplete(argparser):
    argparser = unwrapped(argparser)
    if not isinstance(argparser, argparse.ArgumentParser):
        if os.environ.get("_ARC_DEBUG"):
            print("_ARC_DEBUG: parser is not ArgumentParser")
        return

    argcomplete = try_get_argcomplete()
    if argcomplete:
        assert isinstance(argparser, argparse.ArgumentParser)
        argcomplete.autocomplete(argparser)
        if os.environ.get("_ARC_DEBUG"):
            print("_ARC_DEBUG: argcomplete enabled")
        return True

    return


def func_required_args_from_sig(func):
    return [k
            for k, p in inspect.signature(func).parameters.items()
            if p.default is inspect._empty and
            (p.kind is inspect.Parameter.POSITIONAL_ONLY or
             p.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD)]


def func_kwonlydefaults_from_sig(func):
    return {k: p.default
            for k, p in inspect.signature(func).parameters.items()
            if p.default is not inspect._empty and
            p.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD}


def kw_attributify(func):
    for k, default in func_kwonlydefaults_from_sig(func).items():
        if not hasattr(func, k):
            setattr(func, k, default)
    return func


def func_kwonlydefaults(func):
    if isinstance(func, functools.partial):
        if func.args:
            reqargs = func_kwonlydefaults_from_sig(func.func)
            kw = zip(reqargs, func.args)
        else:
            kw = dict()
        kw.update(func_kwonlydefaults(func.func))
        kw.update(func.keywords)
    else:
        kw = func_kwonlydefaults_from_sig(func)
    return kw


def argparse_req_defaults(k):
    return dict(option_strings = ("{}".format(k),))


class EnumChoice(enum.Enum):
    def __str__(self):
        return self.name


def enum_parser(default):
    assert isinstance(default, enum.Enum)
    enumclass = type(default)
    if try_get_argcomplete():
        # autocomplete does not uses metavar instead uses str(choices)
        str2val = {str(v): v for v in enumclass}
    else:
        str2val = {v.name: v for v in enumclass}

    return dict(type=partial(getitem, str2val),
                choices=list(enumclass),
                metavar=str2val.keys())


def dict_parser(default):
    assert isinstance(default, dict)
    return dict(type=lambda s: dict(default, **json.loads(s)))


def list_parser(default):
    assert isinstance(default, (list, tuple))
    return dict(type=json.loads)


@kw_attributify
def default_parser(default,
                   fallback_parser=lambda x: dict(type=type(x)),
                   type2parser=OrderedDict([
                       (enum.Enum, enum_parser),
                       (dict, dict_parser),
                       (list, list_parser),
                       (tuple, list_parser)])):
    for t, parser in type2parser.items():
        if isinstance(default, t):
            return parser(default)
    return fallback_parser(default)


class opts(dict):
    """ Token special class """
    pass


def argparse_opt_defaults(k, opts_or_default, infer_parse):
    default = (opts_or_default.get('default')
               if isinstance(opts_or_default, opts)
               else opts_or_default)
    default_apopts = dict(option_strings = ('--{}'.format(k),),
                          default = default)
    return (dict(default_apopts, **opts_or_default)
            if isinstance(opts_or_default, opts)
            else dict(default_apopts, **infer_parse(default)))


def foreach_argument(parser, defaults):
    option_strings = defaults.pop('option_strings')
    parser.add_argument(*option_strings, **defaults)


def add_argument_args_from_func_sig(func, infer_parse=default_parser):
    """
    >>> def main(x, a = 1, b = 2, c = "C"):
    ...     return dict(x = x, a = a, b = b, c = c)
    >>> got_args = add_argument_args_from_func_sig(main)
    >>> expected_args = {'x': {'option_strings': ('x',)}, 'a': {'option_strings': ('--a',), 'type': int, 'default': 1}, 'b': {'option_strings': ('--b',), 'type': int, 'default': 2}, 'c': {'option_strings': ('--c',), 'type': str, 'default': 'C'}}
    >>> got_args == expected_args
    True
    """
    parser_add_argument_args = dict()
    required_args = func_required_args_from_sig(func)
    for k in required_args:
        defaults = argparse_req_defaults(k)
        parser_add_argument_args[k] = defaults

    kwdefaults = func_kwonlydefaults(func)
    for k, deflt in kwdefaults.items():
        defaults = argparse_opt_defaults(k, deflt, infer_parse)
        parser_add_argument_args[k] = defaults
    return parser_add_argument_args


def argparser_from_func_sig(func,
                            argparseopts = dict(),
                            parser_factory = argparse.ArgumentParser,
                            foreach_argument_cb = foreach_argument,
                            infer_parse = default_parser):
    """
    """
    parser = parser_factory(description=func.__doc__ or "")
    for k, kw in add_argument_args_from_func_sig(func, infer_parse=infer_parse).items():
        foreach_argument_cb(parser, dict(kw, **argparseopts.get(k, dict())))
    return parser


class ArgParserKWArgs:
    def __init__(self, parser_fac, func, type_conv=str, **kw):
        self.parser = parser_fac(func)
        self.func = func
        self.type_conv = type_conv
        self.__wrapped__ = self.parser

    def _accepts_var_kw(self, func):
        return any(p.kind == inspect.Parameter.VAR_KEYWORD
                   for k, p in inspect.signature(func).parameters.items())

    def parse_args(self, sys_args):
        if self._accepts_var_kw(self.func):
            args, unknown = self.parser.parse_known_args(sys_args)
            for a in unknown:
                if a.startswith("--"):
                    self.parser.add_argument(a, type=self.type_conv)

        return self.parser.parse_args(sys_args)


def command(func,
            parser_factory = partial(ArgParserKWArgs,
                                     argparser_from_func_sig),
            sys_args_gen = lambda: sys.argv[1:]):
    """
    >>> @command
    ... def main(x, a = 1, b = 2, c = "C"):
    ...     return dict(x = x, a = a, b = b, c = c)
    >>> gotx = main(sys_args = ["X"])
    >>> expectedx = {'x': 'X', 'a': 1, 'b': 2, 'c': 'C'}
    >>> gotx == expectedx
    True
    >>> gotY = main(sys_args = "Y --a 2 --c D".split())
    >>> expectedY = {'x': 'Y', 'a': 2, 'b': 2, 'c': 'D'}
    >>> gotY == expectedY
    True

    >>> @command
    ... def main(**kw):
    ...     return kw
    >>> got = main(sys_args = "--a 2 --b abc".split())
    >>> expected = {'b': 'abc', 'a': '2'}
    >>> got == expected
    True
    """
    parser = parser_factory(func)
    try_autocomplete(parser)

    @functools.wraps(func)
    def wrapper(sys_args = None, *args, **kw):
        # parse arguments when the function is actually called
        parsed_args = parser.parse_args(sys_args_gen()
                                        if sys_args is None
                                        else sys_args)
        return functools.partial(func, **vars(parsed_args))(*args, **kw)

    return wrapper


def click_like_bool_parse(bool_str):
    if bool_str not in ["True", "False"]:
        raise ValueError("Expected either 'True' or 'False' got %s" % bool_str)
    return (True if bool_str == "True" else False)

def click_like_bool_parser(bool_default):
    assert isinstance(bool_default, bool)
    return dict(type=click_like_bool_parse,
                choices=(True, False))


def merge(d1, d2):
    dc = d1.copy()
    dc.update(d2)
    return dc


click_like_parse = partial(default_parser,
                           type2parser=merge(default_parser.type2parser,
                                             { bool: click_like_bool_parser }))


click_like_parser_factory = partial(
    ArgParserKWArgs,
    partial(argparser_from_func_sig, infer_parse = click_like_parse))


def pcommand(**kw):
    return partial(command, **kw)


click_like_command = pcommand(parser_factory = click_like_parser_factory)
"""
>>> @pcommand(parser_factory = click_like_parser_factory)
... def main(x, a = 1, b = 2, c = "C", d = True):
...     return dict(x = x, a = a, b = b, c = c, d = d)
>>> gotx = main(sys_args = ["X"])
>>> expectedx = {'x': 'X', 'a': 1, 'b': 2, 'c': 'C', 'd' : True}
>>> gotx == expectedx
True
>>> gotY = main(sys_args = "Y --a 2 --c D --d False".split())
>>> expectedY = {'x': 'Y', 'a': 2, 'b': 2, 'c': 'D', 'd' : False}
>>> gotY == expectedY
True

>>> @pcommand(parser_factory = click_like_parser_factory)
... def main(**kw):
...     return kw
>>> got = main(sys_args = "--a 2 --b abc --d False".split())
>>> expected = {'b': 'abc', 'a': '2', 'd': 'False'}
>>> got == expected
True
"""
