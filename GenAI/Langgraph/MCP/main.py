# Local MCP Server
from __future__ import annotations
from fastmcp import FastMCP

mcp = FastMCP("arith")

def _as_number(x):
    # Accept init/float or numeric strings; raise clean errors otherwise
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str):
        return float(x.strip())
    raise TypeError("Expected a number (int/float or numeric string)")


def _normalize_result(x):
    # Convert floats that are whole numbers to ints for cleaner tool outputs
    if isinstance(x, float) and x.is_integer():
        return int(x)
    return x

@mcp.tool()
async def add(a: float, b: float) -> float:
    """Return a + b."""
    return _normalize_result(_as_number(a) + _as_number(b))

@mcp.tool()
async def subtract(a: float, b: float) -> float:
    """Return a - b."""
    return _normalize_result(_as_number(a) - _as_number(b))

@mcp.tool()
async def multiply(a: float, b: float) -> float:
    """Return a * b."""
    return _normalize_result(_as_number(a) * _as_number(b))

@mcp.tool()
async def divide(a: float, b: float) -> float:
    """Return a / b. Raises on division by zero."""
    a = _as_number(a)
    b = _as_number(b)

    if b == 0:
        raise ZeroDivisionError("Division by zero")
    return _normalize_result(a / b)

@mcp.tool()
async def power(a: float, b: float) -> float:
    """Return a ** b."""
    return _normalize_result(_as_number(a) ** _as_number(b))

@mcp.tool()
async def modulus(a: float, b: float) -> float:
    """Return a % b. Raises on modulus by zero."""
    a = _as_number(a)
    b = _as_number(b)

    if b == 0:
        raise ZeroDivisionError("Modulus by zero")
    return _normalize_result(a % b)

if __name__ == "__main__":
    mcp.run()