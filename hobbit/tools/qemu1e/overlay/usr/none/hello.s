TEXT main(SB), 1, $16
	MOV	$1, R4
	MOV	$hellomsg+0(SB), R8
	MOV	$9, R12
	CALL	write(SB)
	RETURN

DATA	hellomsg+0(SB), $"hello 1e"
DATA	hellomsg+8(SB), $"\n"
GLOBL	hellomsg+0(SB), $16
