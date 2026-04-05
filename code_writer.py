class CodeWriter:
    """Translates a parsed VM command into Hack assembly instructions."""
    
    def __init__(self, path):
        self.path = path
        self.file = open(path, "w")
        self.distinct = 0
        
    def write_arithmetic(self, command):
        debug = "// "+command+"\n"
        match command: # arithmetic-logical command -> asm instructions
            case "add":
                asm = debug + self.__pop_x_y() + "M=D+M\n" + "@SP\n" + "M=M+1\n"
            case "sub":
                asm = debug + "@SP\n" + "AM=M-1\n" + "D=M\n" + "@SP\n" + "AM=M-1\n" + "M=M-D\n" + "@SP\n" + "M=M+1\n"
            case "neg":
                asm = debug + "@SP\n" + "AM=M-1\n" + "M=-M\n" + "@SP\n" + "M=M+1\n"
            case "eq":
                asm = debug + self.__pop_x_y() + "D=M-D\n" + "M=-1\n" + "@TRUE"+str(self.distinct)+"\n" + "D;JEQ\n" + "@SP\n" + "A=M\n" + "M=0\n" + "(TRUE"+str(self.distinct)+")\n" + "@SP\n" + "M=M+1\n"
            case "gt":
                asm = debug + self.__pop_x_y() + "D=M-D\n" + "M=-1\n" + "@TRUE"+str(self.distinct)+"\n" + "D;JGT\n" + "@SP\n" + "A=M\n" + "M=0\n" + "(TRUE"+str(self.distinct)+")\n" + "@SP\n" + "M=M+1\n"
            case "lt":
                asm = debug + self.__pop_x_y() + "D=M-D\n" + "M=-1\n" + "@TRUE"+str(self.distinct)+"\n" + "D;JLT\n" + "@SP\n" + "A=M\n" + "M=0\n" + "(TRUE"+str(self.distinct)+")\n" + "@SP\n" + "M=M+1\n"
            case "and":
                asm = debug + self.__pop_x_y() + "M=D&M\n" + "@SP\n" + "M=M+1\n"
            case "or":
                asm = debug + self.__pop_x_y() + "M=D|M\n" + "@SP\n" + "M=M+1\n"
            case "not":
                asm = debug + "@SP\n" + "AM=M-1\n" + "M=!M\n" + "@SP\n" + "M=M+1\n"
                
        self.file.write(asm)
        self.distinct += 1
        
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
                asm = debug + "@"+index+"\n" + "D=A\n" + self.__push_to_stack()
                
            elif segment == "static":
                asm = debug + "@"+self.path[:-4]+".i"+"\n" + "D=A\n" + "@"+index+"\n" + "A=D+A\n" + "D=M\n" + self.__push_to_stack()
            
            elif segment == "temp" or segment == "pointer":
                asm = debug + "@"+mapped+"\n" + "D=A\n" + "@"+index+"\n" + "A=D+A\n" + "D=M\n" + self.__push_to_stack() 
                
            else:
                asm = debug + "@"+mapped+"\n" + "D=M\n" + "@"+index+"\n" + "A=D+A\n" + "D=M\n" + self.__push_to_stack()
                
        elif command == "C_POP": # pop segment index -> asm instructions
            debug = "// pop "+segment+" "+index+"\n"
            
            if segment == "static":
                asm = debug + self.__pop_from_stack() + "@"+self.path[:-4]+".i"+"\n" + "D=A\n" + "@"+index+"\n" + self.__store_in_segment()
            
            elif segment == "temp" or segment == "pointer":
                asm = debug + self.__pop_from_stack() + "@"+mapped+"\n" + "D=A\n" + "@"+index+"\n" + self.__store_in_segment()
            
            else:
                asm = debug + self.__pop_from_stack() + "@"+mapped+"\n" + "D=M\n" + "@"+index+"\n" + self.__store_in_segment()
                
        self.file.write(asm)
        
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
