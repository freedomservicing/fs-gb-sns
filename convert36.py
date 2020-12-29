## Copyright (c) 2020 Freedom Servicing, LLC
## Distributed under the MIT software license, see the accompanying
## file LICENSE.md or http://www.opensource.org/licenses/mit-license.php.

import argparse

class b36:

    __decimal_value = None

    __characters = ['0','1','2','3','4','5','6','7','8','9',
    'a','b','c','d','e','f','g','h','i','j','k','l','m','n',
    'o','p','q','r','s','t','u','v','w','x','y','z']

    def __init__(self, value):
        self.__decimal__value = self.__convert(value)

    def __convert(self, value):

        indexed_value = list(value)

        dec_val = 0

        for index in range(len(indexed_value) - 1, -1, -1):
            dec_val += self.__characters.index(indexed_value[index]) * (36 ** (len(indexed_value) - index - 1))

        return dec_val

    def get_decimal_value(self):
        return self.__decimal__value

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--value", dest="value", nargs=1)

    args = parser.parse_args()

    usr_val = b36(args.value[0])

    print(usr_val.get_decimal_value())

if __name__ == "__main__":
    main()
