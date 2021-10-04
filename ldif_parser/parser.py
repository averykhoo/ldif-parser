import base64
from typing import Any
from typing import Generator
from typing import Iterable
from typing import List
from typing import Optional
from typing import TextIO

from ldif_parser.datatypes import Entry
from ldif_parser.datatypes import URL


def lazy_load(file_obj: TextIO,
              *,
              skip_version: bool = True,
              ) -> Generator[Entry, Any, None]:
    """
    yields Entries from an ldif file, skips the version header by default

    :param file_obj: open('sample.ldif', 'r', encoding='ascii')
    :param skip_version: if not skipped, includes the version header as part of the first Entry
    :return: generator of non-empty Entry objects
    """
    _buffer = []

    # helper function to unwrap lines when reading from file
    def read_unfolded_line() -> Optional[str]:
        nonlocal _buffer
        nonlocal file_obj

        while True:
            next_line = file_obj.readline()

            # no next line: end of file
            if not next_line:
                if _buffer:
                    tmp = ''.join(_buffer)
                    _buffer = []
                    return tmp
                else:
                    return None

            # remove trailing newline
            next_line = next_line.rstrip('\r\n')

            # empty buffer
            if not _buffer:
                _buffer.append(next_line)
                continue

            # continuation line
            if next_line.startswith(' '):
                _buffer.append(next_line[1:])
                continue

            # start of next line
            tmp = ''.join(_buffer)
            _buffer = [next_line]
            return tmp

    # read entries
    current_entry = Entry()
    while True:
        line = read_unfolded_line()

        # end of file
        if line is None:
            if current_entry.attributes:
                yield current_entry
            return

        # end of entry
        if not line:
            if current_entry.attributes:
                yield current_entry
                current_entry = Entry()
            continue

        # comment line
        if line.startswith('#'):
            continue

        # parse line
        key, _, value = line.partition(':')
        value = value.lstrip(' ')

        # binary base64
        if value[0] == ':':
            current_entry.append(key, base64.b64decode(value[1:].lstrip(' ')))

        # URL
        elif value[0] == '<':
            current_entry.append(key, URL(value[1:].lstrip(' ')))

        # plaintext
        elif not (skip_version and key.casefold() == 'version' and value.isdigit()):
            current_entry.append(key, value)

        # only skip if first line
        skip_version = False


def load(file_obj: TextIO,
         *,
         skip_version: bool = True,
         ) -> List[Entry]:
    """
    same as lazy_load but returns a list
    """
    return list(lazy_load(file_obj, skip_version=skip_version))


def dump(file_obj: TextIO,
         ldap_entries: Iterable[Entry],
         *,
         version: Optional[int] = 1,
         line_width: Optional[int] = 76,
         ) -> int:
    """
    write Entry instances to a file

    :param file_obj: open('sample.ldif', 'w', encoding='ascii')
    :param ldap_entries: list of Entry instances
    :param version: version number to write, or None to skip writing
    :param line_width: the RFC says 76, but most systems will parse whatever you put in
    :return: number of objects written
    """

    # sanity check the line width
    if line_width is not None:
        if not isinstance(line_width, int):
            raise TypeError(line_width)
        if line_width < 2:
            raise ValueError(line_width)

    # helper function to wrap lines when writing to file
    def write_folded_line(line):
        if line_width is None:
            file_obj.write(f'{line}\n')
        else:
            file_obj.write(f'{line[:line_width]}\n')
            line = line[line_width:]
            while line:
                file_obj.write(f' {line[:line_width - 1]}\n')
                line = line[line_width - 1:]

    # write version
    if version is not None:
        if not isinstance(version, int):
            raise TypeError(version)
        write_folded_line(f'version: {version}')
        write_folded_line('')

    # write all entries
    n_objs_written = 0
    for entry in ldap_entries:
        for attribute_key, attribute_value in entry.attributes:

            # write string
            if isinstance(attribute_value, str):
                write_folded_line(f'{attribute_key}: {attribute_value}')

            # write bytes
            elif isinstance(attribute_value, bytes):
                write_folded_line(f'{attribute_key}:: {base64.b64encode(attribute_value).decode("ascii")}')

            # write URL
            elif isinstance(attribute_value, URL):
                write_folded_line(f'{attribute_key}:< {attribute_value.text}')

            else:
                raise TypeError((attribute_key, attribute_value))

        # write at least one empty line
        write_folded_line('')
        n_objs_written += 1

    # return the number of objects written to the file
    return n_objs_written
