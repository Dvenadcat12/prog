#!/usr/bin/python3

import sys


def is_name_correct(name):
    if len(name) == 0 or not name[0].isupper():
        return False
    return all(char.isalpha() for char in name)


def process_names(input_text):
    name_list = input_text.strip().split()
    for name in name_list:
        if is_name_correct(name):
            print(f'Привет, {name}! Рад видеть тебя!')
        else:
            sys.stderr.write(f'Ошибка: {name} не является корректным именем.\n')


def main():
    if sys.stdin.isatty():
        while True:
            try:
                print('Введите ваше имя:')
                user_input = sys.stdin.readline()
                if user_input.strip() == "":
                    continue
                process_names(user_input)
            except KeyboardInterrupt:
                print('\nВсего доброго!')
                break
    else:
        all_lines = sys.stdin.readlines()
        for line in all_lines:
            process_names(line)


if __name__ == "__main__":
    main()
