#!/usr/bin/python3

import sys
import math


def myLog(message):
    with open('log_sqr.txt', 'a') as log:
        print(message, file=log)


def main():
    try:
        c = float(sys.stdin.read())
        message = f'C = {c}'
        myLog(message)
        sqr = math.sqrt(c)
        message = f'C^(1/2) = {sqr}'
        myLog(message)

    except ValueError:
        message = 'ValueError'
        print(message, file=sys.stderr)
        myLog(message)
    else:
        print(sqr, file=sys.stdout)


if __name__ == "__main__":
    main()
