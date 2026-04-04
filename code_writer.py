class CodeWriter:
    """Translates a parsed VM command into Hack assembly instructions."""
    
    def __init__(self, path):
        self.file = open(path, "w")
        
    def write_arithmetic(self, command):
        match command: # arithmetic-logical command -> asm instructions
            case "add":
                asm = "@SP\n" + "AM=M-1\n" + "D=M\n" + "AM=M-1\n" + "M=D+M\n"
            case "sub":
                asm = "@SP\n" + "AM=M-1\n" + "D=M\n" + "AM=M-1\n" + "M=M-D\n"
            case "neg":
                asm = "@SP\n" + "AM=M-1\n" + "M=-M\n"
            case "eq":
                asm = "@SP\n" + "AM=M-1\n" + "D=M\n" + "AM=M-1\n" + "D=M-D\n" +
                      "M=-1\n" + "@true\n" + "D;JEQ\n" + "@SP\n" + "M=D\n" + "(true)\n"
            case "gt":
                asm = "@SP\n" + "AM=M-1\n" + "D=M\n" + "AM=M-1\n" + "D=M-D\n" +
                      "M=-1\n" + "@true\n" + "D;JGT\n" + "@SP\n" + "M=D\n" + "(true)\n"
            case "lt":
                asm = "@SP\n" + "AM=M-1\n" + "D=M\n" + "AM=M-1\n" + "D=M-D\n" +
                      "M=-1\n" + "@true\n" + "D;JLT\n" + "@SP\n" + "M=D\n" + "(true)\n"
            case "and":
                asm = "@SP\n" + "AM=M-1\n" + "D=M\n" + "AM=M-1\n" + "M=D&M\n"
            case "or":
                asm = "@SP\n" + "AM=M-1\n" + "D=M\n" + "AM=M-1\n" + "M=D|M\n"
            case "not":
                asm = "@SP\n" + "AM=M-1\n" + "M=!M\n"
                
        self.file.write(asm)
        
    def write_pushpop(self, command, segment, index):
        if command "push": # push segment index -> asm instructions
            asm = "@"+segment+"\n" + "D=A\n" + "@"+index+"\n" + "A=D+A\n" + 
                  "D=M\n" + "@SP\n" + "A=M\n" + "M=D\n" + "@SP\n" + "M=M+1\n"
        elif command = "pop": # pop segment index -> asm instructions
            asm = "@SP\n" + "AM=M-1\n" + "D=M\n" + "@R13\n" + "M=D" +
                  "@"+segment+"\n" + "D=A\n" + "@"+index+"\n" + "D=D+A\n" + 
                  "@R14\n" + "M=D\n" + "@R13\n" + "D=M\n" + "@R14\n" + 
                  "A=M\n" + "M=D\n"
                  
        self.file.write(asm)
        
    def close(self):
        self.file.close()
    
