#include "file.h"
#include "c.h"

#ifndef MODE_C
#error MODE_C
#endif

#ifdef MODE_A
#error MODE_A
#endif

int c() { return s_b_c + s_c; }
