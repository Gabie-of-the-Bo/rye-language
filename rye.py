from typing import *
from re import sub


"""
=======================================
| <3Ɔ~ (The Rye Programming Language) |
=======================================

This is the official implementation of the <3Ɔ~ programming language (Rye from now on).

"""


class RyeContext:
    initial_funcs={
        # Definitions
        'set': lambda ctx, a, b: ctx.define_atom(a.args, b.evaluate(ctx)),
        'eset': lambda ctx, a, b: ctx.define_atom(a.evaluate(ctx).args, b.evaluate(ctx)),
        'unset': lambda ctx, a: ctx.delete_atom(a.args),
        'def': lambda ctx, a, b: ctx.define_atom(a.args, b),
        'fun': lambda ctx, *a: ctx.define_func(a[0].args, ctx.get_function_def(a[1:-1], a[-1])),

        # Meta
        'eval': lambda ctx, a: a.evaluate(ctx).evaluate(ctx),
        'do': lambda ctx, *a: [i.evaluate(ctx) for i in a][-1],
        'do-n': lambda ctx, j, *a: [i.evaluate(ctx) for i in a][j.evaluate(ctx)],
        'ret': lambda ctx, *a: [ctx.get_atom(a[0].args), ctx.delete_atom(a[0].args)][0],

        # Arithmetic
        '+': lambda ctx, a, b: a.evaluate(ctx) + b.evaluate(ctx),
        '-': lambda ctx, a, b: a.evaluate(ctx) - b.evaluate(ctx),
        '*': lambda ctx, a, b: a.evaluate(ctx) * b.evaluate(ctx),
        '/': lambda ctx, a, b: a.evaluate(ctx) / b.evaluate(ctx),
        '%': lambda ctx, a, b: a.evaluate(ctx) % b.evaluate(ctx),

        # Logic
        '<': lambda ctx, a, b: a.evaluate(ctx) < b.evaluate(ctx),
        '>': lambda ctx, a, b: a.evaluate(ctx) > b.evaluate(ctx),
        '=': lambda ctx, a, b: a.evaluate(ctx) == b.evaluate(ctx),
        'any': lambda ctx, a: any(a.evaluate(ctx)),
        'all': lambda ctx, a: all(a.evaluate(ctx)),

        # Output
        'print': lambda ctx, a: print(a.evaluate(ctx)),

        # Flow control
        'if': lambda ctx, a, b, c: b.evaluate(ctx) if a.evaluate(ctx) else c.evaluate(ctx),
        'repeat': lambda ctx, a, b: [b.evaluate(ctx) for _ in range(a.evaluate(ctx))],
    }

    def __init__(self):
        self.atoms = {}
        self.funcs = RyeContext.initial_funcs

    def get_atom(self, name: str):
        return self.atoms[name]

    def get_func(self, name: str):
        return self.funcs[name]

    def define_atom(self, name: str, value):
        self.atoms[name] = value

    def delete_atom(self, name: str):
        self.atoms.pop(name)

    def define_func(self, name: str, value):
        self.funcs[name] = value

    def delete_func(self, name: str):
        self.funcs.pop(name)

    def get_function_def(self, params, expr):
        def wrapper(ctx, *call_args):
            for p, c in zip(params, call_args):
                ctx.define_atom(p.args, c)

            return expr.evaluate(ctx)

        return wrapper

class RyeExpression:
    CONS, ATOM, FUNC = range(3)

    def __init__(self, args: List, etype: int):
        self.args = args
        self.etype = etype

    def evaluate(self, context: RyeContext):
        if self.etype == RyeExpression.CONS:
            return self.args

        if self.etype == RyeExpression.ATOM:
            return context.get_atom(self.args)

        if self.etype == RyeExpression.FUNC:
            return context.get_func(self.args[0].args)(context, *self.args[1:])

def is_enclosed(code):
    count = 0

    for i, t in enumerate(code):
        if t == '(': count += 1
        if count == 0: return False
        elif t == ')': count -= 1

    return count == 0

def contextual_split(code):
    j, count = 0, 0

    for i, t in enumerate(code + ' '):
        if t == '(': count += 1
        
        if count == 0 and t in ' \n': 
            yield code[j:i].strip()
            j = i
        
        elif t == ')': count -= 1

def parse_expr(code: str):
    if all(i.isdigit() for i in code):
        return RyeExpression(int(code), RyeExpression.CONS)

    if code.upper() == 'TRUE':
        return RyeExpression(True, RyeExpression.CONS)

    if code.upper() == 'FALSE':
        return RyeExpression(False, RyeExpression.CONS)

    if is_enclosed(code):
        return RyeExpression([parse_expr(i) for i in contextual_split(code[1:-1])], RyeExpression.FUNC)

    if code.startswith('\''):
        return RyeExpression([RyeExpression('eval', None), parse_expr(code[1:])], RyeExpression.FUNC)

    return RyeExpression(code, RyeExpression.ATOM)

def parse(code: str):
    yield from (parse_expr(i) for i in contextual_split(code))

def evaluate(code: str):
    ctx = RyeContext()

    code = sub(r'\s{2,}', ' ', code.strip())
    code = sub(r'\s+\)', ')', code)
    code = sub(r'\(\s+', '(', code)

    for expr in parse(code):
        expr.evaluate(ctx)