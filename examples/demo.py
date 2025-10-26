"""
Demonstration script for Django Query Parser

This script shows various examples of using the query parser.
Run this after installing the package or from the project root with:
    PYTHONPATH=src python examples/demo.py
"""

import os
import sys
import django
from django.conf import settings

# Configure Django settings for standalone script
if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
        ],
    )
    django.setup()

# Now we can import our parser
from django_query_parser import DjangoQueryParser


def main():
    """Run demonstration examples"""
    
    # 1. Define allowed fields for security in a real Django view
    WHITELISTED_FIELDS = {'status', 'priority', 'name', 'is_active', 'price'}
    parser = DjangoQueryParser(allowed_fields=WHITELISTED_FIELDS)

    print("=" * 70)
    print("Django Query Parser Demonstration")
    print("=" * 70)

    # Example 1: Complex logic with grouping and mixed lookups
    print("\n" + "─" * 70)
    print("Example 1: Complex Query with Grouping")
    print("─" * 70)
    query1 = '(status:active OR status:pending) AND priority>=5 AND name~="John Doe"'
    q_object1 = parser.parse(query1)
    print(f"Query: {query1}")
    print(f"\nResulting Q Object:\n{q_object1}")
    print(f"\nSQL-like representation: {q_object1}")
    # Expected output: (OR: ('status__exact', 'active'), ('status__exact', 'pending')) & ('priority__gte', 5) & ('name__icontains', 'John Doe')

    # Example 2: Simple exclusion and boolean check
    print("\n" + "─" * 70)
    print("Example 2: Exclusion and Boolean Values")
    print("─" * 70)
    query2 = 'is_active:true AND price<100.00 AND priority!=1'
    q_object2 = parser.parse(query2)
    print(f"Query: {query2}")
    print(f"\nResulting Q Object:\n{q_object2}")
    # Expected output: ('is_active__exact', True) & ('price__lt', 100.0) & (NOT (Q: ('priority__exact', 1)))

    # Example 3: Security Failure (Attempt to query a non-whitelisted field)
    print("\n" + "─" * 70)
    print("Example 3: Security Check (Disallowed Field)")
    print("─" * 70)
    query3 = 'secret_data:true'
    print(f"Query: {query3}")
    try:
        parser.parse(query3)
        print("⚠️  Security check FAILED - query was allowed!")
    except ValueError as e:
        print(f"✅ Security Check Passed (Query Rejected)")
        print(f"Error: {e}")
        # Expected output: Security Check Passed (Raised): Invalid query string: Querying on field 'secret_data' is not allowed.

    # Example 4: Different operators
    print("\n" + "─" * 70)
    print("Example 4: Various Operators")
    print("─" * 70)
    queries = [
        ('status:=active', 'Exact match with := operator'),
        ('name~="test"', 'Case-insensitive contains'),
        ('price>50.5', 'Greater than (float)'),
        ('priority<=10', 'Less than or equal'),
    ]
    
    for query, description in queries:
        q_obj = parser.parse(query)
        print(f"{description:30} | {query:20} → {q_obj}")

    # Example 5: Parser without field restrictions
    print("\n" + "─" * 70)
    print("Example 5: Unrestricted Parser (Use with caution!)")
    print("─" * 70)
    unrestricted_parser = DjangoQueryParser()  # No field whitelist
    query5 = 'any_field:value AND another_field>100'
    q_object5 = unrestricted_parser.parse(query5)
    print(f"Query: {query5}")
    print(f"Resulting Q Object: {q_object5}")
    print("⚠️  Note: This allows querying any field - use whitelist in production!")

    # Example 6: Edge cases
    print("\n" + "─" * 70)
    print("Example 6: Edge Cases and Special Values")
    print("─" * 70)
    edge_cases = [
        ('status:null', 'Null value'),
        ('is_active:false', 'Boolean false'),
        ('priority:0', 'Zero value'),
        ('name:""', 'Empty string'),
    ]
    
    for query, description in edge_cases:
        try:
            q_obj = parser.parse(query)
            print(f"{description:20} | {query:20} → {q_obj}")
        except ValueError as e:
            print(f"{description:20} | {query:20} → Error: {e}")

    print("\n" + "=" * 70)
    print("Demonstration Complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()
