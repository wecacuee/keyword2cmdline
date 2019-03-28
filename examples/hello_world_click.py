#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

from keyword2cmdline import click_like_command, EnumChoice

Lang = EnumChoice('Lang', 'en_US hi_IN')
TRANSLATIONS = {
    ("Hello world", Lang.hi_IN): "नमस्ते दुनिया"}


@click_like_command
def main(text="Hello world",
         language=Lang.en_US,
         exclamation_number=2,
         exclamation_sign="!",
         exclamation=True):
    print_text = TRANSLATIONS.get((text, language), text)
    print_text = (print_text + exclamation_sign * exclamation_number
                  if exclamation else print_text)
    print(print_text)

if __name__ == '__main__':
    main()
