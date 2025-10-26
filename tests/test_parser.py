"""Tests for the Django Query Parser"""

import pytest
from django.db.models import Q
from django_query_parser import DjangoQueryParser


class TestBasicParsing:
    """Test basic query parsing functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.parser = DjangoQueryParser()

    def test_simple_exact_match(self):
        """Test simple exact match query"""
        q = self.parser.parse('status:active')
        assert q == Q(status__exact='active')

    def test_exact_match_with_equals_operator(self):
        """Test exact match with := operator"""
        q = self.parser.parse('status:=active')
        assert q == Q(status__exact='active')

    def test_greater_than(self):
        """Test greater than operator"""
        q = self.parser.parse('priority>5')
        assert q == Q(priority__gt=5)

    def test_greater_than_or_equal(self):
        """Test greater than or equal operator"""
        q = self.parser.parse('priority>=5')
        assert q == Q(priority__gte=5)

    def test_less_than(self):
        """Test less than operator"""
        q = self.parser.parse('priority<10')
        assert q == Q(priority__lt=10)

    def test_less_than_or_equal(self):
        """Test less than or equal operator"""
        q = self.parser.parse('priority<=10')
        assert q == Q(priority__lte=10)

    def test_contains_operator(self):
        """Test case-insensitive contains operator"""
        q = self.parser.parse('name~="John"')
        assert q == Q(name__icontains='John')

    def test_not_equal_operator(self):
        """Test not equal operator"""
        q = self.parser.parse('status!=active')
        assert q == ~Q(status__exact='active')

    def test_empty_query_string(self):
        """Test that empty string returns empty Q object"""
        q = self.parser.parse('')
        assert q == Q()


class TestValueTypes:
    """Test parsing different value types"""

    def setup_method(self):
        """Set up test fixtures"""
        self.parser = DjangoQueryParser()

    def test_integer_value(self):
        """Test parsing integer values"""
        q = self.parser.parse('priority:5')
        assert q == Q(priority__exact=5)

    def test_float_value(self):
        """Test parsing float values"""
        q = self.parser.parse('price:99.99')
        assert q == Q(price__exact=99.99)

    def test_boolean_true(self):
        """Test parsing boolean true"""
        q = self.parser.parse('is_active:true')
        assert q == Q(is_active__exact=True)

    def test_boolean_false(self):
        """Test parsing boolean false"""
        q = self.parser.parse('is_active:false')
        assert q == Q(is_active__exact=False)

    def test_null_value(self):
        """Test parsing null value"""
        q = self.parser.parse('deleted_at:null')
        assert q == Q(deleted_at__exact=None)

    def test_quoted_string(self):
        """Test parsing quoted strings"""
        q = self.parser.parse('name:"John Doe"')
        assert q == Q(name__exact='John Doe')

    def test_unquoted_string(self):
        """Test parsing unquoted strings"""
        q = self.parser.parse('status:active')
        assert q == Q(status__exact='active')


class TestLogicalOperators:
    """Test logical AND/OR combinations"""

    def setup_method(self):
        """Set up test fixtures"""
        self.parser = DjangoQueryParser()

    def test_simple_and(self):
        """Test simple AND combination"""
        q = self.parser.parse('status:active AND priority:5')
        expected = Q(status__exact='active') & Q(priority__exact=5)
        assert q == expected

    def test_simple_or(self):
        """Test simple OR combination"""
        q = self.parser.parse('status:active OR status:pending')
        expected = Q(status__exact='active') | Q(status__exact='pending')
        assert q == expected

    def test_and_with_lowercase(self):
        """Test AND with lowercase"""
        q = self.parser.parse('status:active and priority:5')
        expected = Q(status__exact='active') & Q(priority__exact=5)
        assert q == expected

    def test_or_with_lowercase(self):
        """Test OR with lowercase"""
        q = self.parser.parse('status:active or status:pending')
        expected = Q(status__exact='active') | Q(status__exact='pending')
        assert q == expected

    def test_mixed_and_or(self):
        """Test mixed AND/OR with proper precedence"""
        q = self.parser.parse('status:active AND priority:5 OR priority:10')
        # AND binds tighter than OR
        expected = ((Q(status__exact='active') & Q(priority__exact=5)) | 
                   Q(priority__exact=10))
        assert q == expected

    def test_parentheses_grouping(self):
        """Test grouping with parentheses"""
        q = self.parser.parse('(status:active OR status:pending) AND priority:5')
        expected = (Q(status__exact='active') | Q(status__exact='pending')) & Q(priority__exact=5)
        assert q == expected

    def test_nested_parentheses(self):
        """Test nested parentheses"""
        q = self.parser.parse('((status:active OR status:pending) AND priority>5) OR name~="test"')
        expected = ((Q(status__exact='active') | Q(status__exact='pending')) & 
                   Q(priority__gt=5)) | Q(name__icontains='test')
        assert q == expected


class TestSecurity:
    """Test security features with field whitelisting"""

    def test_allowed_field(self):
        """Test that allowed fields work"""
        parser = DjangoQueryParser(allowed_fields={'status', 'priority'})
        q = parser.parse('status:active')
        assert q == Q(status__exact='active')

    def test_disallowed_field(self):
        """Test that disallowed fields raise ValueError"""
        parser = DjangoQueryParser(allowed_fields={'status', 'priority'})
        with pytest.raises(ValueError, match="not allowed"):
            parser.parse('secret_field:value')

    def test_multiple_fields_one_disallowed(self):
        """Test query with mixed allowed/disallowed fields"""
        parser = DjangoQueryParser(allowed_fields={'status', 'priority'})
        with pytest.raises(ValueError, match="not allowed"):
            parser.parse('status:active AND secret_field:value')

    def test_no_whitelist_allows_all(self):
        """Test that no whitelist allows all fields"""
        parser = DjangoQueryParser()  # No whitelist
        q = parser.parse('any_field:value')
        assert q == Q(any_field__exact='value')


class TestComplexQueries:
    """Test complex real-world query scenarios"""

    def setup_method(self):
        """Set up test fixtures"""
        self.parser = DjangoQueryParser(
            allowed_fields={'status', 'priority', 'name', 'is_active', 'price', 'created_at'}
        )

    def test_complex_query_1(self):
        """Test complex query from documentation example"""
        q = self.parser.parse(
            '(status:active OR status:pending) AND priority>=5 AND name~="John Doe"'
        )
        expected = (
            (Q(status__exact='active') | Q(status__exact='pending')) &
            Q(priority__gte=5) &
            Q(name__icontains='John Doe')
        )
        assert q == expected

    def test_complex_query_2(self):
        """Test complex query with exclusion and multiple types"""
        q = self.parser.parse('is_active:true AND price<100.00 AND priority!=1')
        expected = Q(is_active__exact=True) & Q(price__lt=100.0) & ~Q(priority__exact=1)
        assert q == expected

    def test_multiple_exclusions(self):
        """Test multiple exclusion operators"""
        q = self.parser.parse('status!=inactive AND priority!=0')
        expected = ~Q(status__exact='inactive') & ~Q(priority__exact=0)
        assert q == expected


class TestErrorHandling:
    """Test error handling and invalid queries"""

    def setup_method(self):
        """Set up test fixtures"""
        self.parser = DjangoQueryParser()

    def test_invalid_syntax(self):
        """Test that invalid syntax raises ValueError"""
        with pytest.raises(ValueError, match="Invalid query string"):
            self.parser.parse('status:active AND')

    def test_unmatched_parenthesis(self):
        """Test unmatched parenthesis raises error"""
        with pytest.raises(ValueError, match="Invalid query string"):
            self.parser.parse('(status:active')

    def test_invalid_operator(self):
        """Test that parser handles operator validation"""
        # The grammar should not allow invalid operators
        with pytest.raises(ValueError, match="Invalid query string"):
            self.parser.parse('status&active')


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def setup_method(self):
        """Set up test fixtures"""
        self.parser = DjangoQueryParser()

    def test_zero_value(self):
        """Test parsing zero as a value"""
        q = self.parser.parse('priority:0')
        assert q == Q(priority__exact=0)

    def test_negative_number(self):
        """Test parsing negative numbers"""
        q = self.parser.parse('temperature:-5')
        assert q == Q(temperature__exact=-5)

    def test_field_with_underscores(self):
        """Test field names with underscores"""
        q = self.parser.parse('user_name:john')
        assert q == Q(user_name__exact='john')

    def test_field_with_numbers(self):
        """Test field names with numbers"""
        q = self.parser.parse('field123:value')
        assert q == Q(field123__exact='value')

    def test_empty_quoted_string(self):
        """Test empty quoted string"""
        q = self.parser.parse('name:""')
        assert q == Q(name__exact='')

    def test_whitespace_in_values(self):
        """Test that whitespace is handled correctly"""
        q = self.parser.parse('name:"John   Doe"')
        assert q == Q(name__exact='John   Doe')
