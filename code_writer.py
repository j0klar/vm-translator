import os

class CodeWriter:
    """Generates and writes Hack assembly code to output file for a parsed VM command."""
    
    def __init__(self, path):
        self.filename = os.path.basename(path)[:-4]
        self.file = open(path, "w")
        self.function = ""
        self.distinct = 0
        self.call_count = 0
        self._bootstrap()
        
    def _bootstrap(self):
        self.file.write("// Initialize stack\n" + "@256\n" + "D=A\n" + "@SP\n" + "M=D\n")
        self.file.write("@$$START\n" + "0;JMP\n")
        self._emit_call_subroutine()
        self._emit_return_subroutine()
        self.file.write("($$START)\n")
        self.write_call("Sys.init", "0")
        
    def set_file(self, file):
        self.filename = file[:-3]
        
    def write_arithmetic(self, command):
        debug = "// "+command+"\n"
        match command: # arithmetic-logical command -> asm instructions
            case "add":
                asm = self._pop_x_y() + "M=D+M\n" + "@SP\n" + "M=M+1\n"
            case "sub":
                asm = "@SP\n" + "AM=M-1\n" + "D=M\n" + "@SP\n" + "AM=M-1\n" + "M=M-D\n" + "@SP\n" + "M=M+1\n"
            case "neg":
                asm = "@SP\n" + "AM=M-1\n" + "M=-M\n" + "@SP\n" + "M=M+1\n"
            case "eq":
                asm = self._pop_x_y() + "D=M-D\n" + "M=-1\n" + "@TRUE"+str(self.distinct)+"\n" + "D;JEQ\n" + "@SP\n" + "A=M\n" + "M=0\n" + "(TRUE"+str(self.distinct)+")\n" + "@SP\n" + "M=M+1\n"
                self.distinct += 1
            case "gt":
                asm = self._pop_x_y() + "D=M-D\n" + "M=-1\n" + "@TRUE"+str(self.distinct)+"\n" + "D;JGT\n" + "@SP\n" + "A=M\n" + "M=0\n" + "(TRUE"+str(self.distinct)+")\n" + "@SP\n" + "M=M+1\n"
                self.distinct += 1
            case "lt":
                asm = self._pop_x_y() + "D=M-D\n" + "M=-1\n" + "@TRUE"+str(self.distinct)+"\n" + "D;JLT\n" + "@SP\n" + "A=M\n" + "M=0\n" + "(TRUE"+str(self.distinct)+")\n" + "@SP\n" + "M=M+1\n"
                self.distinct += 1
            case "and":
                asm = self._pop_x_y() + "M=D&M\n" + "@SP\n" + "M=M+1\n"
            case "or":
                asm = self._pop_x_y() + "M=D|M\n" + "@SP\n" + "M=M+1\n"
            case "not":
                asm = "@SP\n" + "AM=M-1\n" + "M=!M\n" + "@SP\n" + "M=M+1\n"
            case _:
                asm = ""
                
        self.file.write(debug+asm)
        
    def _pop_x_y(self):
        return "@SP\n" + "AM=M-1\n" + "D=M\n" + "@SP\n" + "AM=M-1\n"
        
    def write_pushpop(self, command, segment, index):
        match segment:
            case "argument":
                mapped = "ARG"
            case "local":
                mapped = "LCL"
            case "this":
                mapped = "THIS"
            case "that":
                mapped = "THAT"
            case "temp":
                mapped = "5"
            case "pointer":
                mapped = "3"
                
        if command == "C_PUSH": # push segment index -> asm instructions
            debug = "// push "+segment+" "+index+"\n"
            
            if segment == "constant":
                if index == "0":
                    asm = "@SP\n" + "AM=M+1\n" + "A=A-1\n" + "M=0\n"
                elif index == "1":
                    asm = "@SP\n" + "AM=M+1\n" + "A=A-1\n" + "M=1\n"
                else:
                    asm = "@"+index+"\n" + "D=A\n" + self._push_to_stack()
                
            elif segment == "static":
                asm = "@"+self.filename+"."+index+"\n" + "D=M\n" + self._push_to_stack()
            
            elif segment == "temp" or segment == "pointer":
                addr = str(int(mapped) + int(index))
                asm = "@"+addr+"\n" + "D=M\n" + self._push_to_stack()
                
            else:
                asm = "@"+mapped+"\n" + "D=M\n" + "@"+index+"\n" + "A=D+A\n" + "D=M\n" + self._push_to_stack()
                
        elif command == "C_POP": # pop segment index -> asm instructions
            debug = "// pop "+segment+" "+index+"\n"
            
            if segment == "static":
                asm = "@SP\n" + "AM=M-1\n" + "D=M\n" + "@"+self.filename+"."+index+"\n" + "M=D\n"
            
            elif segment == "temp" or segment == "pointer":
                addr = str(int(mapped) + int(index))
                asm = "@SP\n" + "AM=M-1\n" + "D=M\n" + "@"+addr+"\n" + "M=D\n"
            
            else:
                asm = "@"+mapped+"\n" + "D=M\n" + "@"+index+"\n" + "D=D+A\n" + "@R13\n" + "M=D\n" + "@SP\n" + "AM=M-1\n" + "D=M\n" + "@R13\n" + "A=M\n" + "M=D\n"
                
        self.file.write(debug+asm)
        
    def write_label(self, label):
        debug = "// label "+label+"\n"
        asm = "("+self.function+"$"+label+")\n"
        self.file.write(debug+asm)
        
    def write_goto(self, label):
        debug = "// goto "+label+"\n"
        asm = "@"+self.function+"$"+label+"\n" + "0;JMP\n"
        self.file.write(debug+asm)
        
    def write_if(self, label):
        debug = "// if-goto "+label+"\n"
        asm = "@SP\n" + "AM=M-1\n" + "D=M\n" + "@"+self.function+"$"+label+"\n" + "D;JNE\n"
        self.file.write(debug+asm)
        
    def write_function(self, name, n_vars):
        debug = "// function "+name+" "+n_vars+"\n"
        asm = "("+name+")\n"
        if int(n_vars) > 0:
            asm += "@"+n_vars+"\n" + "D=A\n" + "("+name+"."+"LOOP)\n" + "@SP\n" + "A=M\n" + "M=0\n" + "@SP\n" + "M=M+1\n" + "D=D-1\n" + "@"+name+"."+"LOOP\n" + "D;JGT\n"
        self.file.write(debug+asm)
        self.function = name
        
    def write_call(self, name, n_args):
        debug = "// call "+name+" "+n_args+"\n"
        ret_label = name+"$ret."+str(self.call_count)
        asm = "@"+ret_label+"\n" + "D=A\n" + "@R13\n" + "M=D\n" + "@"+n_args+"\n" + "D=A\n" + "@R14\n" + "M=D\n" + "@"+name+"\n" + "D=A\n" + "@R15\n" + "M=D\n" + "@$$CALL\n" + "0;JMP\n" + "("+ret_label+")\n"
        self.call_count += 1
        self.file.write(debug+asm)
        
    def write_return(self):
        self.file.write("// return\n" + "@$$RETURN\n" + "0;JMP\n")
        
    def _emit_call_subroutine(self):
        self.file.write("// $$CALL bootstrap\n" + "($$CALL)\n" + "@R13\n" + "D=M\n" + self._push_to_stack() + self._save_pointer("LCL") + self._save_pointer("ARG") + self._save_pointer("THIS") + self._save_pointer("THAT") + "@SP\n" + "D=M\n" + "@5\n" + "D=D-A\n" + "@R14\n" + "D=D-M\n" + "@ARG\n" + "M=D\n" + "@SP\n" + "D=M\n" + "@LCL\n" + "M=D\n" + "@R15\n" + "A=M\n" + "0;JMP\n")

    def _emit_return_subroutine(self):
        self.file.write("// $$RETURN bootstrap\n" + "($$RETURN)\n" + "@LCL\n" + "D=M\n" + "@R13\n" + "M=D\n" + "@5\n" + "A=D-A\n" + "D=M\n" + "@R14\n" + "M=D\n" + "@SP\n" + "AM=M-1\n" + "D=M\n" + "@ARG\n" + "A=M\n" + "M=D\n" + "D=A\n" + "@SP\n" + "M=D+1\n" + self._restore_pointer("THAT") + self._restore_pointer("THIS") + self._restore_pointer("ARG") + self._restore_pointer("LCL") + "@R14\n" + "A=M\n" + "0;JMP\n")
        
    def _save_pointer(self, pointer):
        return "@"+pointer+"\n" + "D=M\n" + "@SP\n" + "A=M\n" + "M=D\n" + "@SP\n" + "M=M+1\n"
        
    def _restore_pointer(self, pointer):
        return "@R13\n" + "AM=M-1\n" + "D=M\n" + "@"+pointer+"\n" + "M=D\n"
        
    def _push_to_stack(self):
        return "@SP\n" + "A=M\n" + "M=D\n" + "@SP\n" + "M=M+1\n"
        
    def close(self):
        self.file.close()
