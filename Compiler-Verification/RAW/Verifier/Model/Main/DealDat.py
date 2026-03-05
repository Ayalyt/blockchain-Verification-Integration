from ..Setting import ModelingSettings
import struct
from typing import Union, List, Dict, Any


def decode_frelement(rec: bytes, P: int, R_inv: int) -> int:
    if len(rec) != 40:
        raise ValueError(f"Expected 40 bytes, got {len(rec)}")
    short_val = int.from_bytes(rec[0:4], "little", signed=True)
    flags     = int.from_bytes(rec[4:8], "little", signed=False)
    is_long   = bool(flags & (1 << 31))
    is_mont   = bool(flags & (1 << 30))
    long_val  = int.from_bytes(rec[8:40], "little", signed=False)

    if is_mont:
        value = (long_val * R_inv) % P
        if is_long:
            return value
        else:
            assert value == short_val % P
            return value
    else:
        if is_long:
            return long_val
        else:
            return short_val % P


def deal_dat(dat_path: str,
             hash_num: int,
             witness_num: int,
             constant_num: int,
             io_map_size: int,
             P: int, R_inv: int) -> list[int]:
    """
    precisely simulating the C++ mmap/memcpy order and sizes, read three segments from the beginning of the file in order:
      1) InputHashMap:   hash_num * sizeof(HashSignalInfo)
      2) witness list:   witness_num * sizeof(u64) * Witness_u64_count
      3) circuitConstants: constant_num * sizeof(FrElement)
    """

    with open(dat_path, "rb") as f:
        b = f.read()

    # 1) HashSignalInfo[] 
    d_hash_bytes = hash_num * ModelingSettings.HashSignalInfo_Size
    if len(b) < d_hash_bytes:
        raise ValueError("file too short to read hash section")
    off = d_hash_bytes

    # 2) witness2SignalList segment (C++ does new u64[get_size_of_witness()])
    d_witness_bytes = witness_num * ModelingSettings.Witness_size
    if len(b) < off + d_witness_bytes:
        raise ValueError("file too short to read witness section")
    off += d_witness_bytes

    # 3) circuitConstants parsing(FrElement is 40 bytes in little-endian)
    d_const_bytes = constant_num * ModelingSettings.FrElement_size
    if len(b) < off + d_const_bytes:
        raise ValueError("file too short to read constants section")
    const_region = b[off: off + d_const_bytes]

    tail = b[off + d_const_bytes:] 

    constants = []
    for i in range(constant_num):
        rec = const_region[i * ModelingSettings.FrElement_size: (i + 1) * ModelingSettings.FrElement_size]
        constants.append(decode_frelement(rec, P, R_inv))

    templateInsId2IOSignalInfo = parse_template_ins_io_map(tail, io_map_size)

    return constants, templateInsId2IOSignalInfo


def parse_template_ins_io_map(tail_bytes, io_map_size: int):
    """
    extracting the templateInsId2IOSignalInfo from the tail bytes of .dat file.
    args:
      - tail_bytes: the raw bytes (bytes/bytearray) of this section, or
                    or a list of int (0-255) equivalent to bytes
      - io_map_size: the value of get_size_of_io_map() (i.e., number of elements in index)
    returns:
      - dict: { templateInsId(int): [ {offset:int, len:int, lengths:List[int], total_length:int}, ... ] }
    notes:
      - all parsed as little-endian u32
      - layout = index[io_map_size] (u32 each) + N records concatenated:
             record: n(u32) + n times of entries [ offset(u32), len(u32), lengths[len](u32[]) ]
    """
    if isinstance(tail_bytes, list):
        tail_bytes = bytes(tail_bytes)
    if not isinstance(tail_bytes, (bytes, bytearray)):
        raise TypeError("tail_bytes must be bytes/bytearray or list of int")
    

    def read_u32_le(buf: bytes, pos: int) -> int:
        if pos + 4 > len(buf):
            raise ValueError("cannot read u32, buffer too small")
        return struct.unpack_from("<I", buf, pos)[0]

    expected_index_bytes = io_map_size * 4
    if len(tail_bytes) < expected_index_bytes:
        raise ValueError("too short to read index array")

    index_vals = []
    pos = 0
    for _ in range(io_map_size):
        index_vals.append(read_u32_le(tail_bytes, pos))
        pos += 4

    # print(f"DEBUG: Parsed template_ids from dat file are: {index_vals}")

    data = tail_bytes[pos:]
    pos = 0
    result = dict()

    for i in range(io_map_size):
        if pos + 4 > len(data):
            raise ValueError(f"record {i}: cannot read n")
        n = read_u32_le(data, pos)
        pos += 4

        defs = []
        for _ in range(n):
            if pos + 8 > len(data):
                raise ValueError(f"record {i}: cannot read offset/len")
            offset = read_u32_le(data, pos)
            length_count = read_u32_le(data, pos + 4)
            pos += 8

            lengths = []
            if length_count > 0:
                need = length_count * 4
                if pos + need > len(data):
                    raise ValueError(f"record {i}: cannot read lengths[{length_count}]")
                lengths = []
                need = length_count * 4
                if pos + need > len(data):
                    raise ValueError(f"record {i}: cannot read lengths[{length_count}]")
                cur = pos
                end = pos + need
                while cur < end:
                    lengths.append(int.from_bytes(data[cur:cur + 4], "little"))
                    cur += 4
                pos = end

            if ModelingSettings.old_version():
                defs.append({
                    "offset": offset,
                    "len": length_count,
                    "lengths": lengths,
                    # "total_length": sum(lengths) if lengths else 0
                })
            else:
                if pos + 8 > len(data):
                    raise ValueError(f"record {i}: cannot read size/busId")
                size = read_u32_le(data, pos)
                bus_id = read_u32_le(data, pos + 4)
                pos += 8
                defs.append({
                    "offset": offset,
                    "len": length_count,
                    "lengths": lengths,
                    "size": size,
                    "bus_id": bus_id
                })

        template_ins_id = index_vals[i]
        result[template_ins_id] = {'len': n, 'defs': defs}
        # print(f"Template Instance ID {template_ins_id}: {n} IODef(s)")

    if pos != len(data):
        raise ValueError(f"unexpected trailing bytes after parsing: {len(data) - pos} bytes")

    return result
