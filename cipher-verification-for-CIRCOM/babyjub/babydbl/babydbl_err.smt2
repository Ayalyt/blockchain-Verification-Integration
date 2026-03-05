(set-logic QF_FF)
(set-option :produce-models true)
; BabyDbl反例演示：错误实现（A模型）与参考模型（B模型）
; 错误场景：yout计算时误用d代替a_prime参数

; 基础定义
(define-sort BabyJubField () (_ FiniteField 21888242871839275222246405745257275088548364400416034343698204186575808495617))
(define-fun ffadd ((a BabyJubField) (b BabyJubField)) BabyJubField (ff.add a b))
(define-fun ffmul ((a BabyJubField) (b BabyJubField)) BabyJubField (ff.mul a b))
(define-fun ffneg ((a BabyJubField)) BabyJubField (ff.neg a))
(define-fun ffsquare ((a BabyJubField)) BabyJubField (ffmul a a))

;常量定义
(define-fun d () BabyJubField #f168696m21888242871839275222246405745257275088548364400416034343698204186575808495617)
(define-fun a_prime_correct () BabyJubField #f168700m21888242871839275222246405745257275088548364400416034343698204186575808495617)
(define-fun a_prime_wrong () BabyJubField #f168696m21888242871839275222246405745257275088548364400416034343698204186575808495617)  ; 错误：用d代替a_prime
(define-fun neg_a_prime () BabyJubField #f21888242871839275222246405745257275088548364400416034343698204186575808326917m21888242871839275222246405745257275088548364400416034343698204186575808495617)
(define-fun zero () BabyJubField #f0m21888242871839275222246405745257275088548364400416034343698204186575808495617)
(define-fun one () BabyJubField #f1m21888242871839275222246405745257275088548364400416034343698204186575808495617)

; 合法输入（BabyJub曲线上的点P=(x,y)）
(declare-const x BabyJubField)
(declare-const y BabyJubField)
(assert (= x #f1m21888242871839275222246405745257275088548364400416034343698204186575808495617))
(assert (= y #f155276810039275222246405745257275088548364400416034343698204186575808495617m21888242871839275222246405745257275088548364400416034343698204186575808495617))  ; 合法y坐标

;  错误实现（A模型）
(declare-const A_xout BabyJubField)
(declare-const A_yout BabyJubField)
(declare-const A_beta BabyJubField)
(declare-const A_gamma BabyJubField)
(declare-const A_tau BabyJubField)
(declare-const A_delta BabyJubField)
(declare-const A_xout_den BabyJubField)
(declare-const A_yout_den BabyJubField)

(assert (= A_beta (ffmul x y)))
(assert (= A_gamma A_beta))
(assert (= A_tau (ffsquare A_beta)))
(assert (= A_delta (ffmul (ffadd (ffmul neg_a_prime x) y) (ffadd x y))))
(assert (= A_xout_den (ffadd one (ffmul d A_tau))))
(assert (= A_yout_den (ffadd one (ffneg (ffmul d A_tau)))))
(assert (= (ffmul A_xout_den A_xout) (ffadd A_beta A_gamma)))  ; xout计算正确
(assert (= (ffmul A_yout_den A_yout) (ffadd (ffadd A_delta (ffmul a_prime_wrong A_beta)) (ffneg A_gamma))))  ; 错误：用a_prime_wrong

; 正确实现（B模型）
(declare-const B_xout BabyJubField)
(declare-const B_yout BabyJubField)
(declare-const B_beta BabyJubField)
(declare-const B_gamma BabyJubField)
(declare-const B_tau BabyJubField)
(declare-const B_delta BabyJubField)
(declare-const B_xout_den BabyJubField)
(declare-const B_yout_den BabyJubField)

(assert (= B_beta (ffmul x y)))
(assert (= B_gamma B_beta))
(assert (= B_tau (ffsquare B_beta)))
(assert (= B_delta (ffmul (ffadd (ffmul neg_a_prime x) y) (ffadd x y))))
(assert (= B_xout_den (ffadd one (ffmul d B_tau))))
(assert (= B_yout_den (ffadd one (ffneg (ffmul d B_tau)))))
(assert (= (ffmul B_xout_den B_xout) (ffadd B_beta B_gamma)))
(assert (= (ffmul B_yout_den B_yout) (ffadd (ffadd B_delta (ffmul a_prime_correct B_beta)) (ffneg B_gamma))))  ; 正确：用a_prime_correct

; 等价性断言（触发反例）
(assert (not (= A_yout B_yout)))

; 排除无效情况
(assert (not (= A_xout_den zero)))
(assert (not (= A_yout_den zero)))
(assert (not (= B_xout_den zero)))
(assert (not (= B_yout_den zero)))

(check-sat)
(get-model)