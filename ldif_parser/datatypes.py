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

    >>> URL('https://username:password@hostname:1234/path/to/something;http_params?query=1#fragment')
    URL(text='https://username:password@hostname:1234/path/to/something;http_params?query=1#fragment')
    """

    text: str
    parse_result: Optional[ParseResult] = field(default=None, init=False, repr=False, compare=False)

    def __post_init__(self):
        self.parse_result = urlparse(self.text)

    @property
    def scheme(self):
        """
        >>> URL('https://username:password@hostname:1234/path/to/something;http_params?query=1#fragment').scheme
        'https'
        """
        return self.parse_result.scheme

    @property
    def netloc(self):
        """
        includes username, password, hostname, and port

        >>> URL('https://username:password@hostname:1234/path/to/something;http_params?query=1#fragment').netloc
        'username:password@hostname:1234'
        """
        return self.parse_result.netloc

    @property
    def path(self):
        """
        removes semicolon-delimited params of the last segment of the path for http or https urls
        https://datatracker.ietf.org/doc/html/rfc3986#section-3.3

        >>> URL('https://username:password@hostname:1234/path/to/something;http_params?query=1#fragment').path
        '/path/to/something'

        >>> URL('nothttp://username:password@hostname:1234/path/to/something;http_params?query=1#fragment').path
        '/path/to/something;http_params'
        """
        return self.parse_result.path

    @property
    def params(self):
        """
        semicolon-delimited params of the last segment of the path, only valid for http or https urls
        https://datatracker.ietf.org/doc/html/rfc3986#section-3.3

        >>> URL('https://username:password@hostname:1234/path/to/something;http_params?query=1#fragment').params
        'http_params'

        >>> URL('nothttp://username:password@hostname:1234/path/to/something;http_params?query=1#fragment').params
        ''
        """
        return self.parse_result.params

    @property
    def query(self):
        """
        >>> URL('https://username:password@hostname:1234/path/to/something;http_params?query=1#fragment').query
        'query=1'
        """
        return self.parse_result.query

    @property
    def fragment(self):
        """
        >>> URL('https://username:password@hostname:1234/path/to/something;http_params?query=1#fragment').fragment
        'fragment'
        """
        return self.parse_result.fragment

    @property
    def username(self):
        """
        >>> URL('https://username:password@hostname:1234/path/to/something;http_params?query=1#fragment').username
        'username'
        """
        return self.parse_result.username

    @property
    def password(self):
        """
        >>> URL('https://username:password@hostname:1234/path/to/something;http_params?query=1#fragment').password
        'password'
        """
        return self.parse_result.password

    @property
    def hostname(self):
        """
        >>> URL('https://username:password@hostname:1234/path/to/something;http_params?query=1#fragment').hostname
        'hostname'
        """
        return self.parse_result.hostname

    @property
    def port(self):
        """
        port must be an integer in the range [0, ..., 65535]

        >>> URL('https://username:password@hostname:1234/path/to/something;http_params?query=1#fragment').port
        1234
        """
        return self.parse_result.port

    @property
    def parsed_query(self):
        """
        >>> URL('https://username:password@hostname:1234/path/to/something;http_params?query=1#fragment').parsed_query
        {'query': ['1']}
        """
        return parse_qs(self.query)

    @property
    def parsed_query_list(self):
        """
        >>> URL('https://username:password@hostname:1234/path/to/something;http_params?query=1#fragment').parsed_query_list
        [('query', '1')]
        """
        return parse_qsl(self.query)


@dataclass
class Entry:
    attributes: List[Tuple[str, Union[str, bytes, URL]]] = field(default_factory=list, init=False)

    def append(self,
               key: str,
               value: Union[str, bytes, URL],
               ):
        assert isinstance(key, str) and len(key) > 0
        assert isinstance(value, (str, bytes, URL))
        self.attributes.append((key, value))

    def get_first(self, attribute_name: str) -> Union[str, bytes, URL]:
        raise NotImplementedError

    def get_all(self, attribute_name: str) -> List[Union[str, bytes, URL]]:
        raise NotImplementedError
