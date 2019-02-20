import functools
import inspect
import sys
import argparse
from functools import partial


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


class opts(dict):
    """ Token special class """
    pass


def argparse_opt_defaults(k, opts_or_default):
    default = (opts_or_default.get('default')
               if isinstance(opts_or_default, opts)
               else opts_or_default)
    default_apopts = dict(option_strings = ('--{}'.format(k),),
                          default = default)
    return (dict(default_apopts, **opts_or_default)
            if isinstance(opts_or_default, opts)
            else dict(default_apopts, type=type(default)))


def foreach_argument(parser, defaults):
    option_strings = defaults.pop('option_strings')
    parser.add_argument(*option_strings, **defaults)


def add_argument_args_from_func_sig(func):
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
        defaults = argparse_opt_defaults(k, deflt)
        parser_add_argument_args[k] = defaults
    return parser_add_argument_args


def argparser_from_func_sig(func,
                            argparseopts = dict(),
                            parser_factory = argparse.ArgumentParser,
                            foreach_argument_cb = foreach_argument):
    """
    """
    parser = parser_factory(description=func.__doc__ or "")
    for k, kw in add_argument_args_from_func_sig(func).items():
        foreach_argument_cb(parser, dict(kw, **argparseopts.get(k, dict())))
    return parser


class ArgParserKWArgs:
    def __init__(self, parser_fac, func, type_conv=str, **kw):
        self.parser = parser_fac(func)
        self.func = func
        self.type_conv = type_conv

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

    @functools.wraps(func)
    def wrapper(sys_args = None, *args, **kw):
        # parse arguments when the function is actually called
        parsed_args = parser.parse_args(sys_args_gen()
                                        if sys_args is None
                                        else sys_args)
        return functools.partial(func, **vars(parsed_args))(*args, **kw)

    return wrapper
