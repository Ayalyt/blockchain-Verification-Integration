(set-logic QF_FF)
(set-option :produce-models true)
; 修正版BabyCheck反例：无重复声明，确保返回sat
; 错误模型（误用d代替a'）成立，正确模型（a'=168700）不成立
; 基础定义（无重复声明）
(define-sort BabyJubField () (_ FiniteField 21888242871839275222246405745257275088548364400416034343698204186575808495617))
(define-fun ffadd ((a BabyJubField) (b BabyJubField)) BabyJubField (ff.add a b))
(define-fun ffmul ((a BabyJubField) (b BabyJubField)) BabyJubField (ff.mul a b))
(define-fun ffsquare ((a BabyJubField)) BabyJubField (ffmul a a))  ; 仅声明一次单参数平方函数

; 参数定义（正确+错误）
(define-fun a_prime_correct () BabyJubField #f168700m21888242871839275222246405745257275088548364400416034343698204186575808495617)
(define-fun a_prime_wrong () BabyJubField #f168696m21888242871839275222246405745257275088548364400416034343698204186575808495617)  ; 错误：用d代替a'
(define-fun d () BabyJubField #f168696m21888242871839275222246405745257275088548364400416034343698204186575808495617)
(define-fun one () BabyJubField #f1m21888242871839275222246405745257275088548364400416034343698204186575808495617)
(define-fun zero () BabyJubField #f0m21888242871839275222246405745257275088548364400416034343698204186575808495617)

; 输入变量（求解器自动寻找满足条件的x,y）
(declare-const x BabyJubField)
(declare-const y BabyJubField)

; 错误模型（A模型）：满足错误方程 -
(declare-const A_x_sq BabyJubField)
(declare-const A_y_sq BabyJubField)
(assert (= A_x_sq (ffsquare x)))  
(assert (= A_y_sq (ffsquare y)))
; 错误曲线方程：d·x² + y² = 1 + d·x²·y²
(assert (= (ffadd (ffmul a_prime_wrong A_x_sq) A_y_sq) 
           (ffadd one (ffmul d (ffmul A_x_sq A_y_sq)))))

; 正确模型（B模型）：不满足正确方程 
(declare-const B_x_sq BabyJubField)
(declare-const B_y_sq BabyJubField)
(assert (= B_x_sq (ffsquare x)))
(assert (= B_y_sq (ffsquare y)))
; 正确曲线方程：a'·x² + y² = 1 + d·x²·y²（断言不成立）
(assert (not (= (ffadd (ffmul a_prime_correct B_x_sq) B_y_sq) 
                (ffadd one (ffmul d (ffmul B_x_sq B_y_sq))))))

; 排除原点
(assert (not (= x zero)))
(assert (not (= y zero)))

(check-sat)
(get-model)