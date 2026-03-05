import struct
from typing import Optional, Dict

class R1CSError(Exception):
    pass

def parse_r1cs_header(path: str, modulus_int: Optional[int] = None) -> Dict[str, int]:
    """
    解析 Circom 生成的 .r1cs 文件头与 HEADER section，返回关键信息。
    - path: .r1cs 文件路径
    - modulus_int: 可选，编译时所选的大素数（十进制 int）。若提供，将与文件中的模数做一致性校验。

    返回字典包含：
      magic, version, num_sections,
      field_size, total_wires, public_inputs, public_outputs, private_inputs,
      number_of_labels, number_of_constraints, n_public_signals
    """
    with open(path, "rb") as f:
        # 顶层文件头：magic(4) | version(4) | num_sections(u32le)
        magic = f.read(4)
        if magic != b"r1cs":
            raise R1CSError(f"Bad magic: {magic!r}, expected b'r1cs'")
        version = struct.unpack("<I", f.read(4))[0]
        num_sections = struct.unpack("<I", f.read(4))[0]

        header_payload = None

        # 逐个 section 读取：type(u32le) | size(u64le) | payload
        for _ in range(num_sections):
            sec_type = struct.unpack("<I", f.read(4))[0]
            sec_size = struct.unpack("<Q", f.read(8))[0]
            payload = f.read(sec_size)

            # HEADER section 的 type = 1
            if sec_type == 1:
                header_payload = payload

        if header_payload is None:
            raise R1CSError("HEADER section (type=1) not found.")

        # 解析 HEADER payload：
        # [4] field_size (u32)
        # [N] field_modulus (N=field_size, little-endian, 非定长大整数)
        # [4] total_wires
        # [4] public_outputs
        # [4] public_inputs
        # [4] private_inputs
        # [8] number_of_labels (u64)
        # [4] number_of_constraints
        off = 0
        field_size = struct.unpack_from("<I", header_payload, off)[0]; off += 4

        field_mod_bytes = header_payload[off:off+field_size]; off += field_size
        # 小端字节转整数
        field_modulus = int.from_bytes(field_mod_bytes, "little")

        total_wires = struct.unpack_from("<I", header_payload, off)[0]; off += 4
        public_outputs = struct.unpack_from("<I", header_payload, off)[0]; off += 4
        public_inputs = struct.unpack_from("<I", header_payload, off)[0]; off += 4
        private_inputs = struct.unpack_from("<I", header_payload, off)[0]; off += 4
        number_of_labels = struct.unpack_from("<Q", header_payload, off)[0]; off += 8
        number_of_constraints = struct.unpack_from("<I", header_payload, off)[0]; off += 4

        # 可选：校验传入的模数是否与文件一致
        if modulus_int is not None and modulus_int != field_modulus:
            raise R1CSError("Provided modulus does not match R1CS header modulus.")

        n_public_signals = public_inputs + public_outputs

        return {
            "magic": magic.decode(),
            "version": version,
            "num_sections": num_sections,
            "field_size": field_size,
            "field_modulus": field_modulus,  # 十进制 int
            "total_wires": total_wires,
            "public_inputs": public_inputs,
            "public_outputs": public_outputs,
            "private_inputs": private_inputs,
            "number_of_labels": number_of_labels,
            "number_of_constraints": number_of_constraints,
            "n_public_signals": n_public_signals,
        }

# —— 示例 ——
# info = parse_r1cs_header("circuit.r1cs", modulus_int=21888242871839275222246405745257275088548364400416034343698204186575808495617)
# print(info)

if __name__ == '__main__':
    prime = 21888242871839275222246405745257275088548364400416034343698204186575808495617
    R1CS_path = '/home/zeno/Desktop/BlockChain/OurTools/Compiler-Verification/RAW/Verifier/temp_file/Public/Public.r1cs'
    outcome = parse_r1cs_header(R1CS_path, prime)

    print(outcome)