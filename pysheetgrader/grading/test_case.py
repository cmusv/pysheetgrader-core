
class GradingTestCase:
    """
    Represents a test case for the formula inside of a cell.
    Currently only work for a numeric inputs and output.
    """

    def __init__(self, name: str, expected_output: float, inputs: dict, output_delta: float = 0, failmsg: str = ""):
        """
        Initializer of this class.
        :param name: String value of the test case's name.
        :param expected_output: Float value of the expected output.
        :param inputs: Dictionary of {str: float} with cell reference as key and the float input value as related value.
        :param output_delta: Flaot value of the delta for the expected output. Defaults to 0.
        """
        self.name = name
        self.expected_output = expected_output
        self.output_delta = output_delta
        self.inputs = inputs
        self.failmsg = failmsg
