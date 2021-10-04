# LDIF parser in pure python

## Usage

```python
from pprint import pprint
import ldif_parser

# read entries one by one
with open('sample.ldif') as f:
    for entry in ldif_parser.lazy_load(f):
        print(entry)
        pprint(entry.attributes)

# read all entries into memory
with open('sample.ldif') as f:
    entries = ldif_parser.load(f)
    print(len(entries))
```