#include "functions.S"

.text 
.global main_impl

main_impl:
  MessageStr:
    .ascii "Hello, World!"
  mov MessageStr, %si
  call print_string
