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
>>> main(sys_args = [])
Hello world!!
```

``` bash
$ python examples/hello_world.py --exclamation_number 10
Hello world!!!!!!!!!!
```

```python-console
>>> from examples.hello_world import main
>>> main(sys_args = "--exclamation_number 10")
Hello world!!!!!!!!!!
```

``` bash
$ python examples/hello_world.py --language hi.IN
नमस्ते दुनिया!!
```

```python-console
>>> from examples.hello_world import main
>>> main(sys_args = "--language hi.IN".split())
नमस्ते दुनिया!!
```

For boolean variables, any string is `True` but empty string '' is `False`
``` bash
$ python examples/hello_world.py --exclamation ''
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






