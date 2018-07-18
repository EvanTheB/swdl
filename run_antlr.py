import sys
from antlr4 import *
from wdlLexer import wdlLexer
from wdlParser import wdlParser

def main(argv):
    input = InputStream(argv[1])
    lexer = wdlLexer(input)
    stream = CommonTokenStream(lexer)
    # print(stream)
    parser = wdlParser(stream)
    tree = parser.type_()

    print(tree.toStringTree(recog=parser))

if __name__ == '__main__':
    main(sys.argv)
