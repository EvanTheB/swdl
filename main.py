from lark import Lark

wdl_parser = Lark(r"""
    ?doc: workflow

    workflow: "workflow" "{" input "}"

    input: "input" "{" declaration* "}"

    declaration: type NAME ("=" expression)?

    expression: value

    type: "Int"    -> type_int
        | "Float"  -> type_float
        | "Boolean"  -> type_boolean
        | "String"  -> type_string
        | "File"  -> type_file

    value:  string
          | SIGNED_NUMBER      -> number
          | "true"             -> true
          | "false"            -> false


    string : ESCAPED_STRING

    %import common.ESCAPED_STRING
    %import common.SIGNED_NUMBER
    %import common.CNAME -> NAME
    %import common.WS
    %ignore WS

    """, start='doc')

print(wdl_parser.parse(r'''workflow { input { Int abc } }''').pretty())
print(wdl_parser.parse(r'''workflow { input { String abc = 1 } }''').pretty())

from lark import Transformer

class WDLTransformer(Transformer):
    def string(self, v):
        return v[0][1:-1]
    def number(self, v):
        return float(v[0])

    true = lambda self, _: True
    false = lambda self, _: False

#print(WDLTransformer().transform(wdl_parser.parse('13.1')))

