(set-logic QF_FF)
(set-option :produce-models true)
; BabyAdd等价性验证：两种独立实现的计算等价性
(define-sort BabyJubField () (_ FiniteField 21888242871839275222246405745257275088548364400416034343698204186575808495617))

; 基础运算
(define-fun ffadd ((a BabyJubField) (b BabyJubField)) BabyJubField (ff.add a b))
(define-fun ffmul ((a BabyJubField) (b BabyJubField)) BabyJubField (ff.mul a b))
(define-fun ffneg ((a BabyJubField)) BabyJubField (ff.neg a))  ; 关键修正：ffneg仅需1个参数

; 常量定义
(define-fun d () BabyJubField #f168696m21888242871839275222246405745257275088548364400416034343698204186575808495617)
(define-fun a_prime () BabyJubField #f168700m21888242871839275222246405745257275088548364400416034343698204186575808495617)
(define-fun zero () BabyJubField #f0m21888242871839275222246405745257275088548364400416034343698204186575808495617)
(define-fun one () BabyJubField #f1m21888242871839275222246405745257275088548364400416034343698204186575808495617)
(define-fun four () BabyJubField #f4m21888242871839275222246405745257275088548364400416034343698204186575808495617)

; 共享输入
(declare-const x1 BabyJubField)
(declare-const y1 BabyJubField)
(declare-const x2 BabyJubField)
(declare-const y2 BabyJubField)

; Circom电路约束
(declare-const A_beta BabyJubField)
(declare-const A_gamma BabyJubField)
(declare-const A_delta BabyJubField)
(declare-const A_tau BabyJubField)
(declare-const A_xout BabyJubField)
(declare-const A_yout BabyJubField)

(assert (= A_beta (ffmul x1 y2)))
(assert (= A_gamma (ffmul y1 x2)))
(assert (= A_delta (ffmul (ffadd (ffneg (ffmul a_prime x1)) y1) (ffadd x2 y2))))  ; 这里使用ffneg单参数
(assert (= A_tau (ffmul A_beta A_gamma)))
(assert (= (ffmul (ffadd one (ffmul d A_tau)) A_xout) (ffadd A_beta A_gamma)))
(assert (= (ffmul (ffadd one (ffneg (ffmul d A_tau))) A_yout)  ; 这里使用ffneg单参数
           (ffadd (ffadd A_delta (ffmul (ffadd four d) A_beta)) (ffneg A_gamma))))  ; 这里使用ffneg单参数

; 参考模型
(declare-const B_beta BabyJubField)
(declare-const B_gamma BabyJubField)
(declare-const B_tau BabyJubField)
(declare-const B_x1x2 BabyJubField)
(declare-const B_y1y2 BabyJubField)
(declare-const B_xout BabyJubField)
(declare-const B_yout BabyJubField)

(assert (= B_beta (ffmul x1 y2)))
(assert (= B_gamma (ffmul y1 x2)))
(assert (= B_tau (ffmul B_beta B_gamma)))
(assert (= B_x1x2 (ffmul x1 x2)))
(assert (= B_y1y2 (ffmul y1 y2)))
(assert (= (ffmul (ffadd one (ffmul d B_tau)) B_xout) (ffadd B_beta B_gamma)))
(assert (= (ffmul (ffadd one (ffneg (ffmul d B_tau))) B_yout)  
           (ffadd B_y1y2 (ffneg (ffmul a_prime B_x1x2)))))  

; 等价性断言 
(assert (not (= A_xout B_xout)))
(assert (not (= A_yout B_yout)))

; 排除无效情况 
(assert (not (= x1 zero)))
(assert (not (= y1 zero)))
(assert (not (= x2 zero)))
(assert (not (= y2 zero)))
(assert (not (= (ffadd one (ffmul d A_tau)) zero)))
(assert (not (= (ffadd one (ffneg (ffmul d A_tau))) zero)))
(assert (not (= (ffadd one (ffmul d B_tau)) zero)))
(assert (not (= (ffadd one (ffneg (ffmul d B_tau))) zero)))

(check-sat)
(get-model)
