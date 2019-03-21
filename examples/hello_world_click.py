#!/usr/bin/env python3.5

from keyword2cmdline import click_like_command

TRANSLATIONS = {
    ("Hello world", "hi.IN"): "नमस्ते दुनिया"}


@click_like_command
def main(text="Hello world",
         language='en.US',
         exclamation_number=2,
         exclamation_sign="!",
         exclamation=True):
    print_text = TRANSLATIONS.get((text, language), text)
    print_text = (print_text + exclamation_sign * exclamation_number
                  if exclamation else print_text)
    print(print_text)

if __name__ == '__main__':
    main()
