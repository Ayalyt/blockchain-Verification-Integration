(* 85行修改 *)
proc sha256Ch(uint32 x,uint32 y,uint32 z;uint32 r)=
{ true && true }
(* r = (x && y) ^ (~x && z) *)
and r0@uint32 x y;
not xnot@uint32 x;
and r1@uint32 xnot z;
xor r@uint32 r0 r1;
{ true && true }

proc sha256Maj (uint32 x, uint32 y, uint32 z; uint32 r) =
(* r = (x && y) ^ (x && z) ^ (y && z) *)
{ true && true }
and r0@uint32 x y;
and r1@uint32 x z;
and r2@uint32 y z;
xor r3@uint32 r0 r1;
xor r@uint32 r2 r3;
{ true && true }

proc sha256Sigma0 (uint32 x; uint32 r) =
{ true && true }
(* r = (x ror 2) ^ (x ror 13) ^ (x ror 22) *)
ror r0@uint32 x  2;
ror r1@uint32 x 13;
ror r2@uint32 x 22;
xor r3@uint32 r0 r1;
xor r@uint32 r2 r3;
{ true && true }

proc sha256Sigma1 (uint32 x; uint32 r) =
{ true && true }
(* r = (x ror 6) ^ (x ror 11) ^ (x ror 25) *)
ror r0@uint32 x  6;
ror r1@uint32 x 11;
ror r2@uint32 x 25;
xor r3@uint32 r0 r1;
xor r@uint32 r2 r3;
{ true && true }

proc sha256sigma0 (uint32 x; uint32 r) =
{ true && true }
(* r = (x ror 7) ^ (x ror 18) ^ (x >> 3) *)
ror r0@uint32 x  7;
ror r1@uint32 x 18;
split r2 dc x 3;
xor r3@uint32 r0 r1;
xor r@uint32 r2 r3;
{ true && true }

proc sha256sigma1 (uint32 x; uint32 r) =
{ true && true }
(* r = (x ror 17) ^ (x ror 19) ^ (x >> 10) *)
ror r0@uint32 x 17;
ror r1@uint32 x 19;
split r2 dc x 10;
xor r3@uint32 r0 r1;
xor r@uint32 r2 r3;
{ true && true }

proc sha256roundFunction(uint32 A, uint32 B, uint32 C, uint32 D,
                uint32 E, uint32 F, uint32 G, uint32 H,
                uint32 W, uint32 K; 
                uint32 a, uint32 b, uint32 c, uint32 d,
                uint32 e, uint32 f, uint32 g, uint32 h)=
{ true && true }
inline sha256Sigma1 (E, ESigma1);
inline sha256Ch (E, F, G, EFGCh);
inline sha256Sigma0 (A, ASigma0);
inline sha256Maj (A, B, C, ABCMaj);

(* T1 = H + Sigma1 (E) + Ch (E, F, G) + K + W *)
adds dc T00 H ESigma1;
adds dc T01 K W;
adds dc T02 T00 T01;
adds dc T1 T02 EFGCh;

(* T2 = Sigma0 (a) + Maj (a, b, c) *)
adds dc T2 ASigma0 ABCMaj;

mov h G;
mov g F;
mov f E;
adds dc e D T1;
mov d C;
(*
mov c B;
mov b A;
*)
mov b B;
mov c A;
adds dc a T1 T2;
{ true && true }

proc montage(uint8 A, uint8 B, uint8 C, uint8 D;uint32 w )=
{ true && true }
mov v9 A;
cast v_conv@uint32 v9@uint8;
shls discard_0 v_shl v_conv 24;
mov v10 B;
cast v_conv17@uint32 v10@uint8;
shls discard_1 v_shl18 v_conv17 16;
or uint32 v_or v_shl18 v_shl;
mov v11 C;
cast v_conv20@uint32 v11@uint8;
shls discard_2 v_shl21 v_conv20 8;
or uint32 v_or22 v_or v_shl21;
mov v12 D;
cast v_conv24@uint32 v12@uint8;
or uint32 v_or25 v_or22 v_conv24;
mov w v_or25;
{ true && true }

proc main(uint8 A00, uint8 A01, uint8 A02, uint8 A03, uint8 A04, uint8 A05, uint8 A06,
uint8 A07, uint8 A08, uint8 A09, uint8 A10, uint8 A11, uint8 A12, uint8 A13,
uint8 A14, uint8 A15, uint8 A16, uint8 A17, uint8 A18, uint8 A19,
  uint8 A20, uint8 A21, uint8 A22, uint8 A23, uint8 A24,
  uint8 A25, uint8 A26, uint8 A27, uint8 A28, uint8 A29,
  uint8 A30, uint8 A31, uint8 A32, uint8 A33, uint8 A34,
  uint8 A35, uint8 A36, uint8 A37, uint8 A38, uint8 A39,
  uint8 A40, uint8 A41, uint8 A42, uint8 A43, uint8 A44,
  uint8 A45, uint8 A46, uint8 A47, uint8 A48, uint8 A49,
  uint8 A50, uint8 A51, uint8 A52, uint8 A53, uint8 A54,
  uint8 A55, uint8 A56, uint8 A57, uint8 A58, uint8 A59,
  uint8 A60, uint8 A61, uint8 A62, uint8 A63,
uint32 A0, uint32 A1, uint32 A2, uint32 A3,
uint32 A4, uint32 A5, uint32 A6, uint32 A7;
uint32 a0, uint32 a1, uint32 a2, uint32 a3,
uint32 a4, uint32 a5, uint32 a6, uint32 a7)=
{
  true
  &&
  true
}
mov a A0;
mov b A1;
mov c A2;
mov d A3;
mov e A4;
mov f A5;
mov g A6;
mov h A7;
(*
mov K0 0@uint32; mov K1 1@uint32;  
mov K2 2@uint32; mov K3 3@uint32;  
mov K4 4@uint32; mov K5 5@uint32;  
mov K6 6@uint32; mov K7 7@uint32;  
mov K8 8@uint32; mov K9 9@uint32;  
mov K10 10@uint32; mov K11 11@uint32;  
mov K12 12@uint32; mov K13 13@uint32;  
mov K14 14@uint32; mov K15 15@uint32;  
mov K16 16@uint32; mov K17 17@uint32;  
mov K18 18@uint32; mov K19 19@uint32;  
mov K20 20@uint32; mov K21 21@uint32;  
mov K22 22@uint32; mov K23 23@uint32;  
mov K24 24@uint32; mov K25 25@uint32;  
mov K26 26@uint32; mov K27 27@uint32;  
mov K28 28@uint32; mov K29 29@uint32;  
mov K30 30@uint32; mov K31 31@uint32;  
mov K32 32@uint32; mov K33 33@uint32;  
mov K34 34@uint32; mov K35 35@uint32;  
mov K36 36@uint32; mov K37 37@uint32;  
mov K38 38@uint32; mov K39 39@uint32;  
mov K40 40@uint32; mov K41 41@uint32;  
mov K42 42@uint32; mov K43 43@uint32;  
mov K44 44@uint32; mov K45 45@uint32;  
mov K46 46@uint32; mov K47 47@uint32;  
mov K48 48@uint32; mov K49 49@uint32;  
mov K50 50@uint32; mov K51 51@uint32;  
mov K52 52@uint32; mov K53 53@uint32;  
mov K54 54@uint32; mov K55 55@uint32;  
mov K56 56@uint32; mov K57 57@uint32;  
mov K58 58@uint32; mov K59 59@uint32;  
mov K60 60@uint32; mov K61 61@uint32;  
mov K62 62@uint32; mov K63 63@uint32;
*)


mov K0 0x428a2f98@uint32; mov K1 0x71374491@uint32;  
mov K2 0xb5c0fbcf@uint32; mov K3 0xe9b5dba5@uint32;  
mov K4 0x3956c25b@uint32; mov K5 0x59f111f1@uint32;  
mov K6 0x923f82a4@uint32; mov K7 0xab1c5ed5@uint32;  
mov K8 0xd807aa98@uint32; mov K9 0x12835b01@uint32;  
mov K10 0x243185be@uint32; mov K11 0x550c7dc3@uint32;  
mov K12 0x72be5d74@uint32; mov K13 0x80deb1fe@uint32;  
mov K14 0x9bdc06a7@uint32; mov K15 0xc19bf174@uint32;  
mov K16 0xe49b69c1@uint32; mov K17 0xefbe4786@uint32;  
mov K18 0x0fc19dc6@uint32; mov K19 0x240ca1cc@uint32;  
mov K20 0x2de92c6f@uint32; mov K21 0x4a7484aa@uint32;  
mov K22 0x5cb0a9dc@uint32; mov K23 0x76f988da@uint32;  
mov K24 0x983e5152@uint32; mov K25 0xa831c66d@uint32;  
mov K26 0xb00327c8@uint32; mov K27 0xbf597fc7@uint32;  
mov K28 0xc6e00bf3@uint32; mov K29 0xd5a79147@uint32;  
mov K30 0x06ca6351@uint32; mov K31 0x14292967@uint32;  
mov K32 0x27b70a85@uint32; mov K33 0x2e1b2138@uint32;  
mov K34 0x4d2c6dfc@uint32; mov K35 0x53380d13@uint32;  
mov K36 0x650a7354@uint32; mov K37 0x766a0abb@uint32;  
mov K38 0x81c2c92e@uint32; mov K39 0x92722c85@uint32;  
mov K40 0xa2bfe8a1@uint32; mov K41 0xa81a664b@uint32;  
mov K42 0xc24b8b70@uint32; mov K43 0xc76c51a3@uint32;  
mov K44 0xd192e819@uint32; mov K45 0xd6990624@uint32;  
mov K46 0xf40e3585@uint32; mov K47 0x106aa070@uint32;  
mov K48 0x19a4c116@uint32; mov K49 0x1e376c08@uint32;  
mov K50 0x2748774c@uint32; mov K51 0x34b0bcb5@uint32;  
mov K52 0x391c0cb3@uint32; mov K53 0x4ed8aa4a@uint32;  
mov K54 0x5b9cca4f@uint32; mov K55 0x682e6ff3@uint32;  
mov K56 0x748f82ee@uint32; mov K57 0x78a5636f@uint32;  
mov K58 0x84c87814@uint32; mov K59 0x8cc70208@uint32;  
mov K60 0x90befffa@uint32; mov K61 0xa4506ceb@uint32;  
mov K62 0xbef9a3f7@uint32; mov K63 0xc67178f2@uint32;

#r=0
inline montage(A00,A01,A02,A03;w0);
inline sha256roundFunction(a,b,c,d,e,f,g,h,w0,K0;a,b,c,d,e,f,g,h);

#r=1
inline montage(A04,A05,A06,A07;w1);
inline sha256roundFunction(a,b,c,d,e,f,g,h,w1,K1;a,b,c,d,e,f,g,h);
#r=2
inline montage(A08,A09,A10,A11;w2);
inline sha256roundFunction(a,b,c,d,e,f,g,h,w2,K2;a,b,c,d,e,f,g,h);
#r=3
inline montage(A12,A13,A14,A15;w3);
inline sha256roundFunction(a,b,c,d,e,f,g,h,w3,K3;a,b,c,d,e,f,g,h);
#r=4
inline montage(A16,A17,A18,A19;w4);
inline sha256roundFunction(a,b,c,d,e,f,g,h,w4,K4;a,b,c,d,e,f,g,h);
#r=5
inline montage(A20,A21,A22,A23;w5);
inline sha256roundFunction(a,b,c,d,e,f,g,h,w5,K5;a,b,c,d,e,f,g,h);
#r=6
inline montage(A24,A25,A26,A27;w6);
inline sha256roundFunction(a,b,c,d,e,f,g,h,w6,K6;a,b,c,d,e,f,g,h);
#r=7
inline montage(A28,A29,A30,A31;w7);
inline sha256roundFunction(a,b,c,d,e,f,g,h,w7,K7;a,b,c,d,e,f,g,h);
#r=8
inline montage(A32,A33,A34,A35;w8);
inline sha256roundFunction(a,b,c,d,e,f,g,h,w8,K8;a,b,c,d,e,f,g,h);
#r=9
inline montage(A36,A37,A38,A39;w9);
inline sha256roundFunction(a,b,c,d,e,f,g,h,w9,K9;a,b,c,d,e,f,g,h);
#r=10
inline montage(A40,A41,A42,A43;w10);
inline sha256roundFunction(a,b,c,d,e,f,g,h,w10,K10;a,b,c,d,e,f,g,h);
#r=11
inline montage(A44,A45,A46,A47;w11);
inline sha256roundFunction(a,b,c,d,e,f,g,h,w11,K11;a,b,c,d,e,f,g,h);
#r=12
inline montage(A48,A49,A50,A51;w12);
inline sha256roundFunction(a,b,c,d,e,f,g,h,w12,K12;a,b,c,d,e,f,g,h);
#r=13
inline montage(A52,A53,A54,A55;w13);
inline sha256roundFunction(a,b,c,d,e,f,g,h,w13,K13;a,b,c,d,e,f,g,h);
#r=14
inline montage(A56,A57,A58,A59;w14);
inline sha256roundFunction(a,b,c,d,e,f,g,h,w14,K14;a,b,c,d,e,f,g,h);
#r=15
inline montage(A60,A61,A62,A63;w15);
inline sha256roundFunction(a,b,c,d,e,f,g,h,w15,K15;a,b,c,d,e,f,g,h);
#r=16
inline sha256sigma1(w14,w000);
inline sha256sigma0(w1,w001);
adds dc wa w000 w9;
adds dc wb w001 w0;
adds dc w16 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w16,K16;a,b,c,d,e,f,g,h);

#r=17
inline sha256sigma1(w15,w000);
inline sha256sigma0(w2,w001);
adds dc wa w000 w10;
adds dc wb w001 w1;
adds dc w17 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w17,K17;a,b,c,d,e,f,g,h);
#r=18
inline sha256sigma1(w16,w000);
inline sha256sigma0(w3,w001);
adds dc wa w000 w11;
adds dc wb w001 w2;
adds dc w18 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w18,K18;a,b,c,d,e,f,g,h);
#r=19
inline sha256sigma1(w17,w000);
inline sha256sigma0(w4,w001);
adds dc wa w000 w12;
adds dc wb w001 w3;
adds dc w19 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w19,K19;a,b,c,d,e,f,g,h);
#r=20
inline sha256sigma1(w18,w000);
inline sha256sigma0(w5,w001);
adds dc wa w000 w13;
adds dc wb w001 w4;
adds dc w20 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w20,K20;a,b,c,d,e,f,g,h);
#r=21
inline sha256sigma1(w19,w000);
inline sha256sigma0(w6,w001);
adds dc wa w000 w14;
adds dc wb w001 w5;
adds dc w21 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w21,K21;a,b,c,d,e,f,g,h);
#r=22
inline sha256sigma1(w20,w000);
inline sha256sigma0(w7,w001);
adds dc wa w000 w15;
adds dc wb w001 w6;
adds dc w22 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w22,K22;a,b,c,d,e,f,g,h);
#r=23
inline sha256sigma1(w21,w000);
inline sha256sigma0(w8,w001);
adds dc wa w000 w16;
adds dc wb w001 w7;
adds dc w23 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w23,K23;a,b,c,d,e,f,g,h);
#r=24
inline sha256sigma1(w22,w000);
inline sha256sigma0(w9,w001);
adds dc wa w000 w17;
adds dc wb w001 w8;
adds dc w24 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w24,K24;a,b,c,d,e,f,g,h);
#r=25
inline sha256sigma1(w23,w000);
inline sha256sigma0(w10,w001);
adds dc wa w000 w18;
adds dc wb w001 w9;
adds dc w25 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w25,K25;a,b,c,d,e,f,g,h);
#r=26
inline sha256sigma1(w24,w000);
inline sha256sigma0(w11,w001);
adds dc wa w000 w19;
adds dc wb w001 w10;
adds dc w26 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w26,K26;a,b,c,d,e,f,g,h);
#r=27
inline sha256sigma1(w25,w000);
inline sha256sigma0(w12,w001);
adds dc wa w000 w20;
adds dc wb w001 w11;
adds dc w27 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w27,K27;a,b,c,d,e,f,g,h);
#r=28
inline sha256sigma1(w26,w000);
inline sha256sigma0(w13,w001);
adds dc wa w000 w21;
adds dc wb w001 w12;
adds dc w28 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w28,K28;a,b,c,d,e,f,g,h);
#r=29
inline sha256sigma1(w27,w000);
inline sha256sigma0(w14,w001);
adds dc wa w000 w22;
adds dc wb w001 w13;
adds dc w29 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w29,K29;a,b,c,d,e,f,g,h);
#r=30
inline sha256sigma1(w28,w000);
inline sha256sigma0(w15,w001);
adds dc wa w000 w23;
adds dc wb w001 w14;
adds dc w30 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w30,K30;a,b,c,d,e,f,g,h);
#r=31
inline sha256sigma1(w29,w000);
inline sha256sigma0(w16,w001);
adds dc wa w000 w24;
adds dc wb w001 w15;
adds dc w31 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w31,K31;a,b,c,d,e,f,g,h);
#r=32
inline sha256sigma1(w30,w000);
inline sha256sigma0(w17,w001);
adds dc wa w000 w25;
adds dc wb w001 w16;
adds dc w32 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w32,K32;a,b,c,d,e,f,g,h);
#r=33
inline sha256sigma1(w31,w000);
inline sha256sigma0(w18,w001);
adds dc wa w000 w26;
adds dc wb w001 w17;
adds dc w33 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w33,K33;a,b,c,d,e,f,g,h);
#r=34
inline sha256sigma1(w32,w000);
inline sha256sigma0(w19,w001);
adds dc wa w000 w27;
adds dc wb w001 w18;
adds dc w34 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w34,K34;a,b,c,d,e,f,g,h);
#r=35
inline sha256sigma1(w33,w000);
inline sha256sigma0(w20,w001);
adds dc wa w000 w28;
adds dc wb w001 w19;
adds dc w35 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w35,K35;a,b,c,d,e,f,g,h);
#r=36
inline sha256sigma1(w34,w000);
inline sha256sigma0(w21,w001);
adds dc wa w000 w29;
adds dc wb w001 w20;
adds dc w36 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w36,K36;a,b,c,d,e,f,g,h);
#r=37
inline sha256sigma1(w35,w000);
inline sha256sigma0(w22,w001);
adds dc wa w000 w30;
adds dc wb w001 w21;
adds dc w37 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w37,K37;a,b,c,d,e,f,g,h);
#r=38
inline sha256sigma1(w36,w000);
inline sha256sigma0(w23,w001);
adds dc wa w000 w31;
adds dc wb w001 w22;
adds dc w38 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w38,K38;a,b,c,d,e,f,g,h);
#r=39
inline sha256sigma1(w37,w000);
inline sha256sigma0(w24,w001);
adds dc wa w000 w32;
adds dc wb w001 w23;
adds dc w39 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w39,K39;a,b,c,d,e,f,g,h);
#r=40
inline sha256sigma1(w38,w000);
inline sha256sigma0(w25,w001);
adds dc wa w000 w33;
adds dc wb w001 w24;
adds dc w40 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w40,K40;a,b,c,d,e,f,g,h);
#r=41
inline sha256sigma1(w39,w000);
inline sha256sigma0(w26,w001);
adds dc wa w000 w34;
adds dc wb w001 w25;
adds dc w41 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w41,K41;a,b,c,d,e,f,g,h);
#r=42
inline sha256sigma1(w40,w000);
inline sha256sigma0(w27,w001);
adds dc wa w000 w35;
adds dc wb w001 w26;
adds dc w42 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w42,K42;a,b,c,d,e,f,g,h);
#r=43
inline sha256sigma1(w41,w000);
inline sha256sigma0(w28,w001);
adds dc wa w000 w36;
adds dc wb w001 w27;
adds dc w43 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w43,K43;a,b,c,d,e,f,g,h);
#r=44
inline sha256sigma1(w42,w000);
inline sha256sigma0(w29,w001);
adds dc wa w000 w37;
adds dc wb w001 w28;
adds dc w44 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w44,K44;a,b,c,d,e,f,g,h);
#r=45
inline sha256sigma1(w43,w000);
inline sha256sigma0(w30,w001);
adds dc wa w000 w38;
adds dc wb w001 w29;
adds dc w45 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w45,K45;a,b,c,d,e,f,g,h);
#r=46
inline sha256sigma1(w44,w000);
inline sha256sigma0(w31,w001);
adds dc wa w000 w39;
adds dc wb w001 w30;
adds dc w46 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w46,K46;a,b,c,d,e,f,g,h);
#r=47
inline sha256sigma1(w45,w000);
inline sha256sigma0(w32,w001);
adds dc wa w000 w40;
adds dc wb w001 w31;
adds dc w47 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w47,K47;a,b,c,d,e,f,g,h);
#r=48
inline sha256sigma1(w46,w000);
inline sha256sigma0(w33,w001);
adds dc wa w000 w41;
adds dc wb w001 w32;
adds dc w48 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w48,K48;a,b,c,d,e,f,g,h);
#r=49
inline sha256sigma1(w47,w000);
inline sha256sigma0(w34,w001);
adds dc wa w000 w42;
adds dc wb w001 w33;
adds dc w49 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w49,K49;a,b,c,d,e,f,g,h);
#r=50
inline sha256sigma1(w48,w000);
inline sha256sigma0(w35,w001);
adds dc wa w000 w43;
adds dc wb w001 w34;
adds dc w50 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w50,K50;a,b,c,d,e,f,g,h);
#r=51
inline sha256sigma1(w49,w000);
inline sha256sigma0(w36,w001);
adds dc wa w000 w44;
adds dc wb w001 w35;
adds dc w51 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w51,K51;a,b,c,d,e,f,g,h);
#r=52
inline sha256sigma1(w50,w000);
inline sha256sigma0(w37,w001);
adds dc wa w000 w45;
adds dc wb w001 w36;
adds dc w52 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w52,K52;a,b,c,d,e,f,g,h);
#r=53
inline sha256sigma1(w51,w000);
inline sha256sigma0(w38,w001);
adds dc wa w000 w46;
adds dc wb w001 w37;
adds dc w53 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w53,K53;a,b,c,d,e,f,g,h);
#r=54
inline sha256sigma1(w52,w000);
inline sha256sigma0(w39,w001);
adds dc wa w000 w47;
adds dc wb w001 w38;
adds dc w54 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w54,K54;a,b,c,d,e,f,g,h);
#r=55
inline sha256sigma1(w53,w000);
inline sha256sigma0(w40,w001);
adds dc wa w000 w48;
adds dc wb w001 w39;
adds dc w55 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w55,K55;a,b,c,d,e,f,g,h);
#r=56
inline sha256sigma1(w54,w000);
inline sha256sigma0(w41,w001);
adds dc wa w000 w49;
adds dc wb w001 w40;
adds dc w56 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w56,K56;a,b,c,d,e,f,g,h);
#r=57
inline sha256sigma1(w55,w000);
inline sha256sigma0(w42,w001);
adds dc wa w000 w50;
adds dc wb w001 w41;
adds dc w57 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w57,K57;a,b,c,d,e,f,g,h);
#r=58
inline sha256sigma1(w56,w000);
inline sha256sigma0(w43,w001);
adds dc wa w000 w51;
adds dc wb w001 w42;
adds dc w58 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w58,K58;a,b,c,d,e,f,g,h);
#r=59
inline sha256sigma1(w57,w000);
inline sha256sigma0(w44,w001);
adds dc wa w000 w52;
adds dc wb w001 w43;
adds dc w59 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w59,K59;a,b,c,d,e,f,g,h);
#r=60
inline sha256sigma1(w58,w000);
inline sha256sigma0(w45,w001);
adds dc wa w000 w53;
adds dc wb w001 w44;
adds dc w60 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w60,K60;a,b,c,d,e,f,g,h);
#r=61
inline sha256sigma1(w59,w000);
inline sha256sigma0(w46,w001);
adds dc wa w000 w54;
adds dc wb w001 w45;
adds dc w61 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w61,K61;a,b,c,d,e,f,g,h);
#r=62
inline sha256sigma1(w60,w000);
inline sha256sigma0(w47,w001);
adds dc wa w000 w55;
adds dc wb w001 w46;
adds dc w62 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w62,K62;a,b,c,d,e,f,g,h);
#r=63
inline sha256sigma1(w61,w000);
inline sha256sigma0(w48,w001);
adds dc wa w000 w56;
adds dc wb w001 w47;
adds dc w63 wa wb;
inline sha256roundFunction(a,b,c,d,e,f,g,h,w63,K63;a,b,c,d,e,f,g,h);

adds dc a0 a A0;
adds dc a1 b A1;
adds dc a2 c A2;
adds dc a3 d A3;
adds dc a4 e A4;
adds dc a5 f A5;
adds dc a6 g A6;
adds dc a7 h A7;

{
  true
  &&
  true
}
