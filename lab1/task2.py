#!/usr/bin/python3

import random
import sys


def myLog(message):
    with open('log_div.txt', 'a') as log:
        print(message, file=log)


def main():
    try:
        a = int(sys.stdin.read())
        b = random.randint(-10, 10)
        message = f'A = {a}, B = {b}'
        myLog(message)
        div = a/b
        message = f'A/B = {div}'
        myLog(message)

    except ZeroDivisionError:
        message = 'ZeroDivisionError'
        print(message, file=sys.stderr)
        myLog(message)
    except ValueError:
        message = 'ValueError'
        print(message, file=sys.stderr)
        myLog(message)
    else:
        print(div, file=sys.stdout)


if __name__ == "__main__":
    main()
