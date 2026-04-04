class CodeWriter:
    """Translates a parsed VM command into Hack assembly instructions."""
    
    def __init__(self, path):
        self.file = open(path, "w")
        
    def write_arithmetic(self, command):
        asm = "// "+command+"\n"
        match command: # arithmetic-logical command -> asm instructions
            case "add":
                asm = asm + "@SP\n" + "AM=M-1\n" + "D=M\n" + "AM=M-1\n" + "M=D+M\n"
            case "sub":
                asm = asm + "@SP\n" + "AM=M-1\n" + "D=M\n" + "AM=M-1\n" + "M=M-D\n"
            case "neg":
                asm = asm + "@SP\n" + "AM=M-1\n" + "M=-M\n"
            case "eq":
                asm = asm + "@SP\n" + "AM=M-1\n" + "D=M\n" + "AM=M-1\n" + "D=M-D\n" + "M=-1\n" + "@true\n" + "D;JEQ\n" + "@SP\n" + "M=D\n" + "(true)\n"
            case "gt":
                asm = asm + "@SP\n" + "AM=M-1\n" + "D=M\n" + "AM=M-1\n" + "D=M-D\n" + "M=-1\n" + "@true\n" + "D;JGT\n" + "@SP\n" + "M=D\n" + "(true)\n"
            case "lt":
                asm = asm + "@SP\n" + "AM=M-1\n" + "D=M\n" + "AM=M-1\n" + "D=M-D\n" + "M=-1\n" + "@true\n" + "D;JLT\n" + "@SP\n" + "M=D\n" + "(true)\n"
            case "and":
                asm = asm + "@SP\n" + "AM=M-1\n" + "D=M\n" + "AM=M-1\n" + "M=D&M\n"
            case "or":
                asm = asm + "@SP\n" + "AM=M-1\n" + "D=M\n" + "AM=M-1\n" + "M=D|M\n"
            case "not":
                asm = asm + "@SP\n" + "AM=M-1\n" + "M=!M\n"
                
        self.file.write(asm)
        
    def write_pushpop(self, command, segment, index):
        if command == "C_PUSH": # push segment index -> asm instructions
            asm = "// push "+segment+" "+index+"\n" + "@"+segment+"\n" + "D=A\n" + "@"+index+"\n" + "A=D+A\n" + "D=M\n" + "@SP\n" + "A=M\n" + "M=D\n" + "@SP\n" + "M=M+1\n"
        elif command == "C_POP": # pop segment index -> asm instructions
            asm = "// pop "+segment+" "+index+"\n" + "@SP\n" + "AM=M-1\n" + "D=M\n" + "@R13\n" + "M=D\n" + "@"+segment+"\n" + "D=A\n" + "@"+index+"\n" + "D=D+A\n" + "@R14\n" + "M=D\n" + "@R13\n" + "D=M\n" + "@R14\n" + "A=M\n" + "M=D\n"
        self.file.write(asm)
        
    def close(self):
        self.file.close()
    
