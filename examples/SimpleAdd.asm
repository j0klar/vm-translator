// push constant 7
@constant
D=A
@7
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
// push constant 8
@constant
D=A
@8
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
// add
@SP
AM=M-1
D=M
AM=M-1
M=D+M
