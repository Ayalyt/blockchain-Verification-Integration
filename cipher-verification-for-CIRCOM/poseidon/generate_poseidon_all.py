#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import re
import argparse


# 有限域素数 (BN254)
PRIME = 21888242871839275222246405745257275088548364400416034343698204186575808495617

# 轮数常量
NROUNDSF = 8
NROUNDSP = [56, 57, 56, 60, 60, 63, 64, 63, 60, 66, 60, 65, 70, 60, 64, 68]

def hex_to_decimal(hex_string):
    """
    将十六进制字符串转换为十进制整数
   
    参数:
        hex_string (str): 十六进制字符串，可以以0x开头或不以0x开头
       
    返回:
        int: 转换后的十进制整数
    """
    # 去除可能的前缀和空格
    hex_string = hex_string.strip('[]').lower()
   
    if hex_string.startswith('0x'):
        hex_string = hex_string[2:]
   
    # 验证输入是否为有效的十六进制数
    if not all(c in '0123456789abcdef' for c in hex_string):
        raise ValueError(f"输入包含非十六进制字符: {hex_string}")
   
    # 转换为十进制
    decimal_value = int(hex_string, 16)
    return decimal_value

def parse_poseidon_constants(file_content):
    """
    解析Poseidon常数文件，提取C、M、P、S常数
    返回包含这些常数的字典
    """
    constants_dict = {}
    m_dict = {}
    p_dict = {}
    s_dict = {}
   
    # 辅助函数：解析数组字符串
    def parse_array(array_str):
        cleaned = re.sub(r'//.*', '', array_str)  # 移除注释
        cleaned = re.sub(r'\s+', '', cleaned)  # 移除空白
        if cleaned.startswith('[') and cleaned.endswith(']'):
            cleaned = cleaned[1:-1]
        return [item for item in cleaned.split(',') if item]
   
    # 解析POSEIDON_C
    c_pattern = r'function\s+POSEIDON_C\s*\(t\)\s*\{([\s\S]*?)^\}'
    c_match = re.search(c_pattern, file_content, re.DOTALL | re.MULTILINE)
    if c_match:
        c_content = c_match.group(1)
        t_blocks = re.findall(
            r'(?:if|else\s+if)\s*\(t\s*==\s*(\d+)\)\s*\{[^}]*?return\s*(\[[\s\S]*?\])\s*;',
            c_content,
            re.DOTALL
        )
        for t_val, array_str in t_blocks:
            constants_dict[t_val] = parse_array(array_str)
   
    # 解析POSEIDON_M
    m_pattern = r'function\s+POSEIDON_M\s*\(t\)\s*\{([\s\S]*?)^\}'
    m_match = re.search(m_pattern, file_content, re.DOTALL | re.MULTILINE)
    if m_match:
        m_content = m_match.group(1)
        t_blocks = re.findall(
            r'(?:if|else\s+if)\s*\(t\s*==\s*(\d+)\)\s*\{[^}]*?return\s*(\[[\s\S]*?\])\s*;',
            m_content,
            re.DOTALL
        )
        for t_val, matrix_str in t_blocks:
            rows = re.findall(r'\[([^\]]+)\]', matrix_str)
            matrix = []
            for row in rows:
                if re.search(r'\w', row):
                    matrix.append(parse_array(row))
            m_dict[t_val] = matrix
   
    # 解析POSEIDON_P
    p_pattern = r'function\s+POSEIDON_P\s*\(t\)\s*\{([\s\S]*?)^\}'
    p_match = re.search(p_pattern, file_content, re.DOTALL | re.MULTILINE)
    if p_match:
        p_content = p_match.group(1)
        t_blocks = re.findall(
            r'(?:if|else\s+if)\s*\(t\s*==\s*(\d+)\)\s*\{[^}]*?return\s*(\[[\s\S]*?\])\s*;',
            p_content,
            re.DOTALL
        )
        for t_val, matrix_str in t_blocks:
            rows = re.findall(r'\[([^\]]+)\]', matrix_str)
            matrix = []
            for row in rows:
                if re.search(r'\w', row):
                    matrix.append(parse_array(row))
            p_dict[t_val] = matrix
   
    # 解析POSEIDON_S
    s_pattern = r'function\s+POSEIDON_S\s*\(t\)\s*\{([\s\S]*?)^\}'
    s_match = re.search(s_pattern, file_content, re.DOTALL | re.MULTILINE)
    if s_match:
        s_content = s_match.group(1)
        t_blocks = re.findall(
            r'(?:if|else\s+if)\s*\(t\s*==\s*(\d+)\)\s*\{[^}]*?return\s*(\[[\s\S]*?\])\s*;',
            s_content,
            re.DOTALL
        )
        for t_val, array_str in t_blocks:
            s_dict[t_val] = parse_array(array_str)
   
    return constants_dict, m_dict, p_dict, s_dict

def load_constants_from_file(file_path, t):
    """
    从文件中加载Poseidon常数并转换为十进制
   
    参数:
        file_path (str): 包含Poseidon常数的文件路径
        t (int): 状态大小 (nInputs + 1)
       
    返回:
        tuple: (C_list, M_matrix, P_matrix, S_list) 的十进制表示
    """
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except Exception as e:
        raise ValueError(f"无法读取文件 {file_path}: {str(e)}")
   
    # 解析常数
    c_dict, m_dict, p_dict, s_dict = parse_poseidon_constants(content)
   
    # 获取对应t的常数
    t_str = str(t)
    if t_str not in c_dict:
        raise ValueError(f"文件中没有找到t={t}的C常数")
    if t_str not in m_dict:
        raise ValueError(f"文件中没有找到t={t}的M常数")
    if t_str not in p_dict:
        raise ValueError(f"文件中没有找到t={t}的P常数")
    if t_str not in s_dict:
        raise ValueError(f"文件中没有找到t={t}的S常数")
   
    # 转换为十进制
    C_list = [hex_to_decimal(hex_str) for hex_str in c_dict[t_str]]
    S_list = [hex_to_decimal(hex_str) for hex_str in s_dict[t_str]]
   
    M_matrix = []
    for row in m_dict[t_str]:
        M_matrix.append([hex_to_decimal(hex_str) for hex_str in row])
   
    P_matrix = []
    for row in p_dict[t_str]:
        P_matrix.append([hex_to_decimal(hex_str) for hex_str in row])
   
    return C_list, M_matrix, P_matrix, S_list

def generate_poseidon_smtlib(nInputs=1, nOuts=1, constants_file=None):
    """
    生成 Poseidon 哈希电路在 nInputs=1 时的 SMT-LIB 表示
   
    参数:
        nInputs (int): 输入数量
        nOuts (int): 输出数量
        constants_file (str): 包含Poseidon常数的文件路径
       
    返回:
        str: SMT-LIB 代码
    """
    # 基础参数
    t = nInputs + 1
    nRoundsF = NROUNDSF
    nRoundsP = NROUNDSP[t-2] if t-2 < len(NROUNDSP) else 56  # 默认值
   
    # 加载常数
    if constants_file:
        try:
            C_list, M_matrix, P_matrix, S_list = load_constants_from_file(constants_file, t)
        except Exception as e:
            print(f"警告: 无法从文件加载常数: {str(e)}，使用默认值")
            # 使用默认值
            C_list = [i+1000 for i in range(72)]
            S_list = [i+2000 for i in range(168)]
            M_matrix = [[3000 + i*t + j for j in range(t)] for i in range(t)]
            P_matrix = [[4000 + i*t + j for j in range(t)] for i in range(t)]
    else:
        # 使用默认值
        C_list = [i+1000 for i in range(72)]
        S_list = [i+2000 for i in range(168)]
        M_matrix = [[3000 + i*t + j for j in range(t)] for i in range(t)]
        P_matrix = [[4000 + i*t + j for j in range(t)] for i in range(t)]
   
    # 输出 SMT-LIB 代码
    smtlib = []
   
    # 头部信息
    smtlib.append("; Poseidon Hash (nInputs={}) with Finite Field Arithmetic".format(nInputs))
    smtlib.append("(set-logic QF_FF)")
    smtlib.append("(set-option :produce-models true)")
    smtlib.append("")
   
    # 定义有限域
    smtlib.append("; 定义有限域 - 使用 BN254 曲线的域素数")
    smtlib.append("(define-sort F () (_ FiniteField {}))".format(PRIME))
    smtlib.append("")
   
    # 声明输入和输出变量
    smtlib.append("; 声明输入和输出变量")
    for i in range(nInputs):
        smtlib.append("(declare-const input_{} F)".format(i))
    smtlib.append("(declare-const initialState F)")
    for i in range(nOuts):
        smtlib.append("(declare-const output_{} F)".format(i))
    smtlib.append("")
   
    # 添加 C 常量
    smtlib.append("; 声明 C 常量")
    for i, c_val in enumerate(C_list):
        smtlib.append("(define-const C_{} F (as ff{} F))".format(i, c_val))
   
    smtlib.append("")
   
    # 添加 S 常量
    smtlib.append("; 声明 S 常量")
    for i, s_val in enumerate(S_list):
        smtlib.append("(define-const S_{} F (as ff{} F))".format(i, s_val))
   
    smtlib.append("")
   
    # 添加 M 矩阵常量
    smtlib.append("; M 矩阵")
    for i in range(t):
        for j in range(t):
            smtlib.append("(define-const M_{}_{} F (as ff{} F))".format(i, j, M_matrix[i][j]))
   
    smtlib.append("")
   
    # 添加 P 矩阵常量
    smtlib.append("; P 矩阵")
    for i in range(t):
        for j in range(t):
            smtlib.append("(define-const P_{}_{} F (as ff{} F))".format(i, j, P_matrix[i][j]))
   
    smtlib.append("")
   
    # 声明中间变量
    smtlib.append("; 声明中间变量")
   
    # 初始状态
    for j in range(t):
        smtlib.append("(declare-const ark_0_out_{} F)".format(j))
   
    smtlib.append("")
   
    # 全轮处理变量
    for r in range(nRoundsF):
        # Sigma 变换变量
        for j in range(t):
            smtlib.append("(declare-const sigmaF_{}_{}_in F)".format(r, j))
            smtlib.append("(declare-const sigmaF_{}_{}_in2 F)".format(r, j))
            smtlib.append("(declare-const sigmaF_{}_{}_in4 F)".format(r, j))
            smtlib.append("(declare-const sigmaF_{}_{}_out F)".format(r, j))
       
        # Ark 变换变量
        if r < nRoundsF - 1:
            for j in range(t):
                smtlib.append("(declare-const ark_{}_in_{} F)".format(r+1, j))
                smtlib.append("(declare-const ark_{}_out_{} F)".format(r+1, j))
       
        # Mix 变换变量
        if r < nRoundsF - 1:
            for j in range(t):
                smtlib.append("(declare-const mix_{}_in_{} F)".format(r, j))
            for j in range(t):
                smtlib.append("(declare-const mix_{}_out_{} F)".format(r, j))
   
    smtlib.append("")
   
    # 部分轮处理变量
    for r in range(nRoundsP):
        smtlib.append("(declare-const sigmaP_{}_in F)".format(r))
        smtlib.append("(declare-const sigmaP_{}_in2 F)".format(r))
        smtlib.append("(declare-const sigmaP_{}_in4 F)".format(r))
        smtlib.append("(declare-const sigmaP_{}_out F)".format(r))
       
        for j in range(t):
            smtlib.append("(declare-const mixS_{}_in_{} F)".format(r, j))
        for j in range(t):
            smtlib.append("(declare-const mixS_{}_out_{} F)".format(r, j))
   
    smtlib.append("")
   
    # MixLast 变量
    for j in range(t):
        smtlib.append("(declare-const mixLast_in_{} F)".format(j))
    for j in range(nOuts):
        smtlib.append("(declare-const mixLast_out_{} F)".format(j))
    smtlib.append("")
   
    # 初始状态设置（包含第一轮ARK操作）
    smtlib.append("; 初始状态设置（包含第一轮ARK操作）")
    smtlib.append("(assert (= ark_0_out_0 (ff.add initialState C_0)))")
    for i in range(nInputs):
        smtlib.append("(assert (= ark_0_out_{} (ff.add input_{} C_{})))".format(i+1, i, i+1))
    smtlib.append("")
   
    # 全轮前半处理
    smtlib.append("; 全轮前半处理")
    for r in range(nRoundsF // 2):
        # Sigma 变换
        for j in range(t):
            if r == 0:
                smtlib.append("(assert (= sigmaF_{}_{}_in ark_0_out_{}))".format(r, j, j))
            else:
                smtlib.append("(assert (= sigmaF_{}_{}_in mix_{}_out_{}))".format(r, j, r-1, j))
           
            smtlib.append("(assert (= sigmaF_{}_{}_in2 (ff.mul sigmaF_{}_{}_in sigmaF_{}_{}_in)))".format(r, j, r, j, r, j))
            smtlib.append("(assert (= sigmaF_{}_{}_in4 (ff.mul sigmaF_{}_{}_in2 sigmaF_{}_{}_in2)))".format(r, j, r, j, r, j))
            smtlib.append("(assert (= sigmaF_{}_{}_out (ff.mul sigmaF_{}_{}_in4 sigmaF_{}_{}_in)))".format(r, j, r, j, r, j))
       
        # Ark 变换
        if r < nRoundsF // 2 - 1:
            for j in range(t):
                smtlib.append("(assert (= ark_{}_in_{} sigmaF_{}_{}_out))".format(r+1, j, r, j))
                smtlib.append("(assert (= ark_{}_out_{} (ff.add ark_{}_in_{} C_{})))".format(
                    r+1, j, r+1, j, (r+1)*t + j))
           
            # Mix 变换 (使用 M 矩阵)
            for j in range(t):
                smtlib.append("(assert (= mix_{}_in_{} ark_{}_out_{}))".format(r, j, r+1, j))
           
            for i in range(t):
                terms = []
                for j in range(t):
                    terms.append("(ff.mul M_{}_{} mix_{}_in_{})".format(j, i, r, j))
                smtlib.append("(assert (= mix_{}_out_{} (ff.add {})))".format(
                    r, i, " ".join(terms)))
       
        # 全轮前半最后一轮
        elif r == nRoundsF // 2 - 1:
            for j in range(t):
                smtlib.append("(assert (= ark_{}_in_{} sigmaF_{}_{}_out))".format(r+1, j, r, j))
                smtlib.append("(assert (= ark_{}_out_{} (ff.add ark_{}_in_{} C_{})))".format(
                    r+1, j, r+1, j, (r+1)*t + j))
           
            # Mix 变换 (使用 P 矩阵)
            for j in range(t):
                smtlib.append("(assert (= mix_{}_in_{} ark_{}_out_{}))".format(r, j, r+1, j))
           
            for i in range(t):
                terms = []
                for j in range(t):
                    terms.append("(ff.mul P_{}_{} mix_{}_in_{})".format(j, i, r, j))
                smtlib.append("(assert (= mix_{}_out_{} (ff.add {})))".format(
                    r, i, " ".join(terms)))
       
        smtlib.append("")
   
    # 部分轮处理
    smtlib.append("; 部分轮处理")
    for r in range(nRoundsP):
        # Sigma 变换 (仅对第一个元素)
        if r == 0:
            smtlib.append("(assert (= sigmaP_{}_in mix_{}_out_0))".format(r, nRoundsF//2 - 1))
        else:
            smtlib.append("(assert (= sigmaP_{}_in mixS_{}_out_0))".format(r, r-1))
       
        smtlib.append("(assert (= sigmaP_{}_in2 (ff.mul sigmaP_{}_in sigmaP_{}_in)))".format(r, r, r))
        smtlib.append("(assert (= sigmaP_{}_in4 (ff.mul sigmaP_{}_in2 sigmaP_{}_in2)))".format(r, r, r))
        smtlib.append("(assert (= sigmaP_{}_out (ff.mul sigmaP_{}_in4 sigmaP_{}_in)))".format(r, r, r))
       
        # MixS 变换
        if r == 0:
            smtlib.append("(assert (= mixS_{}_in_0 (ff.add sigmaP_{}_out C_{})))".format(
                r, r, (nRoundsF//2+1)*t + r))
            for j in range(1, t):
                smtlib.append("(assert (= mixS_{}_in_{} mix_{}_out_{}))".format(r, j, nRoundsF//2 - 1, j))
        else:
            smtlib.append("(assert (= mixS_{}_in_0 (ff.add sigmaP_{}_out C_{})))".format(
                r, r, (nRoundsF//2+1)*t + r))
            for j in range(1, t):
                smtlib.append("(assert (= mixS_{}_in_{} mixS_{}_out_{}))".format(r, j, r-1, j))
       
        # MixS 输出计算
        terms = []
        for j in range(t):
            terms.append("(ff.mul S_{} mixS_{}_in_{})".format((t*2-1)*r + j, r, j))
        smtlib.append("(assert (= mixS_{}_out_0 (ff.add {})))".format(r, " ".join(terms)))
       
        for j in range(1, t):
            smtlib.append("(assert (= mixS_{}_out_{} (ff.add mixS_{}_in_{} (ff.mul mixS_{}_in_0 S_{}))))".format(
                r, j, r, j, r, (t*2-1)*r + t + j - 1))
       
        smtlib.append("")
   
    # 全轮后半处理
    smtlib.append("; 全轮后半处理")
    for r in range(nRoundsF // 2, nRoundsF):
        # Sigma 变换
        for j in range(t):
            if r == nRoundsF // 2:
                smtlib.append("(assert (= sigmaF_{}_{}_in mixS_{}_out_{}))".format(r, j, nRoundsP-1, j))
            else:
                smtlib.append("(assert (= sigmaF_{}_{}_in mix_{}_out_{}))".format(r, j, r-1, j))
           
            smtlib.append("(assert (= sigmaF_{}_{}_in2 (ff.mul sigmaF_{}_{}_in sigmaF_{}_{}_in)))".format(r, j, r, j, r, j))
            smtlib.append("(assert (= sigmaF_{}_{}_in4 (ff.mul sigmaF_{}_{}_in2 sigmaF_{}_{}_in2)))".format(r, j, r, j, r, j))
            smtlib.append("(assert (= sigmaF_{}_{}_out (ff.mul sigmaF_{}_{}_in4 sigmaF_{}_{}_in)))".format(r, j, r, j, r, j))
       
        # Ark 变换
        if r < nRoundsF - 1:
            for j in range(t):
                smtlib.append("(assert (= ark_{}_in_{} sigmaF_{}_{}_out))".format(r+1, j, r, j))
                smtlib.append("(assert (= ark_{}_out_{} (ff.add ark_{}_in_{} C_{})))".format(
                    r+1, j, r+1, j, (nRoundsF//2)*t + nRoundsP + (r+1 - nRoundsF//2)*t + j))
           
            # Mix 变换 (使用 M 矩阵)
            for j in range(t):
                smtlib.append("(assert (= mix_{}_in_{} ark_{}_out_{}))".format(r, j, r+1, j))
           
            for i in range(t):
                terms = []
                for j in range(t):
                    terms.append("(ff.mul M_{}_{} mix_{}_in_{})".format(j, i, r, j))
                smtlib.append("(assert (= mix_{}_out_{} (ff.add {})))".format(
                    r, i, " ".join(terms)))
       
        smtlib.append("")
   
    # 最终输出
    smtlib.append("; 最终输出")
    for j in range(t):
        smtlib.append("(assert (= mixLast_in_{} sigmaF_{}_{}_out))".format(j, nRoundsF-1, j))
   
    for i in range(nOuts):
        terms = []
        for j in range(t):
            terms.append("(ff.mul M_{}_{} mixLast_in_{})".format(j, i, j))
        smtlib.append("(assert (= mixLast_out_{} (ff.add {})))".format(i, " ".join(terms)))
        smtlib.append("(assert (= output_{} mixLast_out_{}))".format(i, i))
   
    smtlib.append("")
   
    # 验证特定输入输出的哈希值
    '''
    smtlib.append("; 验证特定输入输出的哈希值")
    smtlib.append("(assert (= initialState (as ff0 F)))")
    for i in range(nInputs):
        smtlib.append("(assert (= input_{} (as ff{} F)))".format(i, 42+i))
    for i in range(nOuts):
        smtlib.append("(assert (= output_{} (as ff{} F)))".format(i, 123456789+i))
    smtlib.append("")
    '''
    # 检查可满足性并获取模型
    smtlib.append("(check-sat)")
    smtlib.append("(get-model)")
   
    return "\n".join(smtlib)

def main():
    parser = argparse.ArgumentParser(description='生成Poseidon哈希电路的SMT-LIB表示')
    parser.add_argument('-i', '--inputs', type=int, default=1, help='输入数量 (默认: 1)')
    parser.add_argument('-o', '--outputs', type=int, default=1, help='输出数量 (默认: 1)')
    parser.add_argument('-c', '--constants', type=str, help='包含Poseidon常数的文件路径')
    parser.add_argument('-f', '--file', type=str, help='输出文件名')
   
    args = parser.parse_args()
   
    smtlib_code = generate_poseidon_smtlib(args.inputs, args.outputs, args.constants)
   
    # 输出到文件或控制台
    if args.file:
        filename = args.file
        with open(filename, "w", encoding="utf-8") as f:
            f.write(smtlib_code)
        print(f"SMT-LIB代码已生成并保存到 {filename}")
    else:
        print(smtlib_code)
   
    print(f"断言数量: {smtlib_code.count('(assert')}")

if __name__ == "__main__":
    main()