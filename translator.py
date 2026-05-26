"""Translates one or more correct .vm-files into a single correct .asm-file."""

from parser import Parser
from code_writer import CodeWriter
import sys, os

def main():
    path_in = sys.argv[1]
    
    if os.path.isfile(path_in):
        code_writer = CodeWriter(path_in[:-3]+".asm")
        parser = Parser(path_in)
        _parse_file(parser, code_writer)
        
    elif os.path.isdir(path_in):
        if path_in.endswith("/"):
            path_in = path_in[:-1]
        code_writer = CodeWriter(path_in+".asm")
        vm_files = []
        for file in os.listdir(path_in):
            if file.endswith(".vm"):
                vm_files.append(file)
        
        if "Sys.vm" in vm_files:
            vm_files.remove("Sys.vm")
            vm_files.insert(0, "Sys.vm")
            
        for file in vm_files:
            code_writer.set_file(file)
            parser = Parser(os.path.join(path_in, file))
            _parse_file(parser, code_writer)
            
    code_writer.close()

def _parse_file(parser, code_writer):
    while parser.more_lines():
        parser.advance()
        if parser.command_type() == "C_PUSH" or parser.command_type() == "C_POP":
            code_writer.write_pushpop(parser.command_type(), parser.arg1(), parser.arg2())
        elif parser.command_type() == "C_ARITHMETIC":
            code_writer.write_arithmetic(parser.arg1())
        elif parser.command_type() == "C_LABEL":
            code_writer.write_label(parser.arg1())
        elif parser.command_type() == "C_GOTO":
            code_writer.write_goto(parser.arg1())
        elif parser.command_type() == "C_IF":
            code_writer.write_if(parser.arg1())
        elif parser.command_type() == "C_FUNCTION":
            code_writer.write_function(parser.arg1(), parser.arg2())
        elif parser.command_type() == "C_RETURN":
            code_writer.write_return()
        elif parser.command_type() == "C_CALL":
            code_writer.write_call(parser.arg1(), parser.arg2())
    
if __name__ == "__main__":
    main()
