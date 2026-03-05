(set-logic QF_NIA)
(set-option :produce-models true)
(define-const modulus Int 21888242871839275222246405745257275088548364400416034343698204186575808495617)

; 基础运算（模运算版本）
(define-fun add ((a Int) (b Int)) Int (mod (+ a b) modulus))
(define-fun mul ((a Int) (b Int)) Int (mod (* a b) modulus))
(define-fun neg ((a Int)) Int (mod (- a) modulus))  ; 整数取负后模运算

; 常量定义
(define-const d Int (mod 168696 modulus))
(define-const a_prime Int (mod 168700 modulus))
(define-const zero Int 0)
(define-const one Int 1)
(define-const four Int 4)

; 共享输入,范围限制在[0, modulus)
(declare-const x1 Int)
(declare-const y1 Int)
(declare-const x2 Int)
(declare-const y2 Int)
(assert (and (>= x1 0) (< x1 modulus)))
(assert (and (>= y1 0) (< y1 modulus)))
(assert (and (>= x2 0) (< x2 modulus)))
(assert (and (>= y2 0) (< y2 modulus)))

; Circom电路约束
(declare-const A_beta Int)
(declare-const A_gamma Int)
(declare-const A_delta Int)
(declare-const A_tau Int)
(declare-const A_xout Int)
(declare-const A_yout Int)

(assert (= A_beta (mul x1 y2)))
(assert (= A_gamma (mul y1 x2)))
(assert (= A_delta (mul (add (neg (mul a_prime x1)) y1) (add x2 y2))))
(assert (= A_tau (mul A_beta A_gamma)))
(assert (= (mul (add one (mul d A_tau)) A_xout) (add A_beta A_gamma)))
(assert (= (mul (add one (neg (mul d A_tau))) A_yout)
           (add (add A_delta (mul (add four d) A_beta)) (neg A_gamma))))

; 参考模型
(declare-const B_beta Int)
(declare-const B_gamma Int)
(declare-const B_tau Int)
(declare-const B_x1x2 Int)
(declare-const B_y1y2 Int)
(declare-const B_xout Int)
(declare-const B_yout Int)

(assert (= B_beta (mul x1 y2)))
(assert (= B_gamma (mul y1 x2)))
(assert (= B_tau (mul B_beta B_gamma)))
(assert (= B_x1x2 (mul x1 x2)))
(assert (= B_y1y2 (mul y1 y2)))
(assert (= (mul (add one (mul d B_tau)) B_xout) (add B_beta B_gamma)))
(assert (= (mul (add one (neg (mul d B_tau))) B_yout)
           (add B_y1y2 (neg (mul a_prime B_x1x2)))))

; 等价性断言
(assert (not (= A_xout B_xout)))
(assert (not (= A_yout B_yout)))

; 排除无效情况（避免除零，模运算中体现为避免与模数互质的情况）
(assert (not (= x1 zero)))
(assert (not (= y1 zero)))
(assert (not (= x2 zero)))
(assert (not (= y2 zero)))
(assert (not (= (add one (mul d A_tau)) zero)))
(assert (not (= (add one (neg (mul d A_tau))) zero)))
(assert (not (= (add one (mul d B_tau)) zero)))
(assert (not (= (add one (neg (mul d B_tau))) zero)))

(check-sat)
(get-model)
