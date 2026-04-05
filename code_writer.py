class CodeWriter:
    """Translates a parsed VM command into Hack assembly instructions."""
    
    def __init__(self, path):
        self.path = path
        self.file = open(path, "w")
        
    def write_arithmetic(self, command):
        asm = "// "+command+"\n"
        match command: # arithmetic-logical command -> asm instructions
            case "add":
                asm = asm + "@SP\n" + "AM=M-1\n" + "D=M\n" + "@SP\n" + "AM=M-1\n" + "M=D+M\n" + "@SP\n" + "M=M+1\n"
            case "sub":
                asm = asm + "@SP\n" + "AM=M-1\n" + "D=M\n" + "@SP\n" + "AM=M-1\n" + "M=M-D\n" + "@SP\n" + "M=M+1\n"
            case "neg":
                asm = asm + "@SP\n" + "AM=M-1\n" + "M=-M\n" + "@SP\n" + "M=M+1\n"
            case "eq":
                asm = asm + "@SP\n" + "AM=M-1\n" + "D=M\n" + "@SP\n" + "AM=M-1\n" + "D=M-D\n" + "M=-1\n" + "@TRUE\n" + "D;JEQ\n" + "@SP\n" + "A=M\n" + "M=0\n" + "(TRUE)\n" + "@SP\n" + "M=M+1\n"
            case "gt":
                asm = asm + "@SP\n" + "AM=M-1\n" + "D=M\n" + "@SP\n" + "AM=M-1\n" + "D=M-D\n" + "M=-1\n" + "@TRUE\n" + "D;JGT\n" + "@SP\n" + "A=M\n" + "M=0\n" + "(TRUE)\n" + "@SP\n" + "M=M+1\n"
            case "lt":
                asm = asm + "@SP\n" + "AM=M-1\n" + "D=M\n" + "@SP\n" + "AM=M-1\n" + "D=M-D\n" + "M=-1\n" + "@TRUE\n" + "D;JLT\n" + "@SP\n" + "A=M\n" + "M=0\n" + "(TRUE)\n" + "@SP\n" + "M=M+1\n"
            case "and":
                asm = asm + "@SP\n" + "AM=M-1\n" + "D=M\n" + "@SP\n" + "AM=M-1\n" + "M=D&M\n" + "@SP\n" + "M=M+1\n"
            case "or":
                asm = asm + "@SP\n" + "AM=M-1\n" + "D=M\n" + "@SP\n" + "AM=M-1\n" + "M=D|M\n" + "@SP\n" + "M=M+1\n"
            case "not":
                asm = asm + "@SP\n" + "AM=M-1\n" + "M=!M\n" + "@SP\n" + "M=M+1\n"
                
        self.file.write(asm)
        
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
            case "pointer":
                mapped = "3"
            case "temp":
                mapped = "5"
                
        if command == "C_PUSH": # push segment index -> asm instructions
            asm = "// push "+segment+" "+index+"\n"
            if segment == "constant":
                asm = asm + "@"+index+"\n" + "D=A\n" + "@SP\n" + "A=M\n" + "M=D\n" + "@SP\n" + "M=M+1\n"
            elif segment == "static":
                asm = asm + "@"+path[:-4]+".i"+"\n" + "D=A\n" + "@"+index+"\n" + "A=D+A\n" + "D=M\n" + "@SP\n" + "A=M\n" + "M=D\n" + "@SP\n" + "M=M+1\n"
            else:
                asm = asm + "@"+mapped+"\n" + "D=M\n" + "@"+index+"\n" + "A=D+A\n" + "D=M\n" + "@SP\n" + "A=M\n" + "M=D\n" + "@SP\n" + "M=M+1\n"
                
        elif command == "C_POP": # pop segment index -> asm instructions
            asm = "// pop "+segment+" "+index+"\n"
            if segment == "static":
                asm = asm + "@SP\n" + "AM=M-1\n" + "D=M\n" + "@R13\n" + "M=D\n" + "@"+mapped+"\n" + "D=M\n" + "@"+index+"\n" + "D=D+A\n" + "@R14\n" + "M=D\n" + "@R13\n" + "D=M\n" + "@R14\n" + "A=M\n" + "M=D\n"
            else:
                asm = asm + "@SP\n" + "AM=M-1\n" + "D=M\n" + "@R13\n" + "M=D\n" + "@"+path[:-4]+".i"+"\n" + "D=A\n" + "@"+index+"\n" + "D=D+A\n" + "@R14\n" + "M=D\n" + "@R13\n" + "D=M\n" + "@R14\n" + "A=M\n" + "M=D\n"
                
        self.file.write(asm)
        
    def end_program(self):
        self.file.write("// end program\n" + "(END)\n" + "@END\n" + "0;JMP")
        
    def close(self):
        self.file.close()
    
