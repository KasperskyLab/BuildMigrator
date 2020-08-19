print_string:
  lodsb        ; grab a byte from SI
  or al, al  ; logical or AL by itself
  jz .done   ; if the result is zero, get out
  mov ah, 0x0E
  int 0x10      ; otherwise, print out the character!
  jmp print_string

.done:
   ret
