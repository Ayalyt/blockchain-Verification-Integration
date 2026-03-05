# RSA Verifier Circuit for OutDID's verifier

This is a fork of the [double-bilnd](https://github.com/doubleblind-xyz/double-blind/). What we're solely interested in is the RSA Verifier circuit as part of their solution. This fork applies a very lightweight patch over the original repository, namely:
- In `rsa.circom`, we changed the `base_len` variable to 408. This corresponds to the RSA-SHA-256 digest variant. The original version supports RSA-SHA-512. 
- In `rsa.circom`, `bigint.circom`, and `fp.circom`, we change all imports to `circomlib` circuits to point to the same copy of `circomlib` as our main OutDID verifier circuit. This is important because circom doesn't allow the same circuit to be loaded from two separate files, so we need to have one `circomlib` copy per project. 
