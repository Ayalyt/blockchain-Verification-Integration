#!/bin/bash

script_path=$(realpath "$0")
script_dir=$(dirname "$script_path")

cd "$script_dir"

json_header_folder=$(realpath "../lib/json/single_include")
zksnark_folder=$(realpath "../lib/snarkjs")

mkdir -p ./4/temp_output
../assets/circom-202/target/release/circom ./4/temp.circom --r1cs --wasm --sym --c --output ./4/temp_output
cd ./4/temp_output/temp_cpp
CPLUS_INCLUDE_PATH="$json_header_folder" make
./temp ../../input.json ./a.wtns
cd ../temp_js
node generate_witness.js temp.wasm ../../input.json ./b.wtns
cd "$zksnark_folder"
pnpm exec snarkjs wej ../../cases/4/temp_output/temp_cpp/a.wtns 0.json
pnpm exec snarkjs wej ../../cases/4/temp_output/temp_js/b.wtns 1.json
echo '-----------------------'
echo inputFile:
cat "$script_dir"/4/input.json ; echo
echo '<<<<' 0.json
cat 0.json ; echo
echo
echo '<<<<' 1.json
cat 1.json ; echo
