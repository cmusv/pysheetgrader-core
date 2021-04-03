from sympy.utilities.lambdify import implemented_function
from sympy import symbols, lambdify
import sympy


"""
Static dictionary of this file. Please use `get_excel_formula_lambdas()` method to retrieve this instead of
    accessing it directly.
"""
___excel_formula_lambdas = None


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
    # We can also reuse Sympy's predefined function, especially for formula with variable args like sum.

    # This is just a sample.

    roundup_f = implemented_function('roundup', lambda number, digits: roundup(number, digits))
    excel_if = implemented_function('execl_if', lambda cond, first, second: first if cond else second)
    x, y, z = symbols("x y z")
    ___excel_formula_lambdas = {
        'sum': sympy.Add,
        'max': sympy.Max,
        'min': sympy.Min,
        'excel_if': lambdify((x, y, z), excel_if(x, y, z)),
        'roundup': lambdify((x, y), roundup_f(x, y)),
    }

    return ___excel_formula_lambdas


# Custom formula definition

def roundup(number, decimals=0):
    multiplier = 10 ** decimals
    # sympy.ceiling is preferable instead of math.ceil here to allow parsing unknown variables.
    result = sympy.ceiling(number * multiplier) / multiplier

    try:
        float_result = sympy.Float(result)
        return float_result
    except Exception:
        # Just in case the result cannot be converted to float, e.g. due to Formula comparison
        return result
