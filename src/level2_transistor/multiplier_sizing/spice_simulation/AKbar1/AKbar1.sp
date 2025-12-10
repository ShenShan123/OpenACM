* Xyce netlist for akbar1 - Approximate 4-2 Compressor
* Version 1.0
* Date: 2025-10-21
* Design: akbar1 (24 transistors + buffer)
* Logic: S = (a XNOR b) NAND (c XNOR d), cout = d


* Simplified MOS Models for Testing
.MODEL NMOS_VTL NMOS (LEVEL=1 VTO=0.5 KP=200E-6)
.MODEL PMOS_VTL PMOS (LEVEL=1 VTO=-0.5 KP=150E-6)

*************************************************************************
* Power supplies
*************************************************************************
VDD VDD 0 DC 1.2
VSS VSS 0 DC 0

*************************************************************************
* Main circuit: akbar1
*************************************************************************

* Instance _2_ (XNOR2_X1): computes a XNOR b -> _0_
M__2__M_i_0 net__2__net_001 a net__2__net_000 VSS NMOS_VTL W=0.210u L=0.050u
M__2__M_i_5 VSS b net__2__net_001 VSS NMOS_VTL W=0.210u L=0.050u
M__2__M_i_11 net__2__net_002 net__2__net_000 VSS VSS NMOS_VTL W=0.415u L=0.050u
M__2__M_i_17 _0_ a net__2__net_002 VSS NMOS_VTL W=0.415u L=0.050u
M__2__M_i_23 net__2__net_002 b _0_ VSS NMOS_VTL W=0.415u L=0.050u
M__2__M_i_29 net__2__net_000 a VDD VDD PMOS_VTL W=0.315u L=0.050u
M__2__M_i_36 VDD b net__2__net_000 VDD PMOS_VTL W=0.315u L=0.050u
M__2__M_i_42 _0_ net__2__net_000 VDD VDD PMOS_VTL W=0.630u L=0.050u
M__2__M_i_48 net__2__net_003 a _0_ VDD PMOS_VTL W=0.630u L=0.050u
M__2__M_i_53 VDD b net__2__net_003 VDD PMOS_VTL W=0.630u L=0.050u

* Instance _3_ (XNOR2_X1): computes c XNOR d -> _1_
M__3__M_i_0 net__3__net_001 c net__3__net_000 VSS NMOS_VTL W=0.210u L=0.050u
M__3__M_i_5 VSS d net__3__net_001 VSS NMOS_VTL W=0.210u L=0.050u
M__3__M_i_11 net__3__net_002 net__3__net_000 VSS VSS NMOS_VTL W=0.415u L=0.050u
M__3__M_i_17 _1_ c net__3__net_002 VSS NMOS_VTL W=0.415u L=0.050u
M__3__M_i_23 net__3__net_002 d _1_ VSS NMOS_VTL W=0.415u L=0.050u
M__3__M_i_29 net__3__net_000 c VDD VDD PMOS_VTL W=0.315u L=0.050u
M__3__M_i_36 VDD d net__3__net_000 VDD PMOS_VTL W=0.315u L=0.050u
M__3__M_i_42 _1_ net__3__net_000 VDD VDD PMOS_VTL W=0.630u L=0.050u
M__3__M_i_48 net__3__net_003 c _1_ VDD PMOS_VTL W=0.630u L=0.050u
M__3__M_i_53 VDD d net__3__net_003 VDD PMOS_VTL W=0.630u L=0.050u

* Instance _4_ (NAND2_X1): computes S = _0_ NAND _1_
M__4__M_i_1 net__4__net_0 _1_ VSS VSS NMOS_VTL W=0.415u L=0.050u
M__4__M_i_0 S _0_ net__4__net_0 VSS NMOS_VTL W=0.415u L=0.050u
M__4__M_i_3 S _1_ VDD VDD PMOS_VTL W=0.630u L=0.050u
M__4__M_i_2 VDD _0_ S VDD PMOS_VTL W=0.630u L=0.050u

* Instance _5_ (BUF_X1)
*XBUF_CARRY d cout VDD VSS BUF_X1
M__5__M_i_2 VSS d cout_neg VSS NMOS_VTL W=0.210u L=0.050u
M__5__M_i_0 cout cout_neg VSS VSS NMOS_VTL W=0.415u L=0.050u
M__5__M_i_3 VDD d cout_neg VDD PMOS_VTL W=0.315u L=0.050u
M__5__M_i_1 cout cout_neg VDD VDD PMOS_VTL W=0.630u L=0.050u

*************************************************************************
* Parasitic capacitances
*************************************************************************
C_NET2_000 net__2__net_000 0 5f
C_NET2_001 net__2__net_001 0 5f
C_NET2_002 net__2__net_002 0 5f
C_NET2_003 net__2__net_003 0 10f
C_NET3_000 net__3__net_000 0 5f
C_NET3_001 net__3__net_001 0 5f
C_NET3_002 net__3__net_002 0 5f
C_NET3_003 net__3__net_003 0 10f
C_NET4_0 net__4__net_0 0 5f
C_NET4_COUT_NEG cout_neg 0 5f
C_INT_0 _0_ 0 5f
C_INT_1 _1_ 0 5f

*************************************************************************
* Initial conditions
*************************************************************************
.IC V(_0_)=0.6 V(_1_)=0.6
.IC V(S)=1.2 V(cout)=0.0

*************************************************************************
* Input test vectors
*************************************************************************
VA a 0 PWL(
+ 0ns 0V
+ 60ns 0V 70ns 1.2V
+ 200ns 1.2V)

VB b 0 PWL(
+ 0ns 0V
+ 20ns 0V 30ns 1.2V
+ 200ns 1.2V)

VC c 0 PWL(
+ 0ns 0V
+ 40ns 0V 50ns 1.2V
+ 100ns 1.2V 110ns 0V
+ 200ns 0V)

VD d 0 PWL(
+ 0ns 0V 10ns 1.2V
+ 80ns 1.2V 103ns 0V
+ 200ns 0V)

*************************************************************************
* Output loads
*************************************************************************
CLoad_S S 0 10f
CLoad_cout cout 0 10f

*************************************************************************
* Power supply decoupling
*************************************************************************
C_VDD VDD 0 10p
C_VSS VSS 0 10p

*************************************************************************
* Analysis configuration - Relaxed for better convergence
*************************************************************************
.OPTIONS TIMEINT RELTOL=1e-2 ABSTOL=1e-5 METHOD=TRAP MINBREAK=1e-14
.OPTIONS NONLIN MAXSTEP=100 SEARCHMETHOD=0 
.OPTIONS NONLIN-TRAN MAXSTEP=100 SEARCHMETHOD=0
.OPTIONS DEVICE TEMP=27 GMIN=1e-15

.OP
.TRAN 0.1ns 220ns 0ns 0.05ns

*************************************************************************
* Output files
*************************************************************************
.PRINT TRAN FORMAT=STD FILE=akbar1_waveforms.prn 
+ V(a) V(b) V(c) V(d) V(S) V(cout) V(_0_) V(_1_)

.PRINT TRAN FORMAT=CSV FILE=akbar1_power.csv
+ TIME I(VDD) {V(VDD)*I(VDD)} {-V(VDD)*I(VDD)}

*************************************************************************
* Performance measurements - Timing analysis
*************************************************************************

* Pattern 1: d rises 0→10ns, both S and cout should rise (0000→0001)
.MEASURE TRAN T_D_R1 WHEN V(d)=0.6 RISE=1 TD=2ns
.MEASURE TRAN T_cout_R1 WHEN V(cout)=0.6 RISE=1 TD=2ns
.MEASURE TRAN T_S_R1 WHEN V(S)=0.6 RISE=1 TD=2ns
.MEASURE TRAN TPLH_D_cout_P1 PARAM='T_cout_R1-T_D_R1'
.MEASURE TRAN TPLH_D_S_P1 PARAM='T_S_R1-T_D_R1'

* Pattern 4: a rises 60→70ns, S falls (0111→1111)
.MEASURE TRAN T_A_R1 WHEN V(a)=0.6 RISE=1 TD=62ns
.MEASURE TRAN T_S_F1 WHEN V(S)=0.6 FALL=1 TD=62ns
.MEASURE TRAN TPHL_A_S_P4 PARAM='T_S_F1-T_A_R1'

* Pattern 5: d falls 80→90ns, S rises and cout falls (1111→1110)
.MEASURE TRAN T_D_F1 WHEN V(d)=0.6 FALL=1 TD=82ns
.MEASURE TRAN T_S_R2 WHEN V(S)=0.6 RISE=1 TD=82ns
.MEASURE TRAN T_cout_F1 WHEN V(cout)=0.6 FALL=1 TD=82ns
.MEASURE TRAN TPLH_D_S_P5 PARAM='T_S_R2-T_D_F1'
.MEASURE TRAN TPHL_D_cout_P5 PARAM='T_cout_F1-T_D_F1'

* Pattern 6: c falls 100→110ns, S falls (1110→1100)
.MEASURE TRAN T_C_F2 WHEN V(c)=0.6 FALL=1 TD=102ns
.MEASURE TRAN T_S_F2 WHEN V(S)=0.6 FALL=1 TD=102ns
.MEASURE TRAN TPHL_C_S_P6 PARAM='T_S_F2-T_C_F2'

* Average delays
.MEASURE TRAN AVG_DELAY_S_RISE PARAM='(TPLH_D_S_P1+TPLH_D_S_P5)/2'
.MEASURE TRAN AVG_DELAY_S_FALL PARAM='(TPHL_A_S_P4+TPHL_C_S_P6)/2'
.MEASURE TRAN AVG_DELAY_S PARAM='(AVG_DELAY_S_RISE+AVG_DELAY_S_FALL)/2'
.MEASURE TRAN AVG_DELAY_cout PARAM='(TPLH_D_cout_P1+TPHL_D_cout_P5)/2'

*************************************************************************
* Rise/Fall time measurements
*************************************************************************
.MEASURE TRAN T_S_10 WHEN V(S)=0.12 RISE=1 TD=2ns
.MEASURE TRAN T_S_90 WHEN V(S)=1.08 RISE=1 TD=2ns
.MEASURE TRAN RISE_TIME_S PARAM='T_S_90-T_S_10'

.MEASURE TRAN T_cout_10 WHEN V(cout)=0.12 RISE=1 TD=2ns
.MEASURE TRAN T_cout_90 WHEN V(cout)=1.08 RISE=1 TD=2ns
.MEASURE TRAN RISE_TIME_cout PARAM='T_cout_90-T_cout_10'

*************************************************************************
* Power measurements
*************************************************************************
.MEASURE TRAN P_AVG AVG {-V(VDD)*I(VDD)} FROM=6ns TO=220ns
.MEASURE TRAN P_PEAK MAX {-V(VDD)*I(VDD)} FROM=0ns TO=200ns
.MEASURE TRAN E_TOTAL INTEG {-V(VDD)*I(VDD)} FROM=0ns TO=200ns

* Dynamic power
.MEASURE TRAN P_DYN1 AVG {-V(VDD)*I(VDD)} FROM=8ns TO=18ns
.MEASURE TRAN P_DYN2 AVG {-V(VDD)*I(VDD)} FROM=58ns TO=78ns
.MEASURE TRAN P_DYN3 AVG {-V(VDD)*I(VDD)} FROM=88ns TO=108ns
.MEASURE TRAN P_DYNAMIC_AVG PARAM='(P_DYN1+P_DYN2+P_DYN3)/3'

* Static power
.MEASURE TRAN P_STATIC AVG {-V(VDD)*I(VDD)} FROM=150ns TO=195ns

*************************************************************************
* Verification measurements
*************************************************************************
.MEASURE TRAN V_D_15NS FIND V(d) AT=15ns
.MEASURE TRAN V_cout_15NS FIND V(cout) AT=15ns
.MEASURE TRAN V_D_95NS FIND V(d) AT=95ns
.MEASURE TRAN V_cout_95NS FIND V(cout) AT=95ns

.END

