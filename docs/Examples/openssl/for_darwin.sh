#!/bin/sh

set -e

SOURCE_DIR=$1

build_migrator --build_command "{source_dir}/config" \
    --build_command make \
    --source_dir "$SOURCE_DIR" \
    --presets autotools darwin \
    --aggressive_optimization \
    --targets libcrypto.a libcrypto.dylib libssl.a libssl.dylib \
              apps/openssl test/asn1_decode_test test/x509_time_test \
    --verbose
