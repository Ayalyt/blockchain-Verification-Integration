(set-logic QF_FF)
(set-option :produce-models true)
; BabyDbl等价性验证文件
; A模型：Circom电路约束逻辑
; B模型：数学参考模型（BabyJub点双倍公式）

; 有限域定义
(define-sort BabyJubField () (_ FiniteField 21888242871839275222246405745257275088548364400416034343698204186575808495617))

; 基础运算定义
(define-fun ffadd ((a BabyJubField) (b BabyJubField)) BabyJubField (ff.add a b))
(define-fun ffmul ((a BabyJubField) (b BabyJubField)) BabyJubField (ff.mul a b))
(define-fun ffneg ((a BabyJubField)) BabyJubField (ff.neg a))
(define-fun ffsquare ((a BabyJubField)) BabyJubField (ffmul a a))

; 固定参数声明
(define-fun d () BabyJubField #f168696m21888242871839275222246405745257275088548364400416034343698204186575808495617)
(define-fun a_prime () BabyJubField #f168700m21888242871839275222246405745257275088548364400416034343698204186575808495617)
(define-fun neg_a_prime () BabyJubField #f21888242871839275222246405745257275088548364400416034343698204186575808326917m21888242871839275222246405745257275088548364400416034343698204186575808495617)
(define-fun zero () BabyJubField #f0m21888242871839275222246405745257275088548364400416034343698204186575808495617)
(define-fun one () BabyJubField #f1m21888242871839275222246405745257275088548364400416034343698204186575808495617)

; 共享输入：待双倍的点P=(x,y)
(declare-const x BabyJubField)
(declare-const y BabyJubField)

; Circom电路约束
(declare-const A_xout BabyJubField)
(declare-const A_yout BabyJubField)
(declare-const A_beta BabyJubField)
(declare-const A_gamma BabyJubField)
(declare-const A_delta BabyJubField)
(declare-const A_tau BabyJubField)

; 模型约束完全复现Circom逻辑
(assert (= A_beta (ffmul x y)))
(assert (= A_gamma (ffmul y x)))
(assert (= A_delta (ffmul (ffadd (ffmul neg_a_prime x) y) (ffadd x y))))
(assert (= A_tau (ffmul A_beta A_gamma)))
(assert (= (ffmul (ffadd one (ffmul d A_tau)) A_xout) (ffadd A_beta A_gamma)))
(assert (= (ffmul (ffadd one (ffneg (ffmul d A_tau))) A_yout) 
           (ffadd (ffadd A_delta (ffmul a_prime A_beta)) (ffneg A_gamma))))

; 数学参考模型 
(declare-const B_xout BabyJubField)
(declare-const B_yout BabyJubField)
(declare-const B_beta BabyJubField)
(declare-const B_gamma BabyJubField)
(declare-const B_tau BabyJubField)
(declare-const B_delta BabyJubField)
(declare-const B_xout_den BabyJubField)
(declare-const B_yout_den BabyJubField)

; 模型约束遵循BabyDbl数学公式
(assert (= B_beta (ffmul x y)))
(assert (= B_gamma B_beta))  ; 双倍运算中x2=x1,y2=y1，gamma=beta
(assert (= B_tau (ffsquare B_beta)))  ; tau=beta²
(assert (= B_delta (ffmul (ffadd (ffmul neg_a_prime x) y) (ffadd x y))))
(assert (= B_xout_den (ffadd one (ffmul d B_tau))))
(assert (= B_yout_den (ffadd one (ffneg (ffmul d B_tau)))))
(assert (= (ffmul B_xout_den B_xout) (ffadd B_beta B_gamma)))
(assert (= (ffmul B_yout_den B_yout) (ffadd (ffadd B_delta (ffmul a_prime B_beta)) (ffneg B_gamma))))

; 等价性断言：A模型输出 ≡ B模型输出 
(assert (not (= A_xout B_xout)))
(assert (not (= A_yout B_yout)))

; 排除无效情况 
(assert (not (= x zero)))
(assert (not (= y zero)))
(assert (not (= (ffadd one (ffmul d A_tau)) zero)))
(assert (not (= (ffadd one (ffneg (ffmul d A_tau))) zero)))
(assert (not (= B_xout_den zero)))
(assert (not (= B_yout_den zero)))

; 求解并输出结果
(check-sat)
(get-model)
