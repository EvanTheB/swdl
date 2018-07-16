from lark import Lark

wdl_parser = Lark(r"""
    ?doc: task* workflow task*

    workflow: "workflow" NAME "{" input? workflow_block* output? "}"
    workflow_block: declaration | call | scatter
    task: "task" NAME "{" input? declaration* command declaration* runtime? declaration* output? "}"

    input: "input" "{" opt_declaration* "}"
    output: "output" "{" declaration* "}"

    call: "call" NAME [ "{" "input" "{" variable_mapping* "}" "}" ]
    variable_mapping: NAME "=" expression

    scatter: "scatter" "(" NAME "in" expression ")" "{" workflow_block* "}"

    runtime: "runtime" "{" variable_mapping* "}"

    opt_declaration: type NAME ["=" expression]? -> decl
    declaration: type NAME "=" expression        -> decl

    expression: "(" expression ")"                                  -> paren
              | expression "." expression                           -> selection
              | expression "[" expression "]"                       -> getitem
              | NAME "(" (expression ( "," expression )*)? ")"      -> func
              | "!" expression             -> not_
              | "-" expression             -> neg
              | "if" expression "then" expression "else" expression -> ternary
              | expression "*" expression  -> mul
              | expression "%" expression  -> mod
              | expression "/" expression  -> truediv
              | expression "+" expression  -> add
              | expression "-" expression  -> sub
              | expression "<" expression  -> lt
              | expression "<=" expression -> le
              | expression ">" expression  -> gt
              | expression ">=" expression -> ge
              | expression "==" expression -> eq
              | expression "!=" expression -> ne
              | expression "&&" expression -> and_
              | expression "||" expression -> or_
              | literal
              | NAME -> name_usage

    type: actual_type "?"?
    actual_type: "Int"                            -> type_int
               | "Float"                          -> type_float
               | "Boolean"                        -> type_boolean
               | "String"                         -> type_string
               | "File"                           -> type_file
               | "Array" "[" type "]" "+"?        -> type_array
               | "Map" "[" type "," type "]"      -> type_map

    literal: string
           | SIGNED_INT         -> int
           | SIGNED_FLOAT       -> float
           | "true"             -> true
           | "false"            -> false
           | "{" ( expression ":" expression ( "," expression ":" expression )*)? "}" -> map_literal
           | "[" ( expression ( "," expression )*)? "]" -> array_literal

    string: "\"" string_part* "\""
    string_part: actual_string
        | "~{" expression "}" -> string_interpolation
    actual_string: ( /[^"~]+/ | /~+(?!{)/ )*

    command: "command" "<<<" command_part* ">>>"
    command_part: /[^>~]+/
        | "~{" expression "}"
        | /~(?!{)/
        | />(?!>>)/

    %import common.ESCAPED_STRING
    %import common.SIGNED_FLOAT
    %import common.SIGNED_INT
    %import common.CNAME -> NAME

    %import common.WS
    %ignore WS

    COMMENT: /#.*/
    %ignore COMMENT

    """,
    start='doc',
    ambiguity="explicit",
    # "experimental", do Tokens have this anyway?
    # propagate_positions=True,
)

from lark import Transformer
from lark.lexer import Token

class NativizeData(Transformer):
    # TODO losing line numbers?

    def actual_string(self, args):
        return Token('string_part', ''.join(args))

    def int(self, args):
        return Token('int', int(args[0]))

    def float(self, args):
        return Token('float', float(args[0]))

    # can't do these yet as args are not yet pythonised
    # def map_literal(self, args):
    #     return dict(args)

    # def array_literal(self, args):
    #     return tuple(args)

    true = lambda self, _: Token('bool', True)
    false = lambda self, _: Token('bool', False)

import re
re_op = re.compile(r'\|`(\w*)`\|`(.*)`\|`(\w*)`\|`(\w*)`\|.*\|')

import collections
# op -> (l,r) -> result
valid_operators = collections.defaultdict(dict)
op_map = {
    # "!": "not",
    # "-": "neg",
    # "": "ternary",
    "*": "mul",
    "%": "mod",
    "/": "truediv",
    "+": "add",
    "-": "sub",
    "<": "lt",
    "<=": "le",
    ">": "gt",
    ">=": "ge",
    "==": "eq",
    "!=": "ne",
    "&&": "and_",
    "||": "or_",
}


import operators
for l in operators.d.split('\n'):
    m = re_op.match(l)
    assert m, "operator fail: " + l
    valid_operators[op_map[m.group(2)]][m.group(1,3)] = m.group(4)

class TypeCheck(Transformer):
    def __init__(self):
        super()
        self.names = {}
        for operator in valid_operators:
            # http://stackoverflow.com/questions/1015307/python-bind-an-unbound-method#comment8431145_1015405
            # https://gist.github.com/hangtwenty/a928b801ca5c7705e94e
            f = lambda _, args: valid_operators[operator][args[0], args[1]]
            setattr(self, operator,
                f.__get__(self, self.__class__)
            )

    def expression(self, args):
        print (args, self.names)

    def type(self, args):
        # TODO opt
        return args[0].data

    def decl(self, args):
        assert args[1] not in self.names, "name used twice"
        self.names[args[1]] = args[0]

    string = lambda self, _: 'type_string'
    int = lambda self, _: 'type_int'
    float = lambda self, _: 'type_float'
    true = lambda self, _: 'type_boolean'
    false = lambda self, _: 'type_boolean'

def main():
    import sys
    if "-t" in sys.argv:
        import tests
        print(TypeCheck().transform(wdl_parser.parse(tests.t[-1])))
        # for t in tests.t:
            # print(NativizeData().transform(wdl_parser.parse(t)))
            # for x in NativizeData().transform(wdl_parser.parse(t)).iter_subtrees():
            #     print(x)
            #     print()
            # print()
    elif len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            print(wdl_parser.parse(f.read()).pretty())
    else:
        import tests
        for t in tests.t:
            print(wdl_parser.parse(t))

if __name__ == '__main__':
    main()
