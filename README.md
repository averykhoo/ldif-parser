# LDIF parser in pure python

## Usage

### Reading

```python
from pprint import pprint
import ldif_parser

# read entries one by one
with open(f'sample.ldif') as f:
    for entry in ldif_parser.lazy_load(f):
        print(entry)
        pprint(entry.attributes)

# read all entries into memory
with open(f'sample.ldif') as f:
    entries = ldif_parser.load(f)
    print(len(entries))
```

### Writing

```python
from pprint import pprint
import ldif_parser

# create entries
entries = [
    ldif_parser.Entry([(f'dn', f'CN=qwer,O=org,C=xyz'), (f'key', f'value')]),
    ldif_parser.Entry([(f'dn', f'CN=asdf,O=org,C=xyz'), (f'another key', b'another value')]),
]

# write all entries
with open(f'new.ldif', f'w') as f:
    ldif_parser.dump(f, entries)
```

# TODO

* support LDIF `modify` Change Records