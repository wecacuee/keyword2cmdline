[![Build Status](https://travis-ci.org/wecacuee/keyword2cmdline.svg?branch=master)](https://travis-ci.org/wecacuee/keyword2cmdline)
# Keywords to command line arguments

Convert your function with keyword arguments into command line arguments with one line of code.

## Installation

``` python
pip install keyword2cmdline
```

## Usage

Use the decorator `command` from the `keyword2cmdline` module to convert the function into command line arguments.

``` python
from keyword2cmdline import command

@command
def main(text="Hello world",
         language='en.US',
         exclamation_number=2,
         exclamation_sign="!",
         exclamation=True):
     ...
     
 
if __name__ == '__main__':
    main()
```

Check the example `examples/hello_world.py`.

``` bash
$ python examples/hello_world.py -h
usage: hello_world.py [-h] [--exclamation_number EXCLAMATION_NUMBER]
                      [--exclamation_sign EXCLAMATION_SIGN]
                      [--exclamation EXCLAMATION] [--text TEXT]
                      [--language LANGUAGE]

optional arguments:
  -h, --help            show this help message and exit
  --exclamation_number EXCLAMATION_NUMBER
  --exclamation_sign EXCLAMATION_SIGN
  --exclamation EXCLAMATION
  --text TEXT
  --language LANGUAGE
```

``` bash
$ python examples/hello_world.py
Hello world!!
```

``` python-console
>>> from examples.hello_world import main
>>> main.set_sys_args([])()
Hello world!!

```

``` bash
$ python examples/hello_world.py --exclamation_number 10
Hello world!!!!!!!!!!
```

```python-console
>>> from examples.hello_world import main
>>> main.set_sys_args("--exclamation_number 10".split())()
Hello world!!!!!!!!!!

```

``` bash
$ python examples/hello_world.py --language hi.IN
नमस्ते दुनिया!!
```

```python-console
>>> from examples.hello_world import main
>>> main.set_sys_args("--language hi.IN".split())()
नमस्ते दुनिया!!

```

For boolean variables, any string is `True` but empty string '' is `False` (you can customize that)
``` bash
$ python examples/hello_world.py --exclamation ''
Hello world
```

``` python-console
>>> from examples.hello_world import main
>>> main.set_sys_args( ["--exclamation", ""])()
Hello world

```

To add help and more customization to the `ArgumentParser.add_argument()` see the example in 
`examples/hello_world_customizations.py`. Basically import a dummy class `opts`
from keyword2cmdline and then pass all the arguments as if `opts` is a `dict`.

``` python
from keyword2cmdline import command, opts

@command
def main(text="Hello world",
         language='en.US',
         exclamation_number=2,
         exclamation_sign="!",
         exclamation=opts(
               default=True,
               type=bool,
               help="""Whether to use exclamation sign or not. Use empty string '' for False""")):
     ...
     
 
if __name__ == '__main__':
    main()

```

Asking for help will print the keyword help.

``` bash
$ python examples/hello_world_customizations.py -h
usage: hello_world_customizations.py [-h]
                                     [--exclamation_sign EXCLAMATION_SIGN]
                                     [--exclamation EXCLAMATION] [--text TEXT]
                                     [--language LANGUAGE]
                                     [--exclamation_number EXCLAMATION_NUMBER]

Prints hello world with desired number of exclamation signs

optional arguments:
  -h, --help            show this help message and exit
  --exclamation_sign EXCLAMATION_SIGN
  --exclamation EXCLAMATION
                        Whether to use exclamation sign or not. Use empty
                        string '' for False.
  --text TEXT
  --language LANGUAGE
  --exclamation_number EXCLAMATION_NUMBER
```

## New feature in v1.0: Support for Variational **kwargs

``` python-console
>>> from keyword2cmdline import command
>>> first = lambda xs: xs[0]
>>> @command
... def main(text="sum", **kw):
...     return dict(kw, text=text)
>>> _ = main.set_sys_args(sys_args = "--text sum --a 1 --b 2 --c 3".split())
>>> list(sorted(main().items(), key=first))
[('a', '1'), ('b', '2'), ('c', '3'), ('text', 'sum')]

```

## New feature in v1.1.0: Support for click like boolean parser

``` python
from keyword2cmdline import click_like_command

@click_like_command
def main(text="Hello world",
         language='en.US',
         exclamation_number=2,
         exclamation_sign="!",
         exclamation=True):
    ...
```

``` bash
$ python examples/hello_world.py --exclamation False
Hello world
```

``` python-console
>>> from examples.hello_world_click import main
>>> main.set_sys_args( ["--exclamation", "False"])()
Hello world

```

## New feature in v1.3.0: Support for argcomplete, lists, dicts and enums

`list` and `dict` are parsed using `json.loads`. `dict` are merged with the
default `dict` argument. `enum.Enum` are converted to strings and the
corresponding string can be converted back to the enum object. A convenience
class `keyword2cmdline.EnumChoice` is provided for using shortnames for `enum`
object which might use long names to support `argcomplete` feature consistently.

``` python-console
>>> from keyword2cmdline import command, EnumChoice
>>> @command
... def main(text="Hello world",
...          language=EnumChoice('Lang', 'en_US hi_IN').en_US,
...          exclamation_props=dict(number=2),
...          exclamation=True):
...     return sorted(locals().items())
...
>>> main.set_sys_args([])()
[('exclamation', True), ('exclamation_props', {'number': 2}), ('language', <Lang.en_US: 1>), ('text', 'Hello world')]
>>> main.set_sys_args(["--exclamation", ""])()
[('exclamation', False), ('exclamation_props', {'number': 2}), ('language', <Lang.en_US: 1>), ('text', 'Hello world')]
>>> main.set_sys_args(["--language", "hi_IN"])()
[('exclamation', True), ('exclamation_props', {'number': 2}), ('language', <Lang.hi_IN: 2>), ('text', 'Hello world')]
>>> main.set_sys_args(["--exclamation_props", '{"number": 3}'])()
[('exclamation', True), ('exclamation_props', {'number': 3}), ('language', <Lang.en_US: 1>), ('text', 'Hello world')]

>>> from keyword2cmdline import click_like_command
>>> @click_like_command
... def main(text="Hello world",
...          language=EnumChoice('Lang', 'en_US hi_IN').en_US,
...          exclamation_props=dict(number=2),
...          exclamation=True):
...     return sorted(locals().items())
...
>>> main.set_sys_args(["--exclamation", "False"])()
[('exclamation', False), ('exclamation_props', {'number': 2}), ('language', <Lang.en_US: 1>), ('text', 'Hello world')]

```
