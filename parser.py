class Parser:
    """Parses a single .vm-file into push/pop and arithmetic-logical commands."""
    
    def __init__(self, file):
        self.line_count = 0
        self.instr = None
        self.vm = []
        
        with open(file) as stream:
            for line in stream.read().split("\n"):
                line = line.split("//")[0].strip()
                if line:
                    self.vm.append(line)
        
    def more_lines(self):
        return self.line_count < len(self.vm)
        
    def advance(self):
        self.instr = self.vm[self.line_count]
        self.line_count += 1
        
    def command_type(self):
        operator = self.instr.split()[0]
        if operator == "push":
            return "C_PUSH"
        elif operator == "pop":
            return "C_POP"
        else:
            return "C_ARITHMETIC" 
        
    def arg1(self):
        cmd = self.instr.split()[0]
        if cmd == "push" or cmd == "pop":
            return self.instr.split()[1]
        else:
            return cmd
        
    def arg2(self):
        return self.instr.split()[2]
