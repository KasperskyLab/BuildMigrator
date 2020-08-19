%include 'functions.inc'

global _main_impl

_main_impl:
  MessageStr db MSG, 0
  mov si, MessageStr
  call print_string
