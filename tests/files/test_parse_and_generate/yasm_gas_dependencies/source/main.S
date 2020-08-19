%include "functions.S"

.text
.global _main_impl

_main_impl:
  MessageStr:
    .ascii "Hello, World!"
  mov MessageStr, %si
  call print_string
