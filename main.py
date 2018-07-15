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

    opt_declaration: type NAME ["=" expression]?
    declaration: type NAME "=" expression

    expression: "(" expression ")"
              | expression "." expression
              | expression "[" expression "]"
              | NAME "(" (expression ( "," expression )*)? ")"
              | "!" expression
              | "-" expression
              | "if" expression "then" expression "else" expression
              | expression "*" expression
              | expression "%" expression
              | expression "/" expression
              | expression "+" expression
              | expression "-" expression
              | expression "<" expression
              | expression "<=" expression
              | expression ">" expression
              | expression ">=" expression
              | expression "==" expression
              | expression "!=" expression
              | expression "&&" expression
              | expression "||" expression
              | literal
              | NAME

    type: actual_type "?"?
    actual_type: "Int"                            -> type_int
               | "Float"                          -> type_float
               | "Boolean"                        -> type_boolean
               | "String"                         -> type_string
               | "File"                           -> type_file
               | "Array" "[" type "]" "+"?        -> type_array
               | "Map" "[" type "," type "]" "+"? -> type_map

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


def main():
    import sys
    if "-t" in sys.argv:
        import tests
        for t in tests.t:
            print(NativizeData().transform(wdl_parser.parse(t)))
    elif len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            print(wdl_parser.parse(f.read()).pretty())
    else:
        import tests
        for t in tests.t:
            print(wdl_parser.parse(t))

if __name__ == '__main__':
    main()
