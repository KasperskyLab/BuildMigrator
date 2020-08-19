#include <stdio.h>

#include <openssl/crypto.h>
#include <openssl/rsa.h>
#include <openssl/evp.h>
#include <openssl/err.h>
#include <openssl/rand.h>
#include <openssl/ssl.h>

#ifdef _WIN32
#  include <Windows.h>
#  include <Wincrypt.h>
#endif
