%include "file.inc"
%ifndef ASM
	%error ASM
%endif
%ifndef YASM
	%error YASM
%endif
%ifdef NASM
	%error NASM
%endif
%ifdef MASM
	%error MASM
%endif
