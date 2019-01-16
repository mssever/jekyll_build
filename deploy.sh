#!/bin/bash

set -e  # exit if any command returns nonzero

build_dir="$1"; shift
source="$1"; shift
"${build_dir}/deploy.py" "$source" "$@"
exit $?
