#if defined(__ARM_ARCH_ISA_A64)
#	include "arm64.h"
#elif defined(__ARM_ARCH_7S__)
#	include "armv7s.h"
#elif defined(__ARM_ARCH_7A__)
#	include "armv7.h"
#else
#	error "Unknown architecture"
#endif


int main(){}
