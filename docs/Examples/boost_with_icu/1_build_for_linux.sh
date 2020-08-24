#!/bin/sh

set -e

SOURCE_DIR=$1
ICU_BUILD_DIR=$2

build_migrator --commands build \
    --source_dir "$SOURCE_DIR" \
    --build_command "{source_dir}/bootstrap.sh" "{source_dir}" \
    --build_command "{source_dir}/b2 --without-python --without-math address-model=64 architecture=x86 --build-dir=b --stagedir=stage variant=release link=static library-path=$ICU_BUILD_DIR/lib -sICU_PATH=$ICU_BUILD_DIR -sboost.locale.icu=on stage -q -j8 -d+2" "{source_dir}" \
    --presets autotools darwin \
    --verbose
