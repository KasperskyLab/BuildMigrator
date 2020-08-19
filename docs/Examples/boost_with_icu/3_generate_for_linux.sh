#!/bin/sh

set -e

build_migrator --commands optimize generate --aggressive_optimization \
               --default_var_value ICU_INCLUDE_DIRS "" \
               --project boost \
               --flat_build_dir \
               --verbose
