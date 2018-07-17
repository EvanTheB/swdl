from lark import Lark

types = r'''
    type: hidden_type
    ?hidden_type: actual_type "?"?
    ?actual_type: TYPE_INT | TYPE_FLOAT | TYPE_BOOLEAN
               | TYPE_STRING | TYPE_FILE
               | "Array" "[" hidden_type "]" "+"?        -> type_array
               | "Map" "[" hidden_type "," hidden_type "]"      -> type_map
    TYPE_INT: "Int"
    TYPE_FLOAT: "Float"
    TYPE_BOOLEAN: "Boolean"
    TYPE_STRING: "String"
    TYPE_FILE: "File"
'''
type_parser = Lark(types + r'''%import common.WS
    %ignore WS''',
    start='type',
    ambiguity="explicit",
)
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

    opt_declaration: hidden_type NAME ["=" expression] -> decl
    declaration: hidden_type NAME "=" expression        -> decl

    expression: or_expr
              | ( "if" or_expr "then" or_expr "else" or_expr )                -> ternary


    ?or_expr  : and_expr
              | and_expr ("||" and_expr)+                                     -> or_
    ?and_expr : eq_expr
              | eq_expr ("&&" eq_expr)+                                       -> and_
    ?eq_expr  : cmp_expr
              | cmp_expr "!=" cmp_expr                                      -> ne
              | cmp_expr "==" cmp_expr                                      -> eq
    ?cmp_expr : add_expr
              | add_expr ">=" add_expr                                      -> ge
              | add_expr ">" add_expr                                       -> gt
              | add_expr "<=" add_expr                                      -> le
              | add_expr "<" add_expr                                       -> lt
    ?add_expr : mul_expr
              | mul_expr ("-" mul_expr)+                                      -> sub
              | mul_expr ("+" mul_expr)+                                      -> add
    ?mul_expr : unary_expr
              | unary_expr ("/" unary_expr)+                                  -> truediv
              | unary_expr ("%" unary_expr)+                                  -> mod
              | unary_expr ("*" unary_expr)+                                  -> mul
    ?unary_expr: func_expr
              | "-" func_expr                                     -> neg
              | "!" func_expr                                   -> not_
    ?func_expr : index_expr
              | NAME "(" (index_expr ( "," index_expr )*)? ")" -> func
    ?index_expr: dot_expr
              | dot_expr "[" dot_expr "]"                                   -> getitem
    ?dot_expr  : paren_expr
              | paren_expr "." NAME                                         -> selection
    ?paren_expr: literal | "(" expression ")"

    literal: NAME -> name_usage
           | string             -> string
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

    """ + types,
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
op_reverse_map = dict(zip(op_map.values(), op_map.keys()))
# type_map = {
#     "Int" : "type_int",
#     "Float" : "type_float",
#     "Boolean" : "type_boolean",
#     "String" : "type_string",
#     "File" : "type_file",
#     "": None
# }
class TypeMaker(Transformer):
    def type_array(self, args):
        return ('Array', args[0])
    def type_map(self, args):
        return ('Map', args[0], args[1])

def get_type(type_):
    """
    get internal type repr from string
    internal repr just wants to be hashable for now

    Array[File] -> ('type_array', 'type_file')
    Map[Array[File], Int] -> ('type_map', (type_array', 'type_file'), 'type_int')
    """
    # print(type_)
    # print(TypeMaker().transform(type_parser.parse(type_)))
    return TypeMaker().transform(type_parser.parse(type_)).children[0]


import operators
re_op = re.compile(r'\|`(\w*)`\|`(.*)`\|`(\w*)`\|`(\w*)`\|.*\|')
for l in operators.d.split('\n'):
    m = re_op.match(l)
    assert m, "operator fail: " + l
    valid_operators[op_map[m.group(2)]][tuple(get_type(x) for x in m.group(1,3))] = get_type(m.group(4))
assert len(valid_operators) == len(op_map), "some operators not defined"

# this wont work for long
# name -> inputs -> outputs
valid_functions = collections.defaultdict(dict)
re_func = re.compile(r'\|`(.*)`\|`(\w*)`\|`(\w*)`\|')

import functions
for l in functions.d.split('\n'):
    m = re_func.match(l)
    assert m, "function fail: " + l
    input_types = tuple([get_type(t.strip()) for t in m.group(3).split(',') if t.strip()])
    valid_functions[m.group(2)][input_types] = get_type(m.group(1))

# print(valid_operators)
# print(valid_functions)

class TypeCheck(TypeMaker):
    def __init__(self):
        super()
        self.names = {}
        for operator in valid_operators:
            # http://stackoverflow.com/questions/1015307/python-bind-an-unbound-method#comment8431145_1015405
            # https://gist.github.com/hangtwenty/a928b801ca5c7705e94e
            def f(self, args, op=operator):
                assert op in valid_operators, "this should never happen"
                assert (args[0], args[1]) in valid_operators[op], "Operation not defined for types: {} {} {}".format(args[0], op_reverse_map[op], args[1])
                print(op, args, valid_operators[op][args[0], args[1]])
                return valid_operators[op][args[0], args[1]]

            setattr(self, operator,
                f.__get__(self, self.__class__)
            )

    def expression(self, args):
        print ("e", args)
        return args[0]

    def name_usage(self, args):
        print ("n", args)
        assert args[0] in self.names, "name used before declared: {}".format(args[0])
        return self.names[args[0]]

    def type(self, args):
        # TODO opt
        print ("t", args)
        return args[0].data

    def decl(self, args):
        print("d", args)
        assert args[1] not in self.names, "name declared twice: {}".format(args[1])
        self.names[args[1]] = args[0]
        if len(args) > 2:
            assert args[0] == args[2], "wrong type in declaration: {}, {}".format(args[0], args[2])
        return args[0]

    def string_interpolation(self, args):
        print ("si", args)
        assert args[0] == 'String', "string interpolation must evaluate to string"

    def func(self, args):
        assert args[0] in valid_functions, "function does not exist: " + args[0]
        function_inputs = tuple(args[1:])
        assert function_inputs in valid_functions[args[0]], "Function not defined for inputs: {}{}".format(args[0], function_inputs)
        print ("f", args[0], function_inputs)
        return valid_functions[args[0]][function_inputs]

    string = lambda self, args: "String"
    int = lambda self, args: "Int"
    float = lambda self, args: "Float"
    true = lambda self, args: "Boolean"
    false = true

def main():
    import sys
    filenames = [f for f in sys.argv[1:] if f[0] != '-']
    if any(filenames):
        testcases = []
        for f in filenames:
            with open(f) as fd:
                testcases.append(fd.read())
    else:
        import tests
        testcases = tests.t

    for t in testcases:
        print(wdl_parser.parse(t).pretty())

    if "-p" in sys.argv:
        for t in testcases:
            NativizeData().transform(wdl_parser.parse(t))
    if "-t" in sys.argv:
        for t in testcases:
            TypeCheck().transform(wdl_parser.parse(t))

if __name__ == '__main__':
    main()
