from openpyxl.formula import Tokenizer
from openpyxl.formula.tokenizer import Token
from openpyxl.worksheet.datavalidation import expand_cell_ranges
from sympy.parsing.sympy_parser import parse_expr
import re


def parse_formula_tokens(formula: str) -> [str]:
    """
    Parse the string tokens from the formula.
    :param formula: String value of the formula. Should start with '=', otherwise it will throw an exception.
    :return: A list of string values of tokens.
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

    return string_tokens


def parse_formula_inputs(formula: str, encoded: bool = True) -> [str]:
    """
    Filter the tokens from `parse_formula_tokens` and returns only the input coordinates.

    :param encoded: should the returned input coordinated being encoded or not
    :param formula: String value of the formula. Should start with '=', otherwise it will throw an exception.
    :return: A list of strings of input coordinates.
    """
    tokens = parse_formula_tokens(formula)
    inputs = []
    for token in tokens:
        result = re.match(r"^[a-z]+_\d+$", token)
        if result is not None:
            inputs.append(token if encoded else decode_cell_reference(token))
    return inputs


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

    string_tokens = parse_formula_tokens(formula)
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
