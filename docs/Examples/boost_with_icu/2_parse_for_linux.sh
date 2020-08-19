#!/bin/sh

set -e

SOURCE_DIR=$1
ICU_BUILD_DIR=$2

build_migrator --commands parse \
    --build_dirs $SOURCE_DIR/b/boost/bin.v2/libs \
    --targets "*.a" \
    --working_dir "$SOURCE_DIR" \
    --replace_line "compile-c-c\+\+ " "" \
    --path_alias "$ICU_BUILD_DIR/include" "@ICU_INCLUDE_DIRS@" \
    --verbose
