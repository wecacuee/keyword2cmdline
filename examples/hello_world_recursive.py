#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

from keyword2cmdline import command, command_config

TRANSLATIONS = {
    ("Hello world", "hi.IN"): "नमस्ते दुनिया"}


@command_config
def exclamation(number=2,
                sign="!",
                use=True):
    return (exclamation_sign * exclamation_number
            if use else "")


@command
def main(text="Hello world",
         language='en.US',
         exclamation=exclamation):
    print_text = TRANSLATIONS.get((text, language), text)
    print_text = (print_text +  exclamation())
    print(print_text)

if __name__ == '__main__':
    main()
