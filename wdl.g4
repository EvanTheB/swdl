grammar wdl;
WS: [ \t\f\r\n]+ -> skip ;

/* src: https://github.com/lark-parser/lark/blob/master/lark/grammars/common.lark */

DIGIT: '0'..'9' ;
INT: DIGIT+ ;
SIGNED_INT: ('+'|'-')? INT ;

DECIMAL: INT '.' INT? | '.' INT ;
EXP: ('e'|'E') SIGNED_INT ;
FLOAT: INT EXP | DECIMAL EXP? ;
SIGNED_FLOAT: ['+'|'-'] FLOAT ;

NUMBER: FLOAT | INT ;
SIGNED_NUMBER: ['+'|'-'] NUMBER ;

LCASE_LETTER: 'a'..'z' ;
UCASE_LETTER: 'A'..'Z' ;

LETTER: UCASE_LETTER | LCASE_LETTER ;
WORD: LETTER+ ;

CNAME: ('_'|LETTER) ('_'|LETTER|DIGIT)* ;

WS_INLINE: [ \t]+ ;

TYPE_INT: 'Int' ;
TYPE_FLOAT: 'Float' ;
TYPE_BOOLEAN: 'Boolean' ;
TYPE_STRING: 'String' ;
TYPE_FILE: 'File' ;
type_: TYPE_INT | TYPE_FLOAT | TYPE_BOOLEAN | TYPE_STRING | TYPE_FILE | 'Array' '[' type_ ']' | 'Map' '[' type_ ',' type_ ']' ;

workflow: 'workflow' CNAME '{' input_block? workflow_block* output_block? '}' ;
workflow_block: declaration | call | scatter ;
task: 'task' CNAME '{' input_block? declaration* command declaration* runtime? declaration* output_block? '}' ;

input_block: 'input' '{' opt_declaration* '}' ;
output_block: 'output' '{' declaration* '}' ;

call: 'call' CNAME ( '{' 'input' '{' variable_mapping* '}' '}' )? ;
variable_mapping: CNAME '=' expression ;

scatter: 'scatter' '(' CNAME 'in' expression ')' '{' workflow_block* '}' ;

runtime: 'runtime' '{' variable_mapping* '}' ;

opt_declaration: type_ CNAME ( '=' expression )? ;
declaration: type_ CNAME '=' expression ;

expression: or_expr
          | 'if' or_expr 'then' or_expr 'else' or_expr ;
or_expr  : and_expr
         | and_expr ('||' and_expr)+ ;
and_expr : eq_expr
         | eq_expr ('&&' eq_expr)+ ;
eq_expr  : cmp_expr
          | cmp_expr '!=' cmp_expr
          | cmp_expr '==' cmp_expr ;
cmp_expr : add_expr
          | add_expr '>=' add_expr
          | add_expr '>' add_expr
          | add_expr '<=' add_expr
          | add_expr '<' add_expr ;
add_expr : mul_expr
          | mul_expr ('-' mul_expr)+
          | mul_expr ('+' mul_expr)+ ;
mul_expr : unary_expr
          | unary_expr ('/' unary_expr)+
          | unary_expr ('%' unary_expr)+
          | unary_expr ('*' unary_expr)+ ;
unary_expr: func_expr
          | '-' func_expr
          | '!' func_expr ;
func_expr : index_expr
          | CNAME '(' (index_expr ( ',' index_expr )*)? ')' ;
index_expr: dot_expr
          | dot_expr '[' dot_expr ']' ;
dot_expr  : paren_expr
          | paren_expr '.' CNAME ;
paren_expr: literal
          | '(' expression ')' ;

literal: CNAME
       | string
       | SIGNED_INT
       | SIGNED_FLOAT
       | 'true'
       | 'false'
       | '{' ( expression ':' expression ( ',' expression ':' expression )*)? '}'
       | '[' ( expression ( ',' expression )*)? ']' ;

string: '"' string_part* '"' ;
string_part: actual_string
           | '~{' expression '}' ;
actual_string: 'abc' ; /*( ~["~]+ | '~'+ ~[{] )+ ;*/

command: 'command' '<<<' command_part* '>>>' ;
command_part: 'abc' ;
/*
command_part: /[^>~]+/
            | '~{' expression '}'
            | /~(?!{)/
            | />(?!>>)/ ;
*/


