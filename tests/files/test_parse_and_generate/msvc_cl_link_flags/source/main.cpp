#include "a.h"
#include "b.h"

#include <Windows.h>


int main()
{
    a();
    b();
    return 1;
}

BOOL WINAPI DllMain(HINSTANCE, DWORD, LPVOID)
{
    main();
    return TRUE;
}
