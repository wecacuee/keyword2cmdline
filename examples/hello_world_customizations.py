#!/usr/bin/env python3.5

from keyword2cmdline import command, opts

TRANSLATIONS = {
    ("Hello world", "hi.IN"): "नमस्ते दुनिया"}


@command
def main(text="Hello world",
         language='en.US',
         exclamation_number=2,
         exclamation_sign="!",
         # Pass arbitrary keyword arguments to the
         # argparse.ArgumentParser.add_argument()
         exclamation=opts(
             default=True,
             type=bool,
             help="""Whether to use exclamation sign or not. Use empty string '' for False.""")):
    """
    Prints hello world with desired number of exclamation signs
    """
    print_text = TRANSLATIONS.get((text, language), text)
    print_text = (print_text + exclamation_sign * exclamation_number
                  if exclamation else print_text)
    print(print_text)

if __name__ == '__main__':
    main()
