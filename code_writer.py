class CodeWriter:
    """Translates a parsed VM command into Hack assembly instructions."""
    
    def __init__(self, path):
        self.file = open(path, "w")
        
    def write_arithmetic(self, command):
        pass
        
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
    
