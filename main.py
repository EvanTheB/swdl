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

    command: "command" /<<<.*?>>>/s
    runtime: "runtime" "{" variable_mapping* "}"
    
    opt_declaration: type NAME ["=" expression]?
    declaration: type NAME "=" expression

    expression: "(" expression ")"
              | expression "." expression
              | expression "[" expression "]"
              | expression "(" (expression ( "," expression )*)? ")"
              | "!" expression
              | "+" expression
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
              | "{" ( expression ":" expression ( "," expression ":" expression )*)? "}"
              | "[" ( expression ( "," expression )*)? "]"
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
           | SIGNED_NUMBER      -> number
           | "true"             -> true
           | "false"            -> false

    string : ESCAPED_STRING

    %import common.ESCAPED_STRING
    %import common.SIGNED_NUMBER
    %import common.CNAME -> NAME
    %import common.WS
    COMMENT: /#.*/
    %ignore WS
    %ignore COMMENT

    """, start='doc', ambiguity="explicit")

from lark import Transformer

class WDLTransformer(Transformer):
    def string(self, v):
        return v[0][1:-1]
    def number(self, v):
        return float(v[0])

    true = lambda self, _: True
    false = lambda self, _: False

#print(WDLTransformer().transform(wdl_parser.parse('13.1')))

import sys
if len(sys.argv) > 1:
    with open(sys.argv[1]) as f:
        print(wdl_parser.parse(f.read()).pretty())
else:
    import tests
    for t in tests.t:
        print(wdl_parser.parse(t).pretty())

