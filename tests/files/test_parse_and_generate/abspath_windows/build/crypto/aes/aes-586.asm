%ifidn __OUTPUT_FORMAT__,obj
section	code	use32 class=code align=64
%elifidn __OUTPUT_FORMAT__,win32
$@feat.00 equ 1
section	.text	code align=64
%else
section	.text	code
%endif
align	16
__x86_AES_encrypt_compact:
	mov	DWORD [20+esp],edi
	xor	eax,DWORD [edi]
	xor	ebx,DWORD [4+edi]
	xor	ecx,DWORD [8+edi]
	xor	edx,DWORD [12+edi]
	mov	esi,DWORD [240+edi]
	lea	esi,[esi*1+esi-2]
	lea	esi,[esi*8+edi]
	mov	DWORD [24+esp],esi
	mov	edi,DWORD [ebp-128]
	mov	esi,DWORD [ebp-96]
	mov	edi,DWORD [ebp-64]
	mov	esi,DWORD [ebp-32]
	mov	edi,DWORD [ebp]
	mov	esi,DWORD [32+ebp]
	mov	edi,DWORD [64+ebp]
	mov	esi,DWORD [96+ebp]
