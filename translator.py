"""Translates a single correct .vm-file into a correct .asm-file."""

from parser import Parser
from code_writer import CodeWriter
import sys

def main():
    file_in = sys.argv[1]
    parser = Parser(file_in)
    code_writer = CodeWriter(file_in[:-3]+".asm")
    
    while parser.more_lines():
        parser.advance()
        if parser.command_type() == "C_PUSH" or parser.command_type() == "C_POP":
            code_writer.write_pushpop(parser.command_type(), parser.arg1(), parser.arg2())
        elif parser.command_type() == "C_ARITHMETIC":
            code_writer.write_arithmetic(parser.arg1())
    
    code_writer.close()
    
if __name__ == "__main__":
    main()

