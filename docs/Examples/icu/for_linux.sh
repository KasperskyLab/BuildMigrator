#!/bin/sh

set -e

SOURCE_DIR=$1

build_migrator --build_command "{source_dir}/configure --enable-static --enable-shared=no --enable-tests=no --enable-samples=no  --enable-dyload=no" \
    --build_command "make VERBOSE=1" \
    --project icu \
    --source_dir "$SOURCE_DIR" \
    --presets autotools linux icu \
    --targets "lib/*.a" "stubdata/*.a" \
    --aggressive_optimization \
    --delete_flags "^-DU_BUILD=" "^-DU_HOST=" "^-DU_CC=" "^-DU_CXX=" \
    --verbose
