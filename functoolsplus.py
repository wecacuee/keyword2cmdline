from functools import partial, reduce


def call(f, *a, **kw):
    return f(*a, **kw)


def compose(fs):
    """
    Composes functions together

    If the input is [f, g, h], the function returns r such that
    r(x) = f(g(h(x)))

    or r = (f · g · h)
    """
    return partial(reduce, lambda acc, f: f(acc), list(reversed(fs)))


def kwcompose(fs):
    """
    Composes keyword functions together

    If the input is [f, g, h], the function returns r such that
    r(**kw) = f(**g(**h(**kw)))

    or r = (f · g · h)
    """
    return partial(reduce, lambda acc, f: f(**acc), list(reversed(fs)))


def argcompose(fs):
    """
    Composes keyword functions together

    If the input is [f, g, h], the function returns r such that
    r(*a) = f(*g(*h(*a)))

    or r = (f · g · h)
    """
    return partial(reduce, lambda acc, f: f(*acc), list(reversed(fs)))


def headtail(xs):
    itxs = iter(xs)
    return next(itxs), itxs


def tail(xs):
    return headtail(xs)[1]


def head(xs):
    return headtail(xs)[0]


first = head

second = compose((head, tail))


def group_by(rows, key_fn, init_fn=list, group_init_fn=dict):
    grouped = group_init_fn()
    for row in rows:
        grouped.setdefault(key_fn(row), init_fn()).append(row)

    return grouped.items()


def clone_partial(func, **kw):
    return (func.copy(**kw)
            if isinstance(func, xargs)
            else partial(func, **kw))


def recpartial(func, keywords, sep="."):
    """
    recpartial(func, {'a.b.c': 10})

    is a short form for

    partial(func, a=partial(b=partial(c=10))

    As expected a and b need to be callables and b must accept c as a keyword
    argument.
    """
    # Separate head keywords from tail keywords.
    # We will apply partial with head keywords.
    # Tail keywords will be passed on recursively, but they need to be grouped
    # first to minimize calls to the recpartial.
    assert iscallable(func)
    head_keywords = dict()
    tail_keywords = OrderedDict()  # respect keywords order
    for reckey, val in keywords.items():
        reckeys = reckey.split(sep)
        if len(reckeys) > 1:
            tail_keywords.setdefault(
                reckeys[0], {})[sep.join(reckeys[1:])] = val
        else:
            head_keywords[reckeys[0]] = val

    for headkey, t_keywords in tail_keywords.items():
        tail_func = head_keywords.get(headkey, default_kw(func)[headkey])
        head_keywords[headkey] = recpartial(tail_func, t_keywords, sep=sep)
    return clone_partial(func, **head_keywords)
