"""
Safe local maths engine for JARVIS.

Examples:
    2 + 3 * 4
    10 / 2
    2^8
    sqrt(144)
    sin(30)
    cos(60)
    tan(45)
    log(100)
    ln(e)
    factorial(5)
    abs(-12)
    round(3.14159, 2)
"""

import ast
import math
import operator
import re


FUNCTIONS = {
    "sqrt": math.sqrt,
    "sin": lambda x: math.sin(math.radians(x)),
    "cos": lambda x: math.cos(math.radians(x)),
    "tan": lambda x: math.tan(math.radians(x)),
    "asin": lambda x: math.degrees(math.asin(x)),
    "acos": lambda x: math.degrees(math.acos(x)),
    "atan": lambda x: math.degrees(math.atan(x)),
    "log": math.log10,
    "ln": math.log,
    "exp": math.exp,
    "abs": abs,
    "floor": math.floor,
    "ceil": math.ceil,
    "factorial": math.factorial,
    "round": round,
    "pow": pow,
}

CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
    "tau": math.tau,
}

BINARY_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
}

UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _clean_expression(expression: str) -> str:
    text = expression.lower().strip()

    replacements = [
        ("×", "*"),
        ("÷", "/"),
        ("−", "-"),
        ("^", "**"),
        (" squared", "**2"),
        (" cubed", "**3"),
        (" plus ", "+"),
        (" minus ", "-"),
        (" times ", "*"),
        (" multiplied by ", "*"),
        (" divided by ", "/"),
    ]

    for old, new in replacements:
        text = text.replace(old, new)

    # Common spoken-number operators at the edges.
    text = re.sub(r"^plus ", "+", text)
    text = re.sub(r"^minus ", "-", text)
    return text


def _eval(node):
    if isinstance(node, ast.Expression):
        return _eval(node.body)

    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value

    if isinstance(node, ast.Name) and node.id in CONSTANTS:
        return CONSTANTS[node.id]

    if isinstance(node, ast.BinOp) and type(node.op) in BINARY_OPS:
        left = _eval(node.left)
        right = _eval(node.right)
        return BINARY_OPS[type(node.op)](left, right)

    if isinstance(node, ast.UnaryOp) and type(node.op) in UNARY_OPS:
        return UNARY_OPS[type(node.op)](_eval(node.operand))

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only simple maths functions are allowed.")
        function = FUNCTIONS.get(node.func.id)
        if function is None:
            raise ValueError(f"Unknown function '{node.func.id}'.")
        if node.keywords:
            raise ValueError("Keyword arguments are not supported.")
        args = [_eval(arg) for arg in node.args]
        return function(*args)

    raise ValueError("That expression contains something I cannot calculate.")


def calculate(expression: str):
    """Safely calculate an arithmetic expression."""
    text = _clean_expression(expression)

    if len(text) > 200:
        raise ValueError("The expression is too long.")

    try:
        tree = ast.parse(text, mode="eval")
        result = _eval(tree)
    except ZeroDivisionError as exc:
        raise ValueError("Division by zero is not allowed.") from exc
    except (SyntaxError, TypeError, OverflowError, ValueError) as exc:
        if isinstance(exc, ValueError):
            raise
        raise ValueError("Invalid mathematical expression.") from exc

    if isinstance(result, float):
        if not math.isfinite(result):
            raise ValueError("The result is not a finite number.")
        if result.is_integer():
            return int(result)
        return round(result, 10)

    return result


def looks_like_math(text: str) -> bool:
    """Return True for likely arithmetic/math commands."""
    value = text.lower().strip()

    if any(name + "(" in value for name in FUNCTIONS):
        return True

    if any(symbol in value for symbol in ("+", "-", "*", "/", "^", "×", "÷")):
        return bool(re.search(r"\d", value))

    return bool(
        re.search(r"\d", value)
        and any(word in value for word in (
            "plus", "minus", "times", "multiplied", "divided",
            "power", "squared", "cubed",
        ))
    )
