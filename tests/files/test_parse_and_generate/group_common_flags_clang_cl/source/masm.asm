%include file.inc
ifndef ASM
	.err ASM
endif
ifndef MASM
	.err MASM
endif
ifdef NASM
	.err NASM
endif
ifdef YASM
	.err YASM
endif

.386
.model  small
.safeseh    handler

_text SEGMENT
handler PROC
   ret
handler ENDP
_text ENDS

end