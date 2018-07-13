from lark import Lark

wdl_parser = Lark(r"""
    ?value: string
          | SIGNED_NUMBER      -> number
          | "true"             -> true
          | "false"            -> false


    string : ESCAPED_STRING

    %import common.ESCAPED_STRING
    %import common.SIGNED_NUMBER
    %import common.WS
    %ignore WS

    """, start='value')

print(wdl_parser.parse('"abc"'))
print(wdl_parser.parse('13'))
print(wdl_parser.parse('13.3'))
print(wdl_parser.parse('true'))
print(wdl_parser.parse('false'))

from lark import Transformer

class WDLTransformer(Transformer):
    def string(self, v):
        return v[0][1:-1]
    def number(self, v):
        return float(v[0])

    true = lambda self, _: True
    false = lambda self, _: False

print(WDLTransformer().transform(wdl_parser.parse('13.1')))

