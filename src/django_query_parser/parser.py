from lark import Lark, Transformer, v_args
from django.db.models import Q

# --- 1. Define the Query Language Grammar (Lark EBNF) ---

# The grammar defines the structure of the allowed query string.
# Rules are lowercase (e.g., 'start'), Terminals are uppercase (e.g., 'NUMBER').
QUERY_GRAMMAR = r"""
    ?start: or_expr

    // Operator Precedence: AND binds tighter than OR
    ?or_expr: and_expr (OR and_expr)*
    ?and_expr: comparison (AND comparison)*
    ?comparison: term | "(" or_expr ")"

    // Terminals: Basic building blocks of a comparison (e.g., field:value)
    ?term: lookup_statement

    lookup_statement: FIELD OPERATOR VALUE

    // --- Terminals Definitions ---

    // Logical Operators
    AND: "AND" | "and"
    OR: "OR" | "or"

    // Comparison Operators (Longest matches first for safety)
    OPERATOR: ">=" | "<=" | ">" | "<" | ":=" | ":" | "~=" | "!="

    // Field names must be snake_case identifiers
    FIELD: /\w+/

    // Values can be quoted strings or unquoted single words/numbers
    VALUE: ESCAPED_STRING
         | SIGNED_NUMBER
         | UNQUOTED_VALUE
         | "true" | "false" | "null"

    UNQUOTED_VALUE: /\w+/

    // --- Imports and Configuration ---
    %import common.ESCAPED_STRING
    %import common.SIGNED_NUMBER
    %import common.WS
    %ignore WS
"""

# --- 2. Define the Transformer (Converts Tree to Django Q Object) ---

@v_args(inline=True)    # Passes the children of the rule directly to the method
class QueryTranslator(Transformer):
    """
    Transforms the parsed Lark Tree into a Django Q object.
    """

    # Maps query operators to Django ORM lookups
    OPERATOR_MAP = {
        ":": "exact",
        ":=": "exact", # Treat as exact for simplicity
        "~=": "icontains", # Case-insensitive containment
        "!=": "exclude__exact", # Handled later, but useful mapping
        ">": "gt",
        "<": "lt",
        ">=": "gte",
        "<=": "lte",
    }

    def __init__(self, allowed_fields=None):
        """
        Initialize with a set of allowed fields for security.
        """
        self.allowed_fields = set(allowed_fields) if allowed_fields else None
        super().__init__()

    # --- Logical Combination Methods ---

    def or_expr(self, *args):
        # Combines the results of the OR-separated expressions with Q | (OR)
        # Filter out Token objects (the AND/OR terminals) and keep only Q objects
        q_objects = [arg for arg in args if isinstance(arg, Q)]
        if not q_objects:
            return Q()
        if len(q_objects) == 1:
            return q_objects[0]
        result = q_objects[0]
        for q_obj in q_objects[1:]:
            result = result | q_obj
        return result

    def and_expr(self, *args):
        # Combines the results of the AND-separated expressions with Q & (AND)
        # Filter out Token objects (the AND/OR terminals) and keep only Q objects
        q_objects = [arg for arg in args if isinstance(arg, Q)]
        if not q_objects:
            return Q()
        if len(q_objects) == 1:
            return q_objects[0]
        result = q_objects[0]
        for q_obj in q_objects[1:]:
            result = result & q_obj
        return result

    # --- Leaf Node/Comparison Methods ---

    def lookup_statement(self, field_token, operator_token, value_token):
        field = str(field_token)
        operator = str(operator_token)
        value = self._clean_value(str(value_token))

        # Security Guardrail: Check if the field is whitelisted
        if self.allowed_fields and field not in self.allowed_fields:
            raise ValueError(f"Querying on field '{field}' is not allowed.")

        # Special handling for exclusion (!=)
        if operator == "!=":
            lookup = f"{field}__{self.OPERATOR_MAP.get(':')}" # Default to exact
            # Returns a Q object that negates the result (NOT Q)
            return ~Q(**{lookup: value})

        # Standard handling
        lookup_type = self.OPERATOR_MAP.get(operator)
        if not lookup_type:
             raise ValueError(f"Unsupported operator '{operator}' in query.")

        lookup = f"{field}__{lookup_type}"
        return Q(**{lookup: value})

    def _clean_value(self, raw_value):
        """Clean and convert the raw token value."""
        # Strip quotes from strings
        if raw_value.startswith('"') and raw_value.endswith('"'):
            return raw_value.strip('"')

        # Convert simple types
        if raw_value.lower() == 'true':
            return True
        if raw_value.lower() == 'false':
            return False
        if raw_value.lower() == 'null':
            return None

        # Attempt to convert to float/int if it looks like a number
        try:
            return int(raw_value)
        except ValueError:
            try:
                return float(raw_value)
            except ValueError:
                # Fallback to the raw string
                return raw_value.replace("\\n", "\n").replace("\\t", "\t")

    # Pass through other tokens (FIELD, OPERATOR, etc.) directly as strings
    FIELD = str
    OPERATOR = str
    VALUE = str
    UNQUOTED_VALUE = str
    ESCAPED_STRING = str

# --- 3. Public Interface Class ---

class DjangoQueryParser:
    """
    The main interface for developers. Parses a query string into a Django Q object.
    """
    def __init__(self, allowed_fields=None):
        self.parser = Lark(QUERY_GRAMMAR, parser='lalr')
        self.allowed_fields = allowed_fields

    def parse(self, query_string: str) -> Q:
        """
        Parses a query string and returns the final Django Q object.
        """
        if not query_string:
            return Q() # Return an empty Q object if the string is empty

        try:
            # 1. Parse the string into a syntax tree
            tree = self.parser.parse(query_string)

            # 2. Transform the tree into a Django Q object
            translator = QueryTranslator(allowed_fields=self.allowed_fields)
            q_object = translator.transform(tree)

            return q_object

        except Exception as e:
            # Catch parsing/translation errors and wrap them for clarity
            raise ValueError(f"Invalid query string: {e}") from e
