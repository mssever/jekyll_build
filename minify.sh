#!/bin/bash
### This script isn't intended to be run directly. Use build.py.

set -e  # exit if any command returns nonzero
build_dir="$1"; shift
minify_options="$1"; shift
"${build_dir}/minify_html_js.py" _site $minify_options "$@"
exit $?
