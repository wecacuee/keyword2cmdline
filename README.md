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

``` bash
$ python examples/hello_world.py --exclamation_number 10
Hello world!!!!!!!!!!
```

``` bash
$ python examples/hello_world.py --language hi.IN
नमस्ते दुनिया!!
```







