#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re

def extract_constants_from_file(filename):
    """从文件中提取常数数组"""
    with open(filename, 'r') as f:
        content = f.read()
    
    # 使用正则表达式提取数组部分
    match = re.search(r'\[(.*?)\]', content, re.DOTALL)
    if not match:
        raise ValueError("无法从文件中找到有效的数组")
    
    # 提取数组字符串并转换为Python列表
    array_str = match.group(0)
    constants = json.loads(array_str)
    
    return constants

def generate_mimc7_smtlib(constants):
    """使用提取的常数生成SMT-LIB模型"""
    # 有限域模数 (来自 iden3/go-iden-crypto 的 _constants.Q)
    modulus = 21888242871839275222246405745257275088548364400416034343698204186575808495617
    
    # 检查常数数量是否正确
    if len(constants) != 91:
        print(f"警告: 期望91个常数，但找到{len(constants)}个")
    
    # 开始生成SMT-LIB脚本
    smtlib = f"""; MIMC7Hash SMT-LIB模型
; 使用CVC5有限域理论

; 声明有限域类型，模数为 {modulus}
(declare-sort F 0)
(declare-const modulus Int)
(assert (= modulus {modulus}))

; 声明有限域运算
(define-fun ffadd ((a F) (b F)) F (ff.add a b))
(define-fun ffmul ((a F) (b F)) F (ff.mul a b))
(define-fun ffsquare ((a F)) F (ff.mul a a))

; 声明输入变量
(declare-const xInBI F)
(declare-const kBI F)

; 声明常数常量
"""
    
    # 添加常数定义
    for i, constant in enumerate(constants):
        smtlib += f"(declare-const C_{i} F)\n"
        smtlib += f"(assert (= C_{i} (as ff{constant} F)))\n"
    
    # 声明中间变量
    for i in range(91):
        smtlib += f"(declare-const t_{i} F)\n"
        smtlib += f"(declare-const t2_{i} F)\n"
        smtlib += f"(declare-const t4_{i} F)\n"
        smtlib += f"(declare-const r_{i} F)\n"
    
    smtlib += "(declare-const result F)\n\n"
    
    # 第0轮计算
    smtlib += "; 第0轮计算\n"
    smtlib += "(assert (= t_0 (ffadd xInBI kBI)))\n"
    smtlib += "(assert (= t2_0 (ffmul t_0 t_0)))\n"
    smtlib += "(assert (= t4_0 (ffmul t2_0 t2_0)))\n"
    smtlib += "(assert (= r_0 (ffmul (ffmul t4_0 t2_0) t_0)))\n\n"
    
    # 第1到90轮计算
    for i in range(1, 91):
        smtlib += f"; 第{i}轮计算\n"
        smtlib += f"(assert (= t_{i} (ffadd (ffadd r_{i-1} kBI) C_{i})))\n"
        smtlib += f"(assert (= t2_{i} (ffmul t_{i} t_{i})))\n"
        smtlib += f"(assert (= t4_{i} (ffmul t2_{i} t2_{i})))\n"
        smtlib += f"(assert (= r_{i} (ffmul (ffmul t4_{i} t2_{i}) t_{i})))\n\n"
    
    # 最终结果
    smtlib += "; 最终结果\n"
    smtlib += "(assert (= result (ffadd r_90 kBI)))\n\n"
    
    # 可以添加具体的输入输出验证
    smtlib += """; 可以添加具体的输入输出验证
; (assert (= xInBI 12345))
; (assert (= kBI 67890))
; (assert (= result 期望的结果值))

(check-sat)
(get-model)
"""
    
    return smtlib

# 生成并保存SMT-LIB脚本
if __name__ == "__main__":
    try:
        # 从文件中提取常数
        constants = extract_constants_from_file("constant.txt")
        print(f"成功提取 {len(constants)} 个常数")
        
        # 生成SMT-LIB脚本
        smtlib_code = generate_mimc7_smtlib(constants)
        
        # 保存到文件
        with open("mimc7_hash.smt2", "w", encoding="utf-8") as f:
            f.write(smtlib_code)
        
        print("SMT-LIB脚本已生成到 mimc7_hash.smt2")
        
    except Exception as e:
        print(f"错误: {e}")
        print("请确保 constant.txt 文件存在且包含有效的常数数组")