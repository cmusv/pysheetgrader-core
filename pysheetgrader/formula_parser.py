from openpyxl.formula import Tokenizer
from openpyxl.formula.tokenizer import Token
from openpyxl.worksheet.datavalidation import expand_cell_ranges
from sympy.parsing.sympy_parser import parse_expr
import re


def parse_formula(formula):
    """
    Returns the Sympy-parsed form for of the passed formula.
    So far, this method will remove the initial equals (=) sign and expand any cell ranges.
    :return Sympy expression that can be passed to Sympy's `simplify` method.
    """

    string_tokens = []
    formula_tokenizer = Tokenizer(formula)

    for token in formula_tokenizer.items:
        # Uncomment this part for debugging.
        # print(f"Token value: {token.value}, token type: {token.type}, token subtype: {token.subtype}")

        if token.subtype == Token.RANGE:  # TODO: This will still fail on sheet reference ranges.
            expanded_range = expand_cell_ranges(token.value)
            encoded_range = [encode_cell_reference(r) for r in expanded_range]
            string_range = ",".join(encoded_range)
            string_tokens.append(string_range)

        elif token.type == Token.OP_POST and token.value == "%":
            last_number = string_tokens.pop()
            string_tokens.append(f"({last_number}/100)")

        elif token.type == Token.OP_IN and token.value == "^":
            string_tokens.append("**")

        else:
            string_tokens.append(token.value)

    expanded_form = "".join(string_tokens)

    return parse_expr(expanded_form)


def encode_cell_reference(reference):
    """
    Encodes the string of cell reference so it won't clash with predefined variables in Sympy.
    """

    column_finder = re.search('(.+?)[0-9]+', reference)

    # Early return
    if not column_finder:
        return reference

    column = column_finder.group(1)
    row = reference.replace(column, "")

    return f"{column}_{row}"


def decode_cell_reference(encoded_reference):
    """
    Decodes the cell reference from encode_cell_reference method so it can be used in normal spreadsheet operations.
    """
    return encoded_reference.replace('_', '')


