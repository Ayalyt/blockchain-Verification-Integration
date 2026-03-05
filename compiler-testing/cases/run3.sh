#!/bin/bash

script_path=$(realpath "$0")
script_dir=$(dirname "$script_path")

cd "$script_dir"
json_header_folder=$(realpath "../lib/json/single_include")
zksnark_folder=$(realpath "../lib/snarkjs")

echo "$json_header_folder"

mkdir -p ./3/1/temp_output
mkdir -p ./3/2/temp_output
../assets/circom-218/target/release/circom ./3/temp1.circom --r1cs --wasm --sym --c --output ./3/1/temp_output
../assets/circom-218/target/release/circom ./3/temp2.circom --r1cs --wasm --sym --c --output ./3/2/temp_output
cd ./3/1/temp_output/temp1_cpp
CPLUS_INCLUDE_PATH="$json_header_folder" make
./temp1 ../../../input.json ./a.wtns
cd ../temp1_js
node generate_witness.js temp1.wasm ../../../input.json ./b.wtns
cd ../../../2/temp_output/temp2_cpp
CPLUS_INCLUDE_PATH="$json_header_folder" make
./temp2 ../../../input.json ./a.wtns
cd ../temp2_js
node generate_witness.js temp2.wasm ../../../input.json ./b.wtns
cd "$zksnark_folder"
pnpm exec snarkjs wej ../../cases/3/1/temp_output/temp1_cpp/a.wtns 00.json
pnpm exec snarkjs wej ../../cases/3/1/temp_output/temp1_js/b.wtns 01.json
pnpm exec snarkjs wej ../../cases/3/2/temp_output/temp2_cpp/a.wtns 10.json
pnpm exec snarkjs wej ../../cases/3/2/temp_output/temp2_js/b.wtns 11.json
echo '-----------------------'
echo inputFile:
cat "$script_dir"/3/input.json ; echo
echo '<<<<' 00.json
cat 00.json ; echo
echo
echo '<<<<' 01.json
cat 01.json ; echo
echo '<<<<' 10.json
cat 10.json ; echo
echo '<<<<' 11.json
cat 11.json ; echo
