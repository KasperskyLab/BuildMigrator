print_string:
	lodsb        ; grab a byte from SI
	or al, al  ; logical or AL by itself
	jz done   ; if the result is zero, get out
	mov ah, 0eh
	int 10h      ; otherwise, print out the character!
	jmp print_string
