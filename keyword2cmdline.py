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
from abc import ABC, abstractmethod
from kwplus.functools import recpartial


## Copied from _collections_abc.py
def _check_methods(C, *methods):
    mro = C.__mro__
    for method in methods:
        for B in mro:
            if method in B.__dict__:
                if B.__dict__[method] is None:
                    return NotImplemented
                break
        else:
            return NotImplemented
    return True


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


class Parser(ABC):
    @abstractmethod
    def parse_args(self, sys_args):
        """
        Mimics ArgumentParser.parser_args method
        """
        pass

    @classmethod
    def __subclasshook__(cls, C):
        if cls is Parser:
            return _check_methods(C, "parse_args")
        return NotImplemented


Parser.register(argparse.ArgumentParser)

class ArgumentParser(argparse.ArgumentParser):
    def __init__(self, func, infer_parse=default_parser, argparseopts=dict(),
                 kwonly=False,
                 parent_kwargs={}):
        self.func = func
        self.infer_parse = infer_parse
        self.argparseopts = argparseopts
        self.kwonly = kwonly
        kwargs = dict(description=func.__doc__ or "")
        kwargs.update(parent_kwargs)
        super().__init__(**kwargs)
        self.add_all_arguments()

    def argparse_add_argument_map(self):
        return add_argument_args_from_func_sig(
            self.func,
            infer_parse=self.infer_parse,
            kwonly=self.kwonly)

    def add_all_arguments(self):
        for k, kw in self.argparse_add_argument_map().items():
            self.add_argument(**dict(kw, **self.argparseopts.get(k, dict())))

    def add_argument(self, *option_strings, **defaults):
        if not option_strings:
            option_strings = defaults.pop('option_strings')
        super().add_argument(*option_strings, **defaults)


class ExtCommand(ABC):
    """
    Defines a special type that allows keyword2cmdline to recursively get
    commandline arguments from partial keywords.
    """
    @property
    @abstractmethod
    def parser(self):
        """
        Must return a Parser object
        """
        return

    @classmethod
    def __instancecheck__(cls, obj):
        return (hasattr(obj, "parser")
                and hasattr(obj.parser, "argparse_add_argument_map"))

ExtCommand.register(ArgumentParser)


def add_argument_args_from_func_sig(func, infer_parse=default_parser, sep=".",
                                    kwonly=False):
    """
    >>> def main(x, a = 1, b = 2, c = "C"):
    ...     return dict(x = x, a = a, b = b, c = c)
    >>> got_args = add_argument_args_from_func_sig(main)
    >>> expected_args = {'x': {'option_strings': ('x',)}, 'a': {'option_strings': ('--a',), 'type': int, 'default': 1}, 'b': {'option_strings': ('--b',), 'type': int, 'default': 2}, 'c': {'option_strings': ('--c',), 'type': str, 'default': 'C'}}
    >>> got_args == expected_args
    True
    """
    parser_add_argument_args = dict()
    if not kwonly:
        required_args = func_required_args_from_sig(func)
        for k in required_args:
            defaults = argparse_req_defaults(k)
            parser_add_argument_args[k] = defaults

    kwdefaults = func_kwonlydefaults(func)
    for k, deflt in kwdefaults.items():
        if ExtCommand.__instancecheck__(deflt):
            for ext_k, ext_deflt in deflt.parser.argparse_add_argument_map().items():
                new_key = sep.join((k, ext_k))
                ext_deflt['option_strings'] = ["--" + new_key]
                parser_add_argument_args[new_key] = ext_deflt
        else:
            defaults = argparse_opt_defaults(k, deflt, infer_parse)
            parser_add_argument_args[k] = defaults
    return parser_add_argument_args


class ArgParserKWArgs(Parser):
    def __init__(self, parser_fac, func, type_conv=str, **kw):
        self.parser = parser_fac(func)
        self.func = func
        self.type_conv = type_conv
        self.__wrapped__ = self.parser

    def argparse_add_argument_map(self):
        return self.parser.argparse_add_argument_map()

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


def command_config(func,
                   parser_factory = partial(ArgParserKWArgs,
                                            partial(ArgumentParser, kwonly=True))):
    parser = parser_factory(func)
    func.parser = parser
    return func


class command:
    def __init__(self, func,
                 parser_factory = partial(ArgParserKWArgs,
                                          ArgumentParser),
                 sys_args_gen = lambda: sys.argv[1:]):
        """
        >>> @command
        ... def main(x, a = 1, b = 2, c = "C"):
        ...     return dict(x = x, a = a, b = b, c = c)
        >>> gotx = main.set_sys_args(["X"])()
        >>> expectedx = {'x': 'X', 'a': 1, 'b': 2, 'c': 'C'}
        >>> gotx == expectedx
        True
        >>> gotY = main.set_sys_args("Y --a 2 --c D".split())()
        >>> expectedY = {'x': 'Y', 'a': 2, 'b': 2, 'c': 'D'}
        >>> gotY == expectedY
        True

        >>> @command
        ... def main(**kw):
        ...     return kw
        >>> got = main.set_sys_args("--a 2 --b abc".split())()
        >>> expected = {'b': 'abc', 'a': '2'}
        >>> got == expected
        True
        """
        self.func = func
        self.parser_factory = parser_factory
        self.sys_args_gen = sys_args_gen
        self._sys_args = None
        self.parser = parser_factory(func)
        try_autocomplete(self.parser)
        if not isinstance(self.parser, Parser):
            raise ValueError("parser_factory should return "
                             + " keyword2cmdline.Parser object")
        functools.update_wrapper(self, func)

    def set_sys_args(self, sys_args):
        self._sys_args = sys_args
        return self

    def __call__(self, *args, **kw):
        func = self.func
        parser = self.parser
        sys_args_gen = self.sys_args_gen
        _sys_args = self._sys_args
        # parse arguments when the function is actually called
        parsed_args = parser.parse_args(sys_args_gen()
                                        if _sys_args is None
                                        else _sys_args)
        return recpartial(func, vars(parsed_args))(*args, **kw)


def click_like_bool_parse(bool_str):
    if bool_str not in ["", "False"]:
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
    partial(ArgumentParser, infer_parse = click_like_parse))

click_like_parser_factory_kwonly = partial(
    ArgParserKWArgs,
    partial(ArgumentParser, infer_parse = click_like_parse, kwonly=True))


def pcommand(**kw):
    return partial(command, **kw)


click_like_command_config = pcommand(parser_factory = click_like_parser_factory_kwonly)

click_like_command = pcommand(parser_factory = click_like_parser_factory)
"""
>>> @pcommand(parser_factory = click_like_parser_factory)
... def main(x, a = 1, b = 2, c = "C", d = True):
...     return dict(x = x, a = a, b = b, c = c, d = d)
>>> gotx = main.set_sys_args(["X"])()
>>> expectedx = {'x': 'X', 'a': 1, 'b': 2, 'c': 'C', 'd' : True}
>>> gotx == expectedx
True
>>> gotY = main.set_sys_args("Y --a 2 --c D --d False".split())()
>>> expectedY = {'x': 'Y', 'a': 2, 'b': 2, 'c': 'D', 'd' : False}
>>> gotY == expectedY
True

>>> @pcommand(parser_factory = click_like_parser_factory)
... def main(**kw):
...     return kw
>>> got = main.set_sys_args("--a 2 --b abc --d False".split())()
>>> expected = {'b': 'abc', 'a': '2', 'd': 'False'}
>>> got == expected
True
"""
