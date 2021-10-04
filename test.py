from pprint import pprint

import ldif_parser


def main():
    with open('sample.ldif') as f:
        entries = ldif_parser.load(f)
        for entry in entries:
            print(entry)
            pprint(entry.attributes)

    with open('formatted.ldif', 'w') as f:
        ldif_parser.dump(f, entries, line_width=20)

    with open('formatted.ldif') as f:
        assert entries == ldif_parser.load(f)



if __name__ == '__main__':
    main()
