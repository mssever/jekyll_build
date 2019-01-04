#!/bin/bash
### This script isn't intended to be run directly. Use build.py.

set -e  # exit if any command returns nonzero
build_dir="$1"
bundle exec jekyll clean
exit $?
