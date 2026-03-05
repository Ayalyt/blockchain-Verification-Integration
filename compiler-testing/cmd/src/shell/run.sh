#!/bin/bash

script_path=$(realpath "$0")
script_dir=$(dirname "$script_path")

cd "$script_dir"
../../../bin/tbcctfiw --config $1 --mode $2
