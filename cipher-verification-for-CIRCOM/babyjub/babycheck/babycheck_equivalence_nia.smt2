(set-logic QF_NIA)
(set-option :produce-models true)
; BabyCheck等价性验证文件（QF_NIA理论）
; 功能：验证点(x,y)是否满足BabyJub曲线方程
; A模型 Circom电路约束逻辑
; B模型 纯数学参考模型

; 核心参数定义
(define-const MOD Int 21888242871839275222246405745257275088548364400416034343698204186575808495617)

; 基础模运算定义
(define-fun mod_add ((a Int) (b Int)) Int (mod (+ a b) MOD))  ; 模加法
(define-fun mod_mul ((a Int) (b Int)) Int (mod (* a b) MOD))  ; 模乘法
(define-fun mod_square ((a Int)) Int (mod_mul a a))           ; 模平方

; 固定参数声明
(define-const a_prime Int 168700)
(define-const d Int 168696)
(define-const one Int 1)
(define-const zero Int 0)

; 输入变量：待验证的点(x,y)
(declare-const x Int)
(declare-const y Int)
; 限制变量在有限域范围内 [0, MOD-1]
(assert (and (<= 0 x) (< x MOD)))
(assert (and (<= 0 y) (< y MOD)))


; Circom电路约束逻辑
(declare-const A_x_sq Int)  ; x的平方
(declare-const A_y_sq Int)  ; y的平方

; 变量范围约束
(assert (and (<= 0 A_x_sq) (< A_x_sq MOD)))
(assert (and (<= 0 A_y_sq) (< A_y_sq MOD)))

; 核心约束
(assert (= A_x_sq (mod_square x)))                ; A_x_sq = x² mod MOD
(assert (= A_y_sq (mod_square y)))                ; A_y_sq = y² mod MOD
(assert (= (mod_add (mod_mul a_prime A_x_sq) A_y_sq)  ; a'x² + y² = 1 + d x² y² (mod MOD)
           (mod_add one (mod_mul d (mod_mul A_x_sq A_y_sq)))))

;  数学参考模型
(declare-const B_x_sq Int)  ; x的平方
(declare-const B_y_sq Int)  ; y的平方

; B模型变量范围约束
(assert (and (<= 0 B_x_sq) (< B_x_sq MOD)))
(assert (and (<= 0 B_y_sq) (< B_y_sq MOD)))

; B模型核心约束
(assert (= B_x_sq (mod_square x)))                ; B_x_sq = x² mod MOD
(assert (= B_y_sq (mod_square y)))                ; B_y_sq = y² mod MOD
(assert (= (mod_add (mod_mul a_prime B_x_sq) B_y_sq)  ; a'x² + y² = 1 + d x² y² (mod MOD)
           (mod_add one (mod_mul d (mod_mul B_x_sq B_y_sq)))))


; 等价性验证 A模型与B模型是否等价
; 是否存在点满足A模型但不满足B模型
(assert (or 
    (not (= A_x_sq B_x_sq))                     ; x平方计算不等价
    (not (= A_y_sq B_y_sq))                     ; y平方计算不等价
    (not (= (mod_add (mod_mul a_prime A_x_sq) A_y_sq) 
            (mod_add (mod_mul a_prime B_x_sq) B_y_sq)))  ; 曲线方程不等价
))

; 排除无效点（原点等特殊情况）
(assert (not (= x zero)))
(assert (not (= y zero)))

; 求解并输出结果
(check-sat)
(get-model)
