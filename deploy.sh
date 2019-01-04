#!/bin/bash

set -e  # exit if any command returns nonzero

build_dir="$1"; shift
bundle exec octopress deploy
