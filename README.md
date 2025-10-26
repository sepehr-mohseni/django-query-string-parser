# Django Query Parser

[![PyPI version](https://badge.fury.io/py/django-query-string-parser.svg)](https://badge.fury.io/py/django-query-string-parser)
[![Downloads](https://pepy.tech/badge/django-query-string-parser)](https://pepy.tech/project/django-query-string-parser)
[![Python Versions](https://img.shields.io/pypi/pyversions/django-query-string-parser.svg)](https://pypi.org/project/django-query-string-parser/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A flexible query parser that converts query strings into Django Q objects, enabling powerful and secure filtering in your Django applications.

## Features

- 🔍 **Intuitive Query Syntax**: Simple, human-readable query language
- 🔒 **Security Built-in**: Whitelist allowed fields to prevent unauthorized access
- 🎯 **Django Native**: Converts directly to Django Q objects
- 🚀 **Powerful Operators**: Support for comparison, containment, and exclusion
- 🔗 **Logical Combinations**: AND/OR logic with grouping via parentheses
- ⚡ **Fast Parsing**: Uses Lark parser with LALR for efficient parsing

## Installation

```bash
pip install django-query-string-parser
```

Or install from source:

```bash
git clone https://github.com/sepehr-mohseni/django-query-string-parser.git
cd django-query-string-parser
pip install -e .
```

## Quick Start

```python
from django_query_parser import DjangoQueryParser
from myapp.models import Article

# Define allowed fields for security
ALLOWED_FIELDS = {'status', 'priority', 'author', 'published_date'}
parser = DjangoQueryParser(allowed_fields=ALLOWED_FIELDS)

# Parse a query string
query_string = 'status:published AND priority>=5'
q_object = parser.parse(query_string)

# Use it in a Django queryset
articles = Article.objects.filter(q_object)
```

## Query Syntax

### Basic Comparisons

| Operator | Meaning | Example | Django Lookup |
|----------|---------|---------|---------------|
| `:` | Exact match | `status:active` | `status__exact` |
| `:=` | Exact match (alias) | `status:=active` | `status__exact` |
| `~=` | Contains (case-insensitive) | `name~="John"` | `name__icontains` |
| `!=` | Not equal | `priority!=1` | `~Q(priority__exact=1)` |
| `>` | Greater than | `price>100` | `price__gt` |
| `<` | Less than | `price<100` | `price__lt` |
| `>=` | Greater than or equal | `priority>=5` | `priority__gte` |
| `<=` | Less than or equal | `priority<=10` | `priority__lte` |

### Logical Operators

- **AND**: Combine conditions (both must be true)
  ```
  status:active AND priority>=5
  ```

- **OR**: Alternative conditions (at least one must be true)
  ```
  status:active OR status:pending
  ```

- **Grouping**: Use parentheses to control precedence
  ```
  (status:active OR status:pending) AND priority>=5
  ```

### Value Types

- **Strings**: Quoted or unquoted
  ```
  name:"John Doe"
  status:active
  ```

- **Numbers**: Integers or floats
  ```
  priority:5
  price:99.99
  ```

- **Booleans**: `true` or `false`
  ```
  is_active:true
  ```

- **Null**: `null`
  ```
  deleted_at:null
  ```

## Examples

### Example 1: Complex Query with Grouping

```python
parser = DjangoQueryParser(allowed_fields={'status', 'priority', 'author'})

query = '(status:active OR status:pending) AND priority>=5 AND author~="John"'
q_object = parser.parse(query)

# Use in Django ORM
articles = Article.objects.filter(q_object)
```

### Example 2: Exclusion and Boolean

```python
query = 'is_published:true AND priority!=1 AND views>1000'
q_object = parser.parse(query)

articles = Article.objects.filter(q_object)
```

### Example 3: Date Filtering (with custom field)

```python
# Assuming you have a date field
query = 'published_date>="2024-01-01" AND published_date<"2025-01-01"'
q_object = parser.parse(query)

articles = Article.objects.filter(q_object)
```

## Security

The parser includes built-in security features:

```python
# Whitelist allowed fields
SAFE_FIELDS = {'status', 'priority', 'author'}
parser = DjangoQueryParser(allowed_fields=SAFE_FIELDS)

# This will raise ValueError
try:
    parser.parse('secret_data:true')
except ValueError as e:
    print(e)  # "Querying on field 'secret_data' is not allowed."
```

## API Reference

### `DjangoQueryParser`

#### `__init__(allowed_fields=None)`

- **allowed_fields** (optional): Set of field names that are allowed to be queried. If `None`, all fields are allowed (not recommended for production).

#### `parse(query_string: str) -> Q`

- **query_string**: The query string to parse
- **Returns**: A Django `Q` object that can be used in `.filter()` or `.exclude()`
- **Raises**: `ValueError` if the query is invalid or uses disallowed fields

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/sepehr-mohseni/django-query-string-parser.git
cd django-query-string-parser

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/ tests/
```

### Type Checking

```bash
mypy src/
```

## Use Cases

- **API Filtering**: Enable powerful filtering in REST APIs
- **Search Interfaces**: Build advanced search features
- **Admin Panels**: Add flexible filtering to admin interfaces
- **Data Export**: Allow users to define complex export criteria

## Limitations

- Field names must be valid Python identifiers (alphanumeric and underscores)
- No support for related field lookups (e.g., `author__name`) yet (coming soon)
- Date/time values should be in ISO format strings

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### 0.1.0 (2025-10-26)
- Initial release
- Basic query parsing with logical operators
- Security whitelist for fields
- Support for common comparison operators
