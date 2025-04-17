#!/usr/bin/python3
import ast
import operator as op
from argparse import ArgumentParser
import os

# taken from https://stackoverflow.com/questions/2371436/evaluating-a-mathematical-expression-in-a-string

# supported operators
operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
             ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor,
             ast.USub: op.neg}

def eval_expr(expr):
    """
    >>> eval_expr('2^6')
    4
    >>> eval_expr('2**6')
    64
    >>> eval_expr('1 + 2*3**(4^5) / (6 + -7)')
    -5.0
    """
    return eval_(ast.parse(expr, mode='eval').body)

def eval_(node):
    match node:
        case ast.Constant(value) if isinstance(value, int):
            return value  # integer
        case ast.BinOp(left, op, right):
            return operators[type(op)](eval_(left), eval_(right))
        case ast.UnaryOp(op, operand):  # e.g., -1
            return operators[type(op)](eval_(operand))
        case _:
            raise TypeError(node)
        

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("expression")
    parser.add_argument("output")
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    start, end = args.expression.split(",")
    start, end = start.strip(), end.strip()
    if start.lower() == "start":
        start = 0
    else:
        start = eval_expr(start)
    if end.lower() == "end":
        end = os.path.getsize(args.input)
    elif end.startswith("+") or end.startswith("-"):
        end = eval_expr(str(start) + end)
    else:
        end = eval_expr(end)
    with open(args.input, 'rb') as f:
        f.seek(start)
        with open(args.output, 'wb') as fo:
            fo.write(f.read(end-start))

if __name__ == "__main__":
    main()