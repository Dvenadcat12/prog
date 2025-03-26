#!/usr/bin/python3

import random
import sys


def main():
    a = random.randint(-10, 10)
    message = f'A = {a}'
    with open('log_rnd.txt', 'a') as log:
        print(message, file=log)
    print(a, file=sys.stdout)


if __name__ == "__main__":
    main()
