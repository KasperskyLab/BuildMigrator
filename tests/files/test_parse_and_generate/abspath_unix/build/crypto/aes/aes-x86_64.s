.text	
.type	_x86_64_AES_encrypt,@function
.align	16
_x86_64_AES_encrypt:
	xorl	0(%r15),%eax
	xorl	4(%r15),%ebx
	xorl	8(%r15),%ecx
	xorl	12(%r15),%edx

	movl	240(%r15),%r13d
	subl	$1,%r13d
	jmp	.Lenc_loop