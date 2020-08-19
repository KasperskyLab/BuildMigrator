@echo off

set "SOURCE_DIR=%1"

build_migrator --build_command "perl {source_dir}/Configure VC-WIN64A" ^
    --build_command "nmake /U" ^
    --source_dir "%SOURCE_DIR%" ^
    --presets autotools windows ^
    --aggressive_optimization ^
    --targets libcrypto_static.lib libcrypto-1_1-x64.dll ^
             libssl_static.lib libssl-1_1-x64.dll ^
             apps/openssl.exe test/asn1_decode_test.exe test/x509_time_test.exe ^
    --verbose
