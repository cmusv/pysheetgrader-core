from openpyxl.formula import Tokenizer
from openpyxl.formula.tokenizer import Token
from openpyxl.worksheet.datavalidation import expand_cell_ranges
from sympy.utilities.lambdify import lambdify, implemented_function
from sympy.parsing.sympy_parser import parse_expr
from sympy import symbols
import sympy
import re


"""
Static dictionary of this file. Please use `get_excel_formula_lambdas()` method to retrieve this instead of
    accessing it directly.
"""
___excel_formula_lambdas = None


def parse_formula(formula: str, local_dict: dict = None):
    """
    Returns the Sympy-parsed form for of the passed Excel formula. If is preferred to have the lowercased version of
    the formula to allow Sympy use built-in functions (e.g., sqrt).

    So far, this method will always expand any cell ranges.

    This method will raise an exception if the passed `formula` is not a valid Excel formula.

    :param formula: String value of the formula. Should start with '=', otherwise it will throw an exception.
    :param local_dict: Dictionary for replacing variables with values or custom formulas with Sympy lambdas.
        Again, it is preferred to have lowercased keys and custom functions.
    :return: Sympy expression that can be passed to Sympy's `simplify` method.
    """

    if not formula or not isinstance(formula, str):
        raise ValueError(f"Expected formula, got {formula}")
        return

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

    # Lowercase the form, to allow Sympy use built-in functions.
    expanded_form = "".join(string_tokens).lower()

    return parse_expr(expanded_form, local_dict=local_dict)


def encode_cell_reference(reference: str):
    """
    Encodes the string of cell reference so it won't clash with predefined variables in Sympy.
    This method will lowercase the cell references, too.
    """

    column_finder = re.search('(.+?)[0-9]+', reference)

    # Early return
    if not column_finder:
        return reference

    column = column_finder.group(1)
    row = reference.replace(column, "")

    return f"{column}_{row}".lower()


def decode_cell_reference(encoded_reference: str):
    """
    Decodes the cell reference from encode_cell_reference method so it can be used in normal spreadsheet operations.
    This method will uppercase the cell references.
    """
    return encoded_reference.replace('_', '').upper()


def get_excel_formula_lambdas():
    """
    Returns dictionary of Excel formulas as key and the corresponding Sympy lambdas as the value.
    :return: Dictionary instance.
    """
    global ___excel_formula_lambdas

    # If it's already initialized, then early return.
    if ___excel_formula_lambdas:
        return ___excel_formula_lambdas

    # TODO: Implement more function here.
    # Custom implementation
    # The key and the first parameter of the `implemented_function` should be the same.
    # We can also reuse Sympy's predefined function, especially for formula with variadic args like sum.

    # This is just a sample.

    custom_power = implemented_function('custom_pow', lambda base, power: pow(base, power))
    x, y = symbols("x y")
    custom_functions = {
        'sum': sympy.Add,
        'custom_pow': lambdify((x, y), custom_power(x, y))
    }

    return ___excel_formula_lambdas



