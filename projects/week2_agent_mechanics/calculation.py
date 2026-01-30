
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

class CalculatorTool():
    """A tool for performing mathematical calculations"""

    def get_schema(self):
        return {
            "name": "calculator",
            "description": "Performs basic mathematical calculations, use also for simple additions",
            "input_schema": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate (e.g., '2+2', '10*5')"
                    }
                },
                "required": ["expression"]
            }
        }

    def execute(self, expression):
        """
        Evaluate mathematical expressions.
        WARNING: This tutorial uses eval() for simplicity but it is not recommended for production use.

        Args:
            expression (str): The mathematical expression to evaluate
        Returns:
            float: The result of the evaluation
        """
        try:
            result = eval(expression)
            return {"result": result}
        except:
            return {"error": "Invalid mathematical expression"}

calculator_tool = CalculatorTool()
print(calculator_tool.execute("157.09 * 493.89"))