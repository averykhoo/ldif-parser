from pprint import pprint

import ldif_parser


def main():
    with open('sample.ldif') as f:
        ldif = ldif_parser.load(f)
        for entry in ldif:
            print(entry)
            pprint(entry.attributes)


if __name__ == '__main__':
    main()
