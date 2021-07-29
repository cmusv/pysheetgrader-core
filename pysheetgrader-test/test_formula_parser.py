import unittest

from pysheetgrader.formula_parser import parse_formula_tokens, parse_formula, parse_formula_inputs, \
    encode_cell_reference, decode_cell_reference, transform_excel_formula_to_sympy

from pysheetgrader.custom_excel_formula import get_excel_formula_lambdas


class TestFormulaParser(unittest.TestCase):

    def test_parse_formula_tokens(self):
        formula = '= max(b2, b3, b4)'
        tokens = parse_formula_tokens(formula)
        self.assertEqual(tokens, [' ', 'max(', 'b_2', ',', ' ', 'b_3', ',', ' ', 'b_4', ')'])

    def test_parse_formula_inputs_simple(self):
        formula = '= max(ba2, bc3, b42)'
        self.assertEqual(parse_formula_inputs(formula), ['ba_2', 'bc_3', 'b_42'])
        self.assertEqual(parse_formula_inputs(formula, False), ['BA2', 'BC3', 'B42'])

    def test_parse_formula_inputs_complex(self):
        formula = '= excel_if(a2 = "ok", b2, c2)'
        self.assertEqual(parse_formula_inputs(formula), ['a_2', 'b_2', 'c_2'])
        self.assertEqual(parse_formula_inputs(formula, False), ['A2', 'B2', 'C2'])

    def test_transform_excel_formula_to_sympy(self):
        self.assertEqual(transform_excel_formula_to_sympy('= if(a2 = "ok", b2, c2)'), '= excel_if(a2 == "ok", b2, c2)')
        self.assertEqual(transform_excel_formula_to_sympy('= if(a2 = "ok", b2 = 3, c2)'), '= excel_if(a2 == "ok", b2 '
                                                                                          '== 3, c2)')

    def test_parse_formula_max(self):
        formula = '= max(b2, b3, b4)'
        local_dict = {
            'b_2': 1000,
            'b_3': 2000,
            'b_4': 3000,
        }

        local_dict.update(get_excel_formula_lambdas())
        result = parse_formula(formula, local_dict)
        self.assertEqual(result, 3000)

    def test_parse_formula_min(self):
        formula = '= min(b2, b3, b4)'
        local_dict = {
            'b_2': 4000,
            'b_3': 2000,
            'b_4': 3000,
        }

        local_dict.update(get_excel_formula_lambdas())
        result = parse_formula(formula, local_dict)
        self.assertEqual(result, 2000)

    def test_parse_formula_nested_cond_true(self):
        formula = '= excel_if(b2 == "ok", b3, b4)'
        local_dict = {
            'b_2': "ok",
            'b_3': 2000,
            'b_4': 3000,
        }

        local_dict.update(get_excel_formula_lambdas())
        result = parse_formula(formula, local_dict)
        self.assertEqual(result, 2000)

    def test_parse_formula_nested_cond_false(self):
        formula = '= excel_if(b2 == "ok", b3, b4)'
        local_dict = {
            'b_2': "not_ok",
            'b_3': 2000,
            'b_4': 3000,
        }

        local_dict.update(get_excel_formula_lambdas())
        result = parse_formula(formula, local_dict)
        self.assertEqual(result, 3000)

    def test_parse_formula_if_true(self):
        formula = '= excel_if(b2, b3, b4)'
        local_dict = {
            'b_2': True,
            'b_3': 2000,
            'b_4': 3000,
        }

        local_dict.update(get_excel_formula_lambdas())
        result = parse_formula(formula, local_dict)
        self.assertEqual(result, 2000)

    def test_parse_formula_if_false(self):
        formula = '= excel_if(b2, b3, b4)'
        local_dict = {
            'b_2': False,
            'b_3': 2000,
            'b_4': 3000,
        }

        local_dict.update(get_excel_formula_lambdas())
        result = parse_formula(formula, local_dict)
        self.assertEqual(result, 3000)

    def test_encode_cell_reference(self):
        self.assertEqual(encode_cell_reference('BC2'), 'bc_2')
        self.assertEqual(encode_cell_reference('C110'), 'c_110')

    def test_decode_cell_reference(self):
        self.assertEqual(decode_cell_reference('bc_2'), 'BC2')
        self.assertEqual(decode_cell_reference('c_110'), 'C110')
