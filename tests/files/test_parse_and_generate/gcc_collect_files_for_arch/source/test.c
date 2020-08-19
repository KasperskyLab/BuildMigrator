#if defined(__x86_64__)
#	include "x86_64.h"
#elif defined(__i386__)
#	include "i386.h"
#else
#	error "Unknown architecture"
#endif


int main(){}
