from lark import Lark

wdl_parser = Lark(r"""
    ?doc: task* workflow task*

    workflow: "workflow" "{" input? (declaration|call)* output? "}"
    task: "task" "{" input? declaration* command declaration* output? "}"

    input: "input" "{" opt_declaration* "}"
    output: "output" "{" declaration* "}"

    call: "call" NAME [ "{" "input:" variable_mapping* "}" ]
    variable_mapping: NAME "=" expression

    command: "command" /<<<.*?>>>/s
    
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
        | "[" expression* "]"
        | literal
        | NAME

    type: actual_type "?"?
    
    actual_type: "Int"    -> type_int
        | "Float"  -> type_float
        | "Boolean"  -> type_boolean
        | "String"  -> type_string
        | "File"  -> type_file
        | "Array" "[" type "]" "+"? -> type_array
        | "Map" "[" type "," type "]" "+"? -> type_map



    literal:  string
          | SIGNED_NUMBER      -> number
          | "true"             -> true
          | "false"            -> false


    string : ESCAPED_STRING

    %import common.ESCAPED_STRING
    %import common.SIGNED_NUMBER
    %import common.CNAME -> NAME
    %import common.WS
    %ignore WS

    """, start='doc', ambiguity="explicit")

print(wdl_parser.parse(r'''workflow { input { Int abc } }''').pretty())
print(wdl_parser.parse(r'''workflow { input { String abc = 1 } }''').pretty())

print(wdl_parser.parse(r'''workflow { input { String abc = 1 }
    Int abc = false
    call xyz
    Int abc = def
    call xyz {input: a = "a"}
 }''').pretty())

print(wdl_parser.parse(r'''workflow {}
task {
    command <<< >>>
}
task {
    command <<<
    xyz abc

    xyz abc
    >>>
}
    ''').pretty())

print(wdl_parser.parse(r'''workflow {}
task {
    command <<< > >> >>>
}''').pretty())


from lark import Transformer

class WDLTransformer(Transformer):
    def string(self, v):
        return v[0][1:-1]
    def number(self, v):
        return float(v[0])

    true = lambda self, _: True
    false = lambda self, _: False

#print(WDLTransformer().transform(wdl_parser.parse('13.1')))

