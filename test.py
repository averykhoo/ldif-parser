from io import StringIO
from pprint import pprint
from typing import List

import ldif_parser
from ldif_parser import Entry


def check_write_read(entries: List[Entry], version=1, line_width=76):
    entries = list(entries)
    assert all(isinstance(e, Entry) for e in entries)
    s = StringIO()
    ldif_parser.dump(s, entries, version=version, line_width=line_width)
    s.seek(0)
    assert entries == ldif_parser.load(s), entries


def main():
    with open('sample.ldif') as f:
        entries = ldif_parser.load(f)
        for entry in entries:
            print(entry)
            pprint(entry.attributes)

    check_write_read(entries)
    check_write_read(entries, version=None)
    check_write_read(entries, version=0)
    check_write_read(entries, version=999999999999)
    check_write_read(entries, line_width=None)
    check_write_read(entries, line_width=2)
    check_write_read(entries, line_width=20)
    check_write_read(entries, line_width=200)


if __name__ == '__main__':
    main()
