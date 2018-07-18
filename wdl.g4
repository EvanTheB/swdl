grammar wdl;

type_: TYPE_INT | TYPE_FLOAT | TYPE_BOOLEAN | TYPE_STRING | TYPE_FILE | 'Array' '[' type_ ']' | 'Map' '[' type_ ',' type_ ']' ;
TYPE_INT: 'Int' ;
TYPE_FLOAT: 'Float' ;
TYPE_BOOLEAN: 'Boolean' ;
TYPE_STRING: 'String' ;
TYPE_FILE: 'File' ;
