%include "file.inc"
%ifndef ASM
	%error ASM
%endif
%ifndef NASM
	%error NASM
%endif
%ifdef YASM
	%error YASM
%endif
%ifdef MASM
	%error MASM
%endif
