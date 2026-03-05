(set-logic QF_FF)
(set-option :produce-models true)
; BabyAdd反例演示：A模型存在错误，后面有正确参考模型
; 场景：A模型的yout计算错误（误用a'=168696而非正确的168700）

; 有限域定义（BabyJub标量域）
(define-sort BabyJubField () (_ FiniteField 21888242871839275222246405745257275088548364400416034343698204186575808495617))

; 基础运算
(define-fun ffadd ((a BabyJubField) (b BabyJubField)) BabyJubField (ff.add a b))
(define-fun ffmul ((a BabyJubField) (b BabyJubField)) BabyJubField (ff.mul a b))
(define-fun ffneg ((a BabyJubField)) BabyJubField (ff.neg a))

; 常量定义（正确参数）
(define-fun d () BabyJubField #f168696m21888242871839275222246405745257275088548364400416034343698204186575808495617)
(define-fun a_prime_correct () BabyJubField #f168700m21888242871839275222246405745257275088548364400416034343698204186575808495617)  ; 正确a'=168700
(define-fun a_prime_wrong () BabyJubField #f168696m21888242871839275222246405745257275088548364400416034343698204186575808495617)   ; 错误a'=168696（模拟实现错误）
(define-fun zero () BabyJubField #f0m21888242871839275222246405745257275088548364400416034343698204186575808495617)
(define-fun one () BabyJubField #f1m21888242871839275222246405745257275088548364400416034343698204186575808495617)
(define-fun four () BabyJubField #f4m21888242871839275222246405745257275088548364400416034343698204186575808495617)

; 具体输入参数（BabyJub曲线上的合法点）
(declare-const x1 BabyJubField)
(declare-const y1 BabyJubField)
(declare-const x2 BabyJubField)
(declare-const y2 BabyJubField)
; 设定具体输入值（已知在BabyJub曲线上的点）
(assert (= x1 #f1m21888242871839275222246405745257275088548364400416034343698204186575808495617))
(assert (= y1 #f15527681003928902128179717624703512672403908117992798440346960750464748824729m21888242871839275222246405745257275088548364400416034343698204186575808495617))  ; 对应x1的合法y坐标
(assert (= x2 #f2m21888242871839275222246405745257275088548364400416034343698204186575808495617))
(assert (= y2 #f10857046999023057135944570762232829481370756359578518086990519993285655852781m21888242871839275222246405745257275088548364400416034343698204186575808495617))  ; 对应x2的合法y坐标

;  错误实现：误用a'参数 
(declare-const A_xout BabyJubField)
(declare-const A_yout BabyJubField)
(declare-const A_beta BabyJubField)
(declare-const A_gamma BabyJubField)
(declare-const A_tau BabyJubField)
(declare-const A_x1x2 BabyJubField)
(declare-const A_y1y2 BabyJubField)

(assert (= A_beta (ffmul x1 y2)))
(assert (= A_gamma (ffmul y1 x2)))
(assert (= A_tau (ffmul A_beta A_gamma)))
(assert (= A_x1x2 (ffmul x1 x2)))
(assert (= A_y1y2 (ffmul y1 y2)))
; xout计算
(assert (= (ffmul (ffadd one (ffmul d A_tau)) A_xout) (ffadd A_beta A_gamma)))
; yout计算（使用a_prime_wrong）
(assert (= (ffmul (ffadd one (ffneg (ffmul d A_tau))) A_yout) 
           (ffadd A_y1y2 (ffneg (ffmul a_prime_wrong A_x1x2)))))

; 参考模型使用正确a'参数 
(declare-const B_xout BabyJubField)
(declare-const B_yout BabyJubField)
(declare-const B_beta BabyJubField)
(declare-const B_gamma BabyJubField)
(declare-const B_tau BabyJubField)
(declare-const B_x1x2 BabyJubField)
(declare-const B_y1y2 BabyJubField)

(assert (= B_beta (ffmul x1 y2)))
(assert (= B_gamma (ffmul y1 x2)))
(assert (= B_tau (ffmul B_beta B_gamma)))
(assert (= B_x1x2 (ffmul x1 x2)))
(assert (= B_y1y2 (ffmul y1 y2)))
; xout计算
(assert (= (ffmul (ffadd one (ffmul d B_tau)) B_xout) (ffadd B_beta B_gamma)))
; yout计算
(assert (= (ffmul (ffadd one (ffneg (ffmul d B_tau))) B_yout) 
           (ffadd B_y1y2 (ffneg (ffmul a_prime_correct B_x1x2)))))

; 等价性断言：若A和B等价，则此断言不可满足
(assert (not (= A_yout B_yout)))  ; 因A模型yout错误，此断言可满足

; 排除分母为零
(assert (not (= (ffadd one (ffmul d A_tau)) zero)))
(assert (not (= (ffadd one (ffneg (ffmul d A_tau))) zero)))

(check-sat)
(get-model)