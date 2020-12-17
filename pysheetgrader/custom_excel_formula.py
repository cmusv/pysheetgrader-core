import sympy
from sympy import symbols, lambdify
from sympy.utilities.lambdify import implemented_function


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
    # We can also reuse Sympy's predefined function, especially for formula with variadic args like sum.

    # This is just a sample.

    custom_power = implemented_function('custom_pow', lambda base, power: pow(base, power))
    x, y = symbols("x y")
    ___excel_formula_lambdas = {
        'sum': sympy.Add,
        'custom_pow': lambdify((x, y), custom_power(x, y))
    }

    return ___excel_formula_lambdas
