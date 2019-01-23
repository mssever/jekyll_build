#!/bin/bash
### This script isn't intended to be run directly. Use build.py.

set -e  # exit if any command returns nonzero
build_dir="$1"
if [[ $JEKYLL_BUILD_VERBOSITY == -1 ]]; then
    bundle exec jekyll clean >/dev/null
else
    bundle exec jekyll clean
fi
exit $?
