#!/bin/bash
### This script isn't intended to be run directly. Use build.py.

set -e  # exit if any command returns nonzero
mode=$1; shift
build_dir="$1"; shift
bundle exec jekyll "$mode" "$@"
exit $?
