#!/bin/bash
### This script isn't intended to be run directly. Use build.py.

set -e  # exit if any command returns nonzero
build_dir="$1"; shift
minify_options="$1"; shift
#builtin cd "${0%/*}" # The dir this script lives in. See https://stackoverflow.com/q/6393551/713735
"${build_dir}/minify_html_js.py" _site $minify_options "$@"
exit $?
