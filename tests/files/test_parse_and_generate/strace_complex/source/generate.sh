#!/bin/sh

# Script for generating strace.log from building real project

set -e

SCRIPT_DIR=`dirname "$0"`
ABS_SCRIPT_DIR=`realpath "$SCRIPT_DIR"`

SRC_DIR=$ABS_SCRIPT_DIR
BUILD_DIR=$ABS_SCRIPT_DIR/../build
OUT_DIR=$ABS_SCRIPT_DIR/..
TOOLCHAIN=Linux

rm -rf $BUILD_DIR
mkdir $BUILD_DIR


cd $BUILD_DIR

echo "Configuring..."
cmake $SRC_DIR

echo "Building..."
strace -f -e process,chdir -s 65535 -o strace.log make > build.log 2>&1

echo "Generating..."

../../../../../../bin/generate_cmake.sh \
    --project strace_test \
    --targets lib main \
    --log strace strace.log \
    --build_dirs $BUILD_DIR \
    --out_dir $OUT_DIR \
    --platform unix \
    --toolchain $TOOLCHAIN \
    $SRC_DIR > migrate.log 2>&1

echo "Done"

cd ..
