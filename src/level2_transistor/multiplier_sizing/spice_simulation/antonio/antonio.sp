* Xyce netlist for antonio - 4-2 Compressor
* Version 1.0
* Date: 2025-10-21
* Function: S + 2*C = a + b + c + d


* Simplified MOS Models for Testing
.MODEL NMOS_VTL NMOS (LEVEL=1 VTO=0.5 KP=200E-6)
.MODEL PMOS_VTL PMOS (LEVEL=1 VTO=-0.5 KP=150E-6)

*************************************************************************
* Power Supplies
*************************************************************************
VDD VDD 0 DC 1.2
VSS VSS 0 DC 0

*************************************************************************
* Main circuit: antonio (4-2 Compressor)
*************************************************************************

* Instance _0_ (OR2_X1): w1 = a OR b
M__0__M_i_2 net__1__ZN_neg a VSS VSS NMOS_VTL W=0.210u L=0.050u
M__0__M_i_3 VSS b net__1__ZN_neg VSS NMOS_VTL W=0.210u L=0.050u
M__0__M_i_0 w1 net__1__ZN_neg VSS VSS NMOS_VTL W=0.415u L=0.050u
M__0__M_i_4 net__1__net_0 a net__1__ZN_neg VDD PMOS_VTL W=0.315u L=0.050u
M__0__M_i_5 VDD b net__1__net_0 VDD PMOS_VTL W=0.315u L=0.050u
M__0__M_i_1 w1 net__1__ZN_neg VDD VDD PMOS_VTL W=0.630u L=0.050u

* Instance _1_ (AOI21_X1): _0_ = NOT((a OR b) AND c)
M__1__M_i_1 net__2__net_0 a VSS VSS NMOS_VTL W=0.415u L=0.050u
M__1__M_i_0 _0_ b net__2__net_0 VSS NMOS_VTL W=0.415u L=0.050u
M__1__M_i_2 VSS c _0_ VSS NMOS_VTL W=0.415u L=0.050u
M__1__M_i_4 _0_ a net__2__net_1 VDD PMOS_VTL W=0.630u L=0.050u
M__1__M_i_3 net__2__net_1 b _0_ VDD PMOS_VTL W=0.630u L=0.050u
M__1__M_i_5 VDD c net__2__net_1 VDD PMOS_VTL W=0.630u L=0.050u

* Instance _2_ (INV_X1): w2 = NOT(_0_)
M__2__M_i_0 w2 _0_ VSS VSS NMOS_VTL W=0.415u L=0.050u
M__2__M_i_1 w2 _0_ VDD VDD PMOS_VTL W=0.630u L=0.050u

* ============================================
* Full Adder: (w1, w2, d) -> (S, C)
* ============================================

* Instance _3_ (NAND2_X1): Full_adder__0_ = w1 NAND d
M_FA__3__M_i_1 net_FA__3__net_0 d VSS VSS NMOS_VTL W=0.415u L=0.050u
M_FA__3__M_i_0 Full_adder__0_ w1 net_FA__3__net_0 VSS NMOS_VTL W=0.415u L=0.050u
M_FA__3__M_i_3 Full_adder__0_ d VDD VDD PMOS_VTL W=0.630u L=0.050u
M_FA__3__M_i_2 VDD w1 Full_adder__0_ VDD PMOS_VTL W=0.630u L=0.050u

* Instance _4_ (XNOR2_X1): Full_adder__1_ = w1 XNOR d
M_FA__4__M_i_0 net_FA__4__net_001 w1 net_FA__4__net_000 VSS NMOS_VTL W=0.210u L=0.050u
M_FA__4__M_i_5 VSS d net_FA__4__net_001 VSS NMOS_VTL W=0.210u L=0.050u
M_FA__4__M_i_11 net_FA__4__net_002 net_FA__4__net_000 VSS VSS NMOS_VTL W=0.415u L=0.050u
M_FA__4__M_i_17 Full_adder__1_ w1 net_FA__4__net_002 VSS NMOS_VTL W=0.415u L=0.050u
M_FA__4__M_i_23 net_FA__4__net_002 d Full_adder__1_ VSS NMOS_VTL W=0.415u L=0.050u
M_FA__4__M_i_29 net_FA__4__net_000 w1 VDD VDD PMOS_VTL W=0.315u L=0.050u
M_FA__4__M_i_36 VDD d net_FA__4__net_000 VDD PMOS_VTL W=0.315u L=0.050u
M_FA__4__M_i_42 Full_adder__1_ net_FA__4__net_000 VDD VDD PMOS_VTL W=0.630u L=0.050u
M_FA__4__M_i_48 net_FA__4__net_003 w1 Full_adder__1_ VDD PMOS_VTL W=0.630u L=0.050u
M_FA__4__M_i_53 VDD d net_FA__4__net_003 VDD PMOS_VTL W=0.630u L=0.050u

* Instance _5_ (OAI21_X1): Full_adder__2_ = NOT((w1 OR d) AND w2)
M_FA__5__M_i_1 Full_adder__2_ w1 net_FA__5__net_0 VSS NMOS_VTL W=0.415u L=0.050u
M_FA__5__M_i_0 net_FA__5__net_0 d Full_adder__2_ VSS NMOS_VTL W=0.415u L=0.050u
M_FA__5__M_i_2 VSS w2 net_FA__5__net_0 VSS NMOS_VTL W=0.415u L=0.050u
M_FA__5__M_i_4 net_FA__5__net_1 w1 VDD VDD PMOS_VTL W=0.630u L=0.050u
M_FA__5__M_i_3 Full_adder__2_ d net_FA__5__net_1 VDD PMOS_VTL W=0.630u L=0.050u
M_FA__5__M_i_5 VDD w2 Full_adder__2_ VDD PMOS_VTL W=0.630u L=0.050u

* Instance _6_ (NAND2_X1): C = Full_adder__0_ NAND Full_adder__2_
M_FA__6__M_i_1 net_FA__6__net_0 Full_adder__2_ VSS VSS NMOS_VTL W=0.415u L=0.050u
M_FA__6__M_i_0 C Full_adder__0_ net_FA__6__net_0 VSS NMOS_VTL W=0.415u L=0.050u
M_FA__6__M_i_3 C Full_adder__2_ VDD VDD PMOS_VTL W=0.630u L=0.050u
M_FA__6__M_i_2 VDD Full_adder__0_ C VDD PMOS_VTL W=0.630u L=0.050u

* Instance _7_ (XNOR2_X1): S = w2 XNOR Full_adder__1_
M_FA__7__M_i_0 net_FA__7__net_001 w2 net_FA__7__net_000 VSS NMOS_VTL W=0.210u L=0.050u
M_FA__7__M_i_5 VSS Full_adder__1_ net_FA__7__net_001 VSS NMOS_VTL W=0.210u L=0.050u
M_FA__7__M_i_11 net_FA__7__net_002 net_FA__7__net_000 VSS VSS NMOS_VTL W=0.415u L=0.050u
M_FA__7__M_i_17 S w2 net_FA__7__net_002 VSS NMOS_VTL W=0.415u L=0.050u
M_FA__7__M_i_23 net_FA__7__net_002 Full_adder__1_ S VSS NMOS_VTL W=0.415u L=0.050u
M_FA__7__M_i_29 net_FA__7__net_000 w2 VDD VDD PMOS_VTL W=0.315u L=0.050u
M_FA__7__M_i_36 VDD Full_adder__1_ net_FA__7__net_000 VDD PMOS_VTL W=0.315u L=0.050u
M_FA__7__M_i_42 S net_FA__7__net_000 VDD VDD PMOS_VTL W=0.630u L=0.050u
M_FA__7__M_i_48 net_FA__7__net_003 w2 S VDD PMOS_VTL W=0.630u L=0.050u
M_FA__7__M_i_53 VDD Full_adder__1_ net_FA__7__net_003 VDD PMOS_VTL W=0.630u L=0.050u

* Parasitic capacitances
C_1_ZN net__1__ZN_neg 0 20f
C_1_0 net__1__net_0 0 5f
C_2_0 net__2__net_0 0 5f
C_2_1 net__2__net_1 0 5f
C_FA_3 net_FA__3__net_0 0 5f
C_FA_4_000 net_FA__4__net_000 0 20f
C_FA_4_001 net_FA__4__net_001 0 5f
C_FA_4_002 net_FA__4__net_002 0 5f
C_FA_4_003 net_FA__4__net_003 0 20f
C_FA_5_0 net_FA__5__net_0 0 5f
C_FA_5_1 net_FA__5__net_1 0 5f
C_FA_6_0 net_FA__6__net_0 0 5f
C_FA_7_000 net_FA__7__net_000 0 20f
C_FA_7_001 net_FA__7__net_001 0 10f
C_FA_7_002 net_FA__7__net_002 0 10f
C_FA_7_003 net_FA__7__net_003 0 10f
C_0 _0_ 0 10f
C_W1 w1 0 50f
C_W2 w2 0 20f
C_FA0 Full_adder__0_ 0 20f
C_FA1 Full_adder__1_ 0 20f
C_FA2 Full_adder__2_ 0 5f     


* Initial conditions (all zero)
.IC V(a)=0 V(b)=0 V(c)=0 V(d)=0
.IC V(S)=0 V(C)=0

*************************************************************************
* SIMPLIFIED Test Vectors - 5 Patterns Only
*************************************************************************
* Strategy: Test only 4 output states with minimal transitions
* 
* Time    Pattern  (a,b,c,d)  Sum  S  C   Transition
* 0-30ns    P0     (0,0,0,0)   0   0  0   Initial stable
* 30-60ns   P1     (0,0,0,1)   1   1  0   d↑ → S↑ (测TPLH_D_S)
* 60-90ns   P2     (0,0,1,1)   2   0  1   c↑ → S↓,C↑ (测TPHL_C_S, TPLH_C_C)
* 90-120ns  P3     (0,1,1,1)   3   1  1   b↑ → S↑ (测TPLH_B_S)
* 120-150ns P4     (0,0,0,0)   0   0  0   全↓ → S↓,C↓ (测TPHL_ALL_S, TPHL_ALL_C)


* Input A: always 0 (simplified test)
VA a 0 DC 0

* Input B: rises at 90ns, falls at 120ns (FAST 200ps transitions)
VB b 0 PWL(
+ 0ns 0V
+ 90ns 0V 90.3ns 1.2V
+ 120ns 1.2V 120.3ns 0V
+ 200ns 0V)

* Input C: rises at 60ns, falls at 120.3ns (FAST, STAGGERED fall)
VC c 0 PWL(
+ 0ns 0V
+ 60ns 0V 60.3ns 1.2V
+ 121ns 1.2V 121.3ns 0V
+ 200ns 0V)

* Input D: rises at 30ns, falls at 120.6ns (FAST, STAGGERED fall)
VD d 0 PWL(
+ 0ns 0V
+ 30ns 0V 30.3ns 1.2V
+ 122ns 1.2V 122.3ns 0V
+ 200ns 0V)

* Output loads
CLoad_S S 0 10f
CLoad_C C 0 10f

* Supply decoupling
C_VDD VDD 0 10p
C_VSS VSS 0 10p

*************************************************************************
* Analysis Setup
*************************************************************************

.OPTIONS TIMEINT RELTOL=1e-5 ABSTOL=1e-9 METHOD=TRAP
.OPTIONS NONLIN MAXSTEP=100 SEARCHMETHOD=0
.OPTIONS DEVICE TEMP=27

.OP
.TRAN 0.02ns 600ns 0 0.05ns

*************************************************************************
* Output
*************************************************************************

.PRINT TRAN FORMAT=STD FILE=antonio_waveforms.prn 
+ V(a) V(b) V(c) V(d) V(S) V(C)

.PRINT TRAN FORMAT=CSV FILE=antonio_power.csv
+ TIME I(VDD) {-V(VDD)*I(VDD)}

*************************************************************************
* SIMPLIFIED Timing Measurements
*************************************************************************

* Pattern 1: d rises at 32ns, S rises
.MEASURE TRAN T_D_R WHEN V(d)=0.6 RISE=1
.MEASURE TRAN T_S_R1 WHEN V(S)=0.6 RISE=1
.MEASURE TRAN TPLH_D_S PARAM='T_S_R1-T_D_R'

* Pattern 2: c rises at 62ns, S falls and C rises
.MEASURE TRAN T_C_R WHEN V(c)=0.6 RISE=1
.MEASURE TRAN T_S_F1 WHEN V(S)=0.6 FALL=1
.MEASURE TRAN T_C_R1 WHEN V(C)=0.6 RISE=1
.MEASURE TRAN TPHL_C_S PARAM='T_S_F1-T_C_R'
.MEASURE TRAN TPLH_C_C PARAM='T_C_R1-T_C_R'

* Pattern 3: b rises at 92ns, S rises
.MEASURE TRAN T_B_R WHEN V(b)=0.6 RISE=1
.MEASURE TRAN T_S_R2 WHEN V(S)=0.6 RISE=2
.MEASURE TRAN TPLH_B_S PARAM='T_S_R2-T_B_R'

* Pattern 4: All fall at 122ns, S and C fall
.MEASURE TRAN T_BCD_F WHEN V(d)=0.6 FALL=1
.MEASURE TRAN T_S_F2 WHEN V(S)=0.6 FALL=2
.MEASURE TRAN T_C_F1 WHEN V(C)=0.6 FALL=1
.MEASURE TRAN TPHL_BCD_S PARAM='T_BCD_F-T_S_F2'
.MEASURE TRAN TPHL_BCD_C PARAM='T_C_F1-T_BCD_F'

* Average delays
.MEASURE TRAN AVG_TPLH_S PARAM='(TPLH_D_S+TPLH_B_S)/2'
.MEASURE TRAN AVG_TPHL_S PARAM='(TPHL_C_S+TPHL_BCD_S)/2'
.MEASURE TRAN AVG_DELAY_S PARAM='(AVG_TPLH_S+AVG_TPHL_S)/2'

.MEASURE TRAN AVG_TPLH_C PARAM='TPLH_C_C'
.MEASURE TRAN AVG_TPHL_C PARAM='TPHL_BCD_C'
.MEASURE TRAN AVG_DELAY_C PARAM='(AVG_TPLH_C+AVG_TPHL_C)/2'

* Rise/Fall times (10%-90%)
.MEASURE TRAN T_S_10R WHEN V(S)=0.12 RISE=1
.MEASURE TRAN T_S_90R WHEN V(S)=1.08 RISE=1
.MEASURE TRAN RISE_S PARAM='T_S_90R-T_S_10R'

.MEASURE TRAN T_S_90F WHEN V(S)=1.08 FALL=1
.MEASURE TRAN T_S_10F WHEN V(S)=0.12 FALL=1
.MEASURE TRAN FALL_S PARAM='T_S_10F-T_S_90F'

.MEASURE TRAN T_C_10R WHEN V(C)=0.12 RISE=1
.MEASURE TRAN T_C_90R WHEN V(C)=1.08 RISE=1
.MEASURE TRAN RISE_C PARAM='T_C_90R-T_C_10R'

.MEASURE TRAN T_C_90F WHEN V(C)=1.08 FALL=1
.MEASURE TRAN T_C_10F WHEN V(C)=0.12 FALL=1
.MEASURE TRAN FALL_C PARAM='T_C_10F-T_C_90F'

*************************************************************************
* Power Measurements
*************************************************************************

* Dynamic power (during each transition, 20ns window)
.MEASURE TRAN P_DYN_1 AVG {-V(VDD)*I(VDD)} FROM=10ns TO=20ns
.MEASURE TRAN P_DYN_2 AVG {-V(VDD)*I(VDD)} FROM=30ns TO=50ns
.MEASURE TRAN P_DYN_3 AVG {-V(VDD)*I(VDD)} FROM=90ns TO=110ns
.MEASURE TRAN P_DYN_4 AVG {-V(VDD)*I(VDD)} FROM=120ns TO=140ns
.MEASURE TRAN P_DYNAMIC_AVG PARAM='(P_DYN_1+P_DYN_2+P_DYN_3+P_DYN_4)/4'

* Static power (stable periods)
.MEASURE TRAN P_STATIC_1 AVG {-V(VDD)*I(VDD)} FROM=10ns TO=28ns
.MEASURE TRAN P_STATIC_2 AVG {-V(VDD)*I(VDD)} FROM=52ns TO=58ns
.MEASURE TRAN P_STATIC_3 AVG {-V(VDD)*I(VDD)} FROM=82ns TO=88ns
.MEASURE TRAN P_STATIC_4 AVG {-V(VDD)*I(VDD)} FROM=142ns TO=148ns
.MEASURE TRAN P_STATIC_AVG PARAM='(P_STATIC_1+P_STATIC_2+P_STATIC_3+P_STATIC_4)/4'

* Total power
.MEASURE TRAN P_TOTAL_CALC PARAM='P_DYNAMIC_AVG+P_STATIC_AVG'
.MEASURE TRAN P_TOTAL_AVG AVG {-V(VDD)*I(VDD)} FROM=30ns TO=600ns
.MEASURE TRAN P_PEAK MAX {-V(VDD)*I(VDD)} FROM=5ns TO=150ns

* Energy
.MEASURE TRAN E_TOTAL INTEG {-V(VDD)*I(VDD)} FROM=5ns TO=150ns
.MEASURE TRAN E_PER_OP PARAM='E_TOTAL/4'

* Power breakdown
.MEASURE TRAN PWR_DYN_PCT PARAM='100*P_DYNAMIC_AVG/(P_DYNAMIC_AVG+P_STATIC_AVG)'
.MEASURE TRAN PWR_STAT_PCT PARAM='100*P_STATIC_AVG/(P_DYNAMIC_AVG+P_STATIC_AVG)'

*************************************************************************
* End of Netlist
*************************************************************************
.END