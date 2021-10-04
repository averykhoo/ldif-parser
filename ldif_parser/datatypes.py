import base64
import warnings
from dataclasses import dataclass
from dataclasses import field
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union
from urllib.parse import ParseResult
from urllib.parse import parse_qs
from urllib.parse import parse_qsl
from urllib.parse import urlparse


@dataclass(order=True)
class URL:
    """
    convenience wrapper for URL handling, with examples in the docstrings

    >>> URL('')
    URL(text='')

    >>> URL('https://user:pass@hostname:1234/path/to/something;http_params?query=1#fragment')
    URL(text='https://user:pass@hostname:1234/path/to/something;http_params?query=1#fragment')
    """

    text: str
    parse_result: Optional[ParseResult] = field(default=None, init=False, repr=False, compare=False)

    def __post_init__(self):
        self.parse_result = urlparse(self.text)

    @property
    def scheme(self):
        """
        >>> URL('https://user:pass@hostname:1234/path/to/something;http_params?query=1#fragment').scheme
        'https'
        """
        return self.parse_result.scheme

    @property
    def netloc(self):
        """
        includes username, password, hostname, and port

        >>> URL('https://user:pass@hostname:1234/path/to/something;http_params?query=1#fragment').netloc
        'user:pass@hostname:1234'
        """
        return self.parse_result.netloc

    @property
    def path(self):
        """
        removes semicolon-delimited params of the last segment of the path for http or https urls
        https://datatracker.ietf.org/doc/html/rfc3986#section-3.3

        >>> URL('https://user:pass@hostname:1234/path/to/something;http_params?query=1#fragment').path
        '/path/to/something'

        >>> URL('nothttp://user:pass@hostname:1234/path/to/something;http_params?query=1#fragment').path
        '/path/to/something;http_params'
        """
        return self.parse_result.path

    @property
    def params(self):
        """
        semicolon-delimited params of the last segment of the path, only valid for http or https urls
        https://datatracker.ietf.org/doc/html/rfc3986#section-3.3

        >>> URL('https://user:pass@hostname:1234/path/to/something;http_params?query=1#fragment').params
        'http_params'

        >>> URL('nothttp://user:pass@hostname:1234/path/to/something;http_params?query=1#fragment').params
        ''
        """
        return self.parse_result.params

    @property
    def query(self):
        """
        >>> URL('https://user:pass@hostname:1234/path/to/something;http_params?query=1#fragment').query
        'query=1'
        """
        return self.parse_result.query

    @property
    def fragment(self):
        """
        >>> URL('https://user:pass@hostname:1234/path/to/something;http_params?query=1#fragment').fragment
        'fragment'
        """
        return self.parse_result.fragment

    @property
    def username(self):
        """
        >>> URL('https://user:pass@hostname:1234/path/to/something;http_params?query=1#fragment').username
        'user'
        """
        return self.parse_result.username

    @property
    def password(self):
        """
        >>> URL('https://user:pass@hostname:1234/path/to/something;http_params?query=1#fragment').password
        'pass'
        """
        return self.parse_result.password

    @property
    def hostname(self):
        """
        >>> URL('https://user:pass@hostname:1234/path/to/something;http_params?query=1#fragment').hostname
        'hostname'
        """
        return self.parse_result.hostname

    @property
    def port(self):
        """
        port must be an integer in the range [0, ..., 65535]

        >>> URL('https://user:pass@hostname:1234/path/to/something;http_params?query=1#fragment').port
        1234
        """
        return self.parse_result.port

    @property
    def parsed_query(self):
        """
        >>> URL('https://user:pass@hostname:1234/path/to/something;http_params?query=1#fragment').parsed_query
        {'query': ['1']}
        """
        return parse_qs(self.query)

    @property
    def parsed_query_list(self):
        """
        >>> URL('https://user:pass@hostname:1234/path/to/something;http_params?query=1#fragment').parsed_query_list
        [('query', '1')]
        """
        return parse_qsl(self.query)


@dataclass
class Attribute:
    key: str
    options: Optional[str]
    value: Union[str, bytes, URL]

    @classmethod
    def parse_attribute_string(cls,
                               attr_val_spec: str,
                               ) -> 'Attribute':
        if not isinstance(attr_val_spec, str):
            raise TypeError(attr_val_spec)
        if ':' not in attr_val_spec:
            raise ValueError(attr_val_spec)

        # parse line
        description, _, value = attr_val_spec.partition(':')
        key, _, options = description.partition(';')
        value = value.lstrip(' ')

        # parse binary base64
        if value[0] == ':':
            value = base64.b64decode(value[1:].lstrip(' '))

        # parse URL
        elif value[0] == '<':
            value = URL(value[1:].lstrip(' '))

        return Attribute(key=key,
                         options=options,
                         value=value,
                         )

    @property
    def options_list(self) -> List[str]:
        if not self.options:
            return []
        return self.options.split(';')

    @property
    def text(self) -> str:
        if isinstance(self.value, bytes):
            return base64.b64decode(self.value).decode('utf8')
        elif isinstance(self.value, URL):
            return self.value.text
        else:
            assert isinstance(self.value, str)
            return self.value

    def unparse(self) -> str:
        # attribute description
        if self.options is not None:
            description = f'{self.key};{";".join(self.options)}'
        else:
            description = self.key

        # value is bytes
        if isinstance(self.value, bytes):
            return f'{description}:: {base64.b64encode(self.value)}'

        # value is URL
        if isinstance(self.value, URL):
            return f'{description}:< {self.value.text}'

        # first char not safe for a string type
        if ord(self.value[0]) > 127 or self.value[0] in '\0\r\n :<':
            warnings.warn('base64-encoding unsafe string')
            return f'{description}:: {base64.b64encode(self.value.encode("utf8"))}'

        # at least one character is not safe for a string type
        if any(ord(char) > 127 or char in '\0\r\n' for char in self.value[1:]):
            warnings.warn('base64-encoding unsafe string')
            return f'{description}:: {base64.b64encode(self.value.encode("utf8"))}'

        # safe string
        return f'{description}: {self.value}'


@dataclass(frozen=True)
class Entry:
    attributes: List[Tuple[str, Union[str, bytes, URL]]] = field(default_factory=list)

    def __post_init__(self):
        # force re-init to check all keys and values
        _attrs = self.attributes[:]
        self.attributes.clear()
        for key, value in _attrs:
            self.append(key, value)

    def __bool__(self) -> bool:
        return len(self.attributes) > 0

    @property
    def distinguished_name(self) -> str:
        dn = self.get_first('dn')

        if isinstance(dn, str):
            return dn
        elif isinstance(dn, bytes):
            return dn.decode('utf8')  # distinguished names are always strings

    @property
    def controls(self):
        return self.get_all('control')

    @property
    def change_type(self):
        try:
            _change_type = self.get_first('changetype')
        except IndexError:
            return 'add'  # default to add

        if isinstance(_change_type, str):
            return _change_type
        elif isinstance(_change_type, bytes):
            return _change_type.decode('utf8')  # distinguished names are always strings

    def append(self,
               key: str,
               value: Union[str, bytes, URL],
               ) -> None:
        """
        append an attribute as a key-value pair
        """
        assert isinstance(key, str) and len(key) > 0
        assert isinstance(value, (str, bytes, URL))
        if not self.attributes and key.casefold() != 'dn':
            warnings.warn(f'first key expected to be "dn", got "{key}"')
        self.attributes.append((key, value))

    def get_first(self,
                  attribute_name: str,
                  case: bool = True,
                  ) -> Union[str, bytes, URL]:
        """
        get the first matching attribute value
        if missing, raises an IndexError

        :param attribute_name: thing you want to find
        :param case: case-sensitive
        :return: first matching attribute value
        """
        for key, value in self.attributes:
            if case and key == attribute_name:
                return value
            elif key.casefold() == attribute_name.casefold():
                return value
        raise IndexError(attribute_name)

    def get_all(self,
                attribute_name: str,
                case: bool = True,
                ) -> List[Union[str, bytes, URL]]:
        """
        get all matching attribute values as a list
        if missing, returns an empty list

        :param attribute_name: thing you want to find
        :param case: case-sensitive
        :return: list of all matching values, otherwise an empty list
        """
        out = []
        for key, value in self.attributes:
            if case and key == attribute_name:
                out.append(value)
            elif key.casefold() == attribute_name.casefold():
                out.append(value)
        return out
