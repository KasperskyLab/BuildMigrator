SECTION .text

%include 'f1.inc'
%include "f2.inc"

global _main_impl

_main_impl:
  MessageStr db MSG, 0
  mov esi, MessageStr
  call print_string
