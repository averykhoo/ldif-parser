import base64
from typing import Iterable
from typing import Optional
from typing import TextIO

from ldif_parser.datatypes import Entry
from ldif_parser.datatypes import URL


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
    :param version: version number to write (must be a positive integer), or None to skip writing
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
        if version < 0:
            raise ValueError(version)
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
