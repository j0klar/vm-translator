import os

class CodeWriter:
    """Translates a parsed VM command into Hack assembly instructions."""
    
    def __init__(self, path):
        self.filename = os.path.basename(path)[:-4]
        self.file = open(path, "w")
        self.function = ""
        self.distinct = 0
        
    def write_arithmetic(self, command):
        debug = "// "+command+"\n"
        match command: # arithmetic-logical command -> asm instructions
            case "add":
                asm = self.__pop_x_y() + "M=D+M\n" + "@SP\n" + "M=M+1\n"
            case "sub":
                asm = "@SP\n" + "AM=M-1\n" + "D=M\n" + "@SP\n" + "AM=M-1\n" + "M=M-D\n" + "@SP\n" + "M=M+1\n"
            case "neg":
                asm = "@SP\n" + "AM=M-1\n" + "M=-M\n" + "@SP\n" + "M=M+1\n"
            case "eq":
                asm = self.__pop_x_y() + "D=M-D\n" + "M=-1\n" + "@TRUE"+str(self.distinct)+"\n" + "D;JEQ\n" + "@SP\n" + "A=M\n" + "M=0\n" + "(TRUE"+str(self.distinct)+")\n" + "@SP\n" + "M=M+1\n"
                self.distinct += 1
            case "gt":
                asm = self.__pop_x_y() + "D=M-D\n" + "M=-1\n" + "@TRUE"+str(self.distinct)+"\n" + "D;JGT\n" + "@SP\n" + "A=M\n" + "M=0\n" + "(TRUE"+str(self.distinct)+")\n" + "@SP\n" + "M=M+1\n"
                self.distinct += 1
            case "lt":
                asm = self.__pop_x_y() + "D=M-D\n" + "M=-1\n" + "@TRUE"+str(self.distinct)+"\n" + "D;JLT\n" + "@SP\n" + "A=M\n" + "M=0\n" + "(TRUE"+str(self.distinct)+")\n" + "@SP\n" + "M=M+1\n"
                self.distinct += 1
            case "and":
                asm = self.__pop_x_y() + "M=D&M\n" + "@SP\n" + "M=M+1\n"
            case "or":
                asm = self.__pop_x_y() + "M=D|M\n" + "@SP\n" + "M=M+1\n"
            case "not":
                asm = "@SP\n" + "AM=M-1\n" + "M=!M\n" + "@SP\n" + "M=M+1\n"
                
        self.file.write(debug+asm)
        
    def __pop_x_y(self):
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
                asm = "@"+index+"\n" + "D=A\n" + self.__push_to_stack()
                
            elif segment == "static":
                asm = "@"+self.filename+"."+index+"\n" + "D=M\n" + self.__push_to_stack()
            
            elif segment == "temp" or segment == "pointer":
                asm = "@"+mapped+"\n" + "D=A\n" + "@"+index+"\n" + "A=D+A\n" + "D=M\n" + self.__push_to_stack() 
                
            else:
                asm = "@"+mapped+"\n" + "D=M\n" + "@"+index+"\n" + "A=D+A\n" + "D=M\n" + self.__push_to_stack()
                
        elif command == "C_POP": # pop segment index -> asm instructions
            debug = "// pop "+segment+" "+index+"\n"
            
            if segment == "static":
                asm = "@SP\n" + "AM=M-1\n" + "D=M\n" + "@"+self.filename+"."+index+"\n" + "M=D\n"
            
            elif segment == "temp" or segment == "pointer":
                asm = self.__pop_from_stack() + "@"+mapped+"\n" + "D=A\n" + "@"+index+"\n" + self.__store_in_segment()
            
            else:
                asm = self.__pop_from_stack() + "@"+mapped+"\n" + "D=M\n" + "@"+index+"\n" + self.__store_in_segment()
                
        self.file.write(debug+asm)
        
    def write_label(self, label):
        debug = "// "+"label "+label+"\n"
        asm = "("+self.function+"$"+label+")\n"
        self.file.write(debug+asm)
        
    def write_goto(self, label):
        debug = "// "+"goto "+label+"\n"
        asm = "@"+self.function+"$"+label+"\n" + "0;JMP\n"
        self.file.write(debug+asm)
        
    def write_if(self, label):
        debug = "// "+"if-goto "+label+"\n"
        asm = "@SP\n" + "AM=M-1\n" + "D=M\n" + "@"+self.function+"$"+label+"\n" + "D;JNE\n"
        self.file.write(debug+asm)
        
    def write_function(self, name, nVars):
        debug = "// "+"function "+name+" "+nVars+"\n"
        asm = "("+name+")\n" + "@"+nVars+"\n" + "D=A\n" + "("+name+"."+"LOOP)\n" + "@SP\n" + "A=M\n" + "M=0\n" + "@SP\n" + "M=M+1\n" + "D=D-1\n" + "@"+name+"."+"LOOP\n" + "D;JGT\n"
        self.file.write(debug+asm)
        self.function = name
        
    def write_return(self):
        debug = "// return\n"
        asm = "@LCL\n" + "D=M\n" + "@R13\n" + "M=D\n" + "@5\n" + "A=D-A\n" + "D=M\n" + "@R14\n" + "M=D\n" + "@SP\n" + "AM=M-1\n" + "D=M\n" + "@ARG\n" + "A=M\n" + "M=D\n" + "D=A\n" + "@SP\n" + "M=D+1\n" + self.__restore_pointer("THAT") + self.__restore_pointer("THIS") + self.__restore_pointer("ARG") + self.__restore_pointer("LCL") + "@R14\n" + "A=M\n" + "0;JMP\n"
        self.file.write(debug+asm)
    
    def write_call(self, name, nArgs):
        pass
        
    def __restore_pointer(self, pointer):
        return "@R13\n" + "AM=M-1\n" + "D=M\n" + "@"+pointer+"\n" + "M=D\n"
        
    def __push_to_stack(self):
        return "@SP\n" + "A=M\n" + "M=D\n" + "@SP\n" + "M=M+1\n"
    
    def __pop_from_stack(self):
        return "@SP\n" + "AM=M-1\n" + "D=M\n" + "@R13\n" + "M=D\n"
        
    def __store_in_segment(self):
        return  "D=D+A\n" + "@R14\n" + "M=D\n" + "@R13\n" + "D=M\n" + "@R14\n" + "A=M\n" + "M=D\n"
        
    def end_program(self):
        self.file.write("// end program\n" + "(END)\n" + "@END\n" + "0;JMP")
        
    def close(self):
        self.file.close()
