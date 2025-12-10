* Xyce netlist for akbar2 - Approximate 4-2 Compressor
* Date: 2025-10-21
* Design: akbar2 (34 transistors)
* Logic: S = (c XNOR d) NAND (a XNOR b)
*        cout = (a AND b) OR (c AND d)


* Simplified MOS Models for Testing
.MODEL NMOS_VTL NMOS (LEVEL=1 VTO=0.5 KP=200E-6)
.MODEL PMOS_VTL PMOS (LEVEL=1 VTO=-0.5 KP=150E-6)

*************************************************************************
* Power supplies
*************************************************************************
VDD VDD 0 DC 1.2
VSS VSS 0 DC 0

*************************************************************************
* Main circuit: akbar2 (34 transistors)
*************************************************************************

* instance : _3_ (XNOR2_X1): computes c XNOR d -> _1_
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

* Instance _4_ (XNOR2_X1): computes a XNOR b -> _2_
M__4__M_i_0 net__4__net_001 a net__4__net_000 VSS NMOS_VTL W=0.210u L=0.050u
M__4__M_i_5 VSS b net__4__net_001 VSS NMOS_VTL W=0.210u L=0.050u
M__4__M_i_11 net__4__net_002 net__4__net_000 VSS VSS NMOS_VTL W=0.415u L=0.050u
M__4__M_i_17 _2_ a net__4__net_002 VSS NMOS_VTL W=0.415u L=0.050u
M__4__M_i_23 net__4__net_002 b _2_ VSS NMOS_VTL W=0.415u L=0.050u
M__4__M_i_29 net__4__net_000 a VDD VDD PMOS_VTL W=0.315u L=0.050u
M__4__M_i_36 VDD b net__4__net_000 VDD PMOS_VTL W=0.315u L=0.050u
M__4__M_i_42 _2_ net__4__net_000 VDD VDD PMOS_VTL W=0.630u L=0.050u
M__4__M_i_48 net__4__net_003 a _2_ VDD PMOS_VTL W=0.630u L=0.050u
M__4__M_i_53 VDD b net__4__net_003 VDD PMOS_VTL W=0.630u L=0.050u

* Instance _5_ (NAND2_X1): computes S = _1_ NAND _2_
M__5__M_i_1 net__5__net_0 _2_ VSS VSS NMOS_VTL W=0.415u L=0.050u
M__5__M_i_0 S _1_ net__5__net_0 VSS NMOS_VTL W=0.415u L=0.050u
M__5__M_i_3 S _2_ VDD VDD PMOS_VTL W=0.630u L=0.050u
M__5__M_i_2 VDD _1_ S VDD PMOS_VTL W=0.630u L=0.050u

* Instance _6_ (AOI22_X1): computes _0_ = NOT((a AND b) OR (c AND d))
M__6__M_i_3 net__6__net_1 d VSS VSS NMOS_VTL W=0.415u L=0.050u
M__6__M_i_2 _0_ c net__6__net_1 VSS NMOS_VTL W=0.415u L=0.050u
M__6__M_i_0 net__6__net_0 a _0_ VSS NMOS_VTL W=0.415u L=0.050u
M__6__M_i_1 VSS b net__6__net_0 VSS NMOS_VTL W=0.415u L=0.050u
M__6__M_i_7 VDD d net__6__net_2 VDD PMOS_VTL W=0.630u L=0.050u
M__6__M_i_6 net__6__net_2 c VDD VDD PMOS_VTL W=0.630u L=0.050u
M__6__M_i_4 _0_ a net__6__net_2 VDD PMOS_VTL W=0.630u L=0.050u
M__6__M_i_5 net__6__net_2 b _0_ VDD PMOS_VTL W=0.630u L=0.050u

* Instance _7_ (INV_X1): computes cout = NOT(_0_)
M__7__M_i_0 cout _0_ VSS VSS NMOS_VTL W=0.415u L=0.050u
M__7__M_i_1 cout _0_ VDD VDD PMOS_VTL W=0.630u L=0.050u

*************************************************************************
* Parasitic capacitances
*************************************************************************
C_NET3_000 net__3__net_000 0 5f
C_NET3_001 net__3__net_001 0 5f
C_NET3_002 net__3__net_002 0 5f
C_NET3_003 net__3__net_003 0 10f
C_NET4_000 net__4__net_000 0 5f
C_NET4_001 net__4__net_001 0 5f
C_NET4_002 net__4__net_002 0 5f
C_NET4_003 net__4__net_003 0 10f
C_NET5_0 net__5__net_0 0 5f
C_NET6_0 net__6__net_0 0 5f
C_NET6_1 net__6__net_1 0 5f
C_NET6_2 net__6__net_2 0 10f
C_INT_0 _0_ 0 5f
C_INT_1 _1_ 0 5f
C_INT_2 _2_ 0 5f

*************************************************************************
* Initial conditions
*************************************************************************
.IC V(_0_)=1.2 V(_1_)=1.2 V(_2_)=1.2
.IC V(S)=0.0 V(cout)=0.0

*************************************************************************
* Simplified test vectors - Focus on key transitions
*************************************************************************
* Pattern sequence (slower transitions for stability):
* Time | a b c d | Expected S | Expected cout
* 0ns  | 0 0 0 0 |     0      |      0
* 20ns | 0 0 0 1 |     1      |      0        (d rises)
* 60ns | 0 0 1 1 |     0      |      1        (c rises)
* 100ns| 0 1 1 1 |     1      |      1        (b rises)
* 140ns| 1 1 1 1 |     0      |      1        (a rises)
* 180ns| 1 1 1 0 |     1      |      1        (d falls)

VA a 0 PWL(
+ 0ns 0V
+ 130ns 0V 145ns 1.2V
+ 250ns 1.2V)

VB b 0 PWL(
+ 0ns 0V
+ 90ns 0V 105ns 1.2V
+ 250ns 1.2V)

VC c 0 PWL(
+ 0ns 0V
+ 50ns 0V 66ns 1.2V
+ 250ns 1.2V)

VD d 0 PWL(
+ 0ns 0V 10ns 1.2V
+ 165ns 1.2V 180ns 0V
+ 250ns 0V)

*************************************************************************
* Output loads
*************************************************************************
CLoad_S S 0 5f
CLoad_cout cout 0 5f

*************************************************************************
* Power supply decoupling
*************************************************************************
C_VDD VDD 0 10p
C_VSS VSS 0 10p

*************************************************************************
* Analysis configuration
*************************************************************************
.OPTIONS TIMEINT RELTOL=1e-3 ABSTOL=1e-6 METHOD=TRAP
.OPTIONS NONLIN MAXSTEP=50 SEARCHMETHOD=0
.OPTIONS DEVICE TEMP=27

.OP
.TRAN 0.1ns 250ns

*************************************************************************
* Output files
*************************************************************************
.PRINT TRAN FORMAT=STD FILE=akbar2_waveforms.prn 
+ V(a) V(b) V(c) V(d) V(S) V(cout) V(_0_) V(_1_) V(_2_)

.PRINT TRAN FORMAT=CSV FILE=akbar2_power.csv
+ TIME I(VDD) {V(VDD)*I(VDD)} {-V(VDD)*I(VDD)}

*************************************************************************
* Simple delay measurements - Only first occurrence of each transition
*************************************************************************

* Pattern 1: d rises at 10ns (0000→0001)
.MEASURE TRAN T_D_R WHEN V(d)=0.6 RISE=1
.MEASURE TRAN T_S_R1 WHEN V(S)=0.6 RISE=1
.MEASURE TRAN TPLH_D_S_P1 PARAM='T_S_R1-T_D_R'

* Pattern 2: c rises at 60ns (0001→0011)
.MEASURE TRAN T_C_R WHEN V(c)=0.6 RISE=1
.MEASURE TRAN T_S_F1 WHEN V(S)=0.6 FALL=1
.MEASURE TRAN T_cout_R WHEN V(cout)=0.6 RISE=1
.MEASURE TRAN TPHL_C_S_P2 PARAM='T_S_F1-T_C_R'
.MEASURE TRAN TPLH_C_cout_P2 PARAM='T_cout_R-T_C_R'

* Pattern 3: b rises at 100ns (0011→0111)
.MEASURE TRAN T_B_R WHEN V(b)=0.6 RISE=1
.MEASURE TRAN T_S_R2 WHEN V(S)=0.6 RISE=2
.MEASURE TRAN TPLH_B_S_P3 PARAM='T_S_R2-T_B_R'

* Pattern 4: a rises at 140ns (0111→1111)
.MEASURE TRAN T_A_R WHEN V(a)=0.6 RISE=1
.MEASURE TRAN T_S_F2 WHEN V(S)=0.6 FALL=2
.MEASURE TRAN TPHL_A_S_P4 PARAM='T_S_F2-T_A_R'

* Pattern 5: d falls at 180ns (1111→1110)
.MEASURE TRAN T_D_F WHEN V(d)=0.6 FALL=1
.MEASURE TRAN T_S_R3 WHEN V(S)=0.6 RISE=3
.MEASURE TRAN TPLH_D_S_P5 PARAM='T_S_R3-T_D_F'

* Average delays
.MEASURE TRAN AVG_DELAY_S_RISE PARAM='(TPLH_D_S_P1+TPLH_B_S_P3+TPLH_D_S_P5)/3'
.MEASURE TRAN AVG_DELAY_S_FALL PARAM='(TPHL_C_S_P2+TPHL_A_S_P4)/2'
.MEASURE TRAN AVG_DELAY_S PARAM='(AVG_DELAY_S_RISE+AVG_DELAY_S_FALL)/2'

.MEASURE TRAN AVG_DELAY_cout PARAM='TPLH_C_cout_P2'

*************************************************************************
* Rise/Fall time measurements
*************************************************************************
.MEASURE TRAN T_S_10_R WHEN V(S)=0.12 RISE=1
.MEASURE TRAN T_S_90_R WHEN V(S)=1.08 RISE=1
.MEASURE TRAN RISE_TIME_S PARAM='T_S_90_R-T_S_10_R'

.MEASURE TRAN T_S_90_F WHEN V(S)=1.08 FALL=1
.MEASURE TRAN T_S_10_F WHEN V(S)=0.12 FALL=1
.MEASURE TRAN FALL_TIME_S PARAM='T_S_10_F-T_S_90_F'

.MEASURE TRAN T_cout_10_R WHEN V(cout)=0.12 RISE=1
.MEASURE TRAN T_cout_90_R WHEN V(cout)=1.08 RISE=1
.MEASURE TRAN RISE_TIME_cout PARAM='T_cout_90_R-T_cout_10_R'

*************************************************************************
* FIXED: Power measurements with proper time windows
*************************************************************************

* Dynamic power during switching windows (covering full transitions)
* Pattern 1: d rises ~10-20ns
.MEASURE TRAN P_DYN1 AVG {-V(VDD)*I(VDD)} FROM=30ns TO=50ns

* Pattern 2: c rises ~60ns
.MEASURE TRAN P_DYN2 AVG {-V(VDD)*I(VDD)} FROM=50ns TO=70ns

* Pattern 3: b rises ~100ns
.MEASURE TRAN P_DYN3 AVG {-V(VDD)*I(VDD)} FROM=98ns TO=120ns

* Pattern 4: a rises ~140ns
.MEASURE TRAN P_DYN4 AVG {-V(VDD)*I(VDD)} FROM=138ns TO=160ns

* Pattern 5: d falls ~180ns
.MEASURE TRAN P_DYN5 AVG {-V(VDD)*I(VDD)} FROM=178ns TO=200ns

* Average dynamic power across all switching events
.MEASURE TRAN P_DYNAMIC_AVG PARAM='(P_DYN1+P_DYN2+P_DYN3+P_DYN4+P_DYN5)/5'

* Static/leakage power during stable periods
* Period 1: between d and c transitions (stable from 10-30ns)
.MEASURE TRAN P_LEAK1 AVG {-V(VDD)*I(VDD)} FROM=10ns TO=30ns

* Period 2: between b and a transitions (stable from 100-110ns)
.MEASURE TRAN P_LEAK2 AVG {-V(VDD)*I(VDD)} FROM=100ns TO=110ns

* Period 3: after all transitions settle (stable from 210-240ns)
.MEASURE TRAN P_LEAK3 AVG {-V(VDD)*I(VDD)} FROM=210ns TO=240ns

* Average static power
.MEASURE TRAN P_STATIC_AVG PARAM='(P_LEAK1+P_LEAK2+P_LEAK3)/3'

* Total power and energy
.MEASURE TRAN P_AVG AVG {-V(VDD)*I(VDD)} FROM=4ns TO=180ns
.MEASURE TRAN P_PEAK MAX {-V(VDD)*I(VDD)} FROM=0ns TO=250ns

.MEASURE TRAN E_TOTAL INTEG {-V(VDD)*I(VDD)} FROM=0ns TO=250ns

*************************************************************************
* Verification measurements
*************************************************************************
.MEASURE TRAN V_S_AT_30NS FIND V(S) AT=30ns
.MEASURE TRAN V_cout_AT_30NS FIND V(cout) AT=30ns
.MEASURE TRAN V_S_AT_80NS FIND V(S) AT=80ns
.MEASURE TRAN V_cout_AT_80NS FIND V(cout) AT=80ns
.MEASURE TRAN V_S_AT_160NS FIND V(S) AT=160ns
.MEASURE TRAN V_cout_AT_160NS FIND V(cout) AT=160ns

.END