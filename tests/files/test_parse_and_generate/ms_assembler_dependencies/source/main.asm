.386
.model flat, stdcall
option casemap :none

.data
	message db "Hello world!", 0

.code

%include f1.inc
include f2.inc

main_impl:
	mov si, word ptr [message]
	call print_string
end main_impl
