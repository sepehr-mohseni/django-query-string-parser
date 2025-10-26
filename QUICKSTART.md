# Quick Start Guide

## Installation

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package in development mode
pip install -e ".[dev]"
```

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_parser.py -v

# Run with coverage
pytest --cov=django_query_parser --cov-report=html
```

## Running the Demo

```bash
# Make sure you're in the project root and virtual environment is activated
PYTHONPATH=src python examples/demo.py
```

## Using in Your Django Project

### Basic Usage

```python
from django_query_parser import DjangoQueryParser
from myapp.models import Article

# Initialize parser with allowed fields
ALLOWED_FIELDS = {'status', 'priority', 'author', 'created_at'}
parser = DjangoQueryParser(allowed_fields=ALLOWED_FIELDS)

# Parse a query string from user input (e.g., from GET parameters)
query_string = request.GET.get('q', '')
q_object = parser.parse(query_string)

# Use in Django queryset
articles = Article.objects.filter(q_object)
```

### Django REST Framework Example

```python
from rest_framework import generics
from django_query_parser import DjangoQueryParser
from .models import Article
from .serializers import ArticleSerializer

class ArticleListView(generics.ListAPIView):
    serializer_class = ArticleSerializer
    
    # Define allowed query fields
    ALLOWED_QUERY_FIELDS = {'status', 'priority', 'author', 'is_published'}
    
    def get_queryset(self):
        queryset = Article.objects.all()
        
        # Get query string from request
        query_string = self.request.query_params.get('q', '')
        
        if query_string:
            try:
                parser = DjangoQueryParser(allowed_fields=self.ALLOWED_QUERY_FIELDS)
                q_object = parser.parse(query_string)
                queryset = queryset.filter(q_object)
            except ValueError as e:
                # Handle invalid query
                # You might want to return a 400 error here
                pass
        
        return queryset
```

### Example API Calls

Once integrated, users can make powerful queries:

```bash
# Simple exact match
GET /api/articles/?q=status:published

# Complex query with AND/OR
GET /api/articles/?q=(status:published OR status:draft) AND priority>=5

# Case-insensitive search
GET /api/articles/?q=author~="john"

# Exclusion
GET /api/articles/?q=status:published AND priority!=1

# Date range (if you have date fields)
GET /api/articles/?q=created_at>="2024-01-01" AND created_at<"2025-01-01"
```

## Query Syntax Reference

### Operators

- `:` or `:=` - Exact match
- `~=` - Contains (case-insensitive)
- `!=` - Not equal
- `>` - Greater than
- `<` - Less than
- `>=` - Greater than or equal
- `<=` - Less than or equal

### Logical Operators

- `AND` or `and` - Both conditions must be true
- `OR` or `or` - At least one condition must be true
- `( )` - Grouping for precedence

### Value Types

- Strings: `"quoted"` or `unquoted`
- Numbers: `42` or `3.14`
- Booleans: `true` or `false`
- Null: `null`

## Development

### Project Structure

```
django-query-string-parser/
├── src/
│   └── django_query_parser/
│       ├── __init__.py
│       └── parser.py          # Main parser implementation
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Pytest configuration
│   └── test_parser.py         # Test suite
├── examples/
│   └── demo.py                # Demonstration script
├── README.md
├── pyproject.toml
├── setup.py
└── requirements.txt
```

### Adding New Features

1. Add tests in `tests/test_parser.py`
2. Implement feature in `src/django_query_parser/parser.py`
3. Run tests: `pytest -v`
4. Update documentation in `README.md`

### Code Style

```bash
# Format code
black src/ tests/ examples/

# Check style
flake8 src/ tests/ examples/

# Type checking
mypy src/
```

## Troubleshooting

### Common Issues

**Issue**: Field name not allowed
```
ValueError: Invalid query string: Querying on field 'fieldname' is not allowed.
```
**Solution**: Add the field to the `allowed_fields` set when initializing the parser.

**Issue**: Invalid syntax error
```
ValueError: Invalid query string: ...
```
**Solution**: Check your query syntax. Common mistakes:
- Unmatched parentheses
- Missing operators between conditions
- Invalid operator usage

**Issue**: Unexpected results with AND/OR
**Solution**: Use parentheses to control precedence. AND binds tighter than OR, so:
- `A OR B AND C` means `A OR (B AND C)`
- To get `(A OR B) AND C`, use parentheses explicitly

## Publishing (for maintainers)

```bash
# Build distribution
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

## Support

- Report issues: [GitHub Issues](https://github.com/sepehr-mohseni/django-query-string-parser/issues)
- Documentation: [README.md](README.md)
- Examples: [examples/demo.py](examples/demo.py)
