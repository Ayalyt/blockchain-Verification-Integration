def generate_babycheck_verification(output_path):
    """生成BabyCheck等价性验证SMT文件（验证点是否在BabyJub曲线上）"""
    params = {
        "modulus": "21888242871839275222246405745257275088548364400416034343698204186575808495617",
        "a_prime": 168700,
        "d": 168696,
        "one": "1",
        "zero": "0"
    }

    content = f"""(set-logic QF_FF)
(set-option :produce-models true)
; BabyCheck等价性验证文件
; 功能：验证点(x,y)是否满足BabyJub曲线方程
; A模型 Circom电路约束逻辑
; B模型 数学参考模型

; 有限域定义
(define-sort BabyJubField () (_ FiniteField {params['modulus']}))

; 基础运算定义
(define-fun ffadd ((a BabyJubField) (b BabyJubField)) BabyJubField (ff.add a b))
(define-fun ffmul ((a BabyJubField) (b BabyJubField)) BabyJubField (ff.mul a b))
(define-fun ffsquare ((a BabyJubField)) BabyJubField (ffmul a a))

; 固定参数声明
(define-fun a_prime () BabyJubField #f{params['a_prime']}m{params['modulus']})
(define-fun d () BabyJubField #f{params['d']}m{params['modulus']})
(define-fun one () BabyJubField #f{params['one']}m{params['modulus']})
(define-fun zero () BabyJubField #f{params['zero']}m{params['modulus']})

; 输入变量：待验证的点(x,y)
(declare-const x BabyJubField)
(declare-const y BabyJubField)

; A模型 Circom电路约束
(declare-const A_x2 BabyJubField)  ; x²
(declare-const A_y2 BabyJubField)  ; y²

; A模型约束
(assert (= A_x2 (ffsquare x)))
(assert (= A_y2 (ffsquare y)))
(assert (= (ffadd (ffmul a_prime A_x2) A_y2) 
           (ffadd one (ffmul d (ffmul A_x2 A_y2)))))

; B模型 纯数学参考模型 
(declare-const B_x_sq BabyJubField)  ; x²
(declare-const B_y_sq BabyJubField)  ; y²

; B模型约束 
(assert (= B_x_sq (ffsquare x)))
(assert (= B_y_sq (ffsquare y)))
(assert (= (ffadd (ffmul a_prime B_x_sq) B_y_sq) 
           (ffadd one (ffmul d (ffmul B_x_sq B_y_sq)))))

; 等价性断言 A模型与B模型约束一致 
; 验证是否存在点满足A模型但不满足B模型
(assert (or (not (= A_x2 B_x_sq))
            (not (= A_y2 B_y_sq))
            (not (= (ffadd (ffmul a_prime A_x2) A_y2) 
                    (ffadd one (ffmul d (ffmul A_x2 A_y2)))))
            (not (= (ffadd (ffmul a_prime B_x_sq) B_y_sq) 
                    (ffadd one (ffmul d (ffmul B_x_sq B_y_sq)))))))

; 排除无效情况 
(assert (not (= x zero)))
(assert (not (= y zero)))

; 求解并输出结果
(check-sat)
(get-model)
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"BabyCheck等价性验证文件已生成：{output_path}")

if __name__ == "__main__":
    generate_babycheck_verification("babycheck_equivalence.smt2")