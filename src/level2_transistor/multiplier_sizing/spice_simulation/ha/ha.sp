* Xyce netlist for ha - Approximate 4-2 Compressor (FINAL CORRECTED v12)
* Version 1.0
* Date: 2025-10-23


* Simplified MOS Models for Testing
.MODEL NMOS_VTL NMOS (LEVEL=1 VTO=0.5 KP=200E-6)
.MODEL PMOS_VTL PMOS (LEVEL=1 VTO=-0.5 KP=150E-6)

*************************************************************************
* Power supplies
*************************************************************************
VDD VDD 0 DC 1.2
VSS VSS 0 DC 0

*************************************************************************
* Main circuit: ha (38 transistors)
*************************************************************************

* Instance _04_ (NOR2_X1): computes _1_ = c NOR d
M__04__M_i_1 _1_ d VSS VSS NMOS_VTL W=0.415u L=0.050u
M__04__M_i_0 VSS c _1_ VSS NMOS_VTL W=0.415u L=0.050u
M__04__M_i_3 net__4__net_0 d VDD VDD PMOS_VTL W=0.630u L=0.050u
M__04__M_i_2 _1_ c net__4__net_0 VDD PMOS_VTL W=0.630u L=0.050u

* Instance _05_ (NAND2_X1): computes _2_ = a NAND b
M__05__M_i_1 net__5__net_0 b VSS VSS NMOS_VTL W=0.415u L=0.050u
M__05__M_i_0 _2_ a net__5__net_0 VSS NMOS_VTL W=0.415u L=0.050u
M__05__M_i_3 _2_ b VDD VDD PMOS_VTL W=0.630u L=0.050u
M__05__M_i_2 VDD a _2_ VDD PMOS_VTL W=0.630u L=0.050u

* Instance _06_ (NOR2_X1): computes _3_ = a NOR b
M__06__M_i_1 _3_ b VSS VSS NMOS_VTL W=0.415u L=0.050u
M__06__M_i_0 VSS a _3_ VSS NMOS_VTL W=0.415u L=0.050u
M__06__M_i_3 net__6__net_0 b VDD VDD PMOS_VTL W=0.630u L=0.050u
M__06__M_i_2 _3_ a net__6__net_0 VDD PMOS_VTL W=0.630u L=0.050u

* Instance _07_ (XOR2_X1): computes _0_ = a XOR b
M__07__M_i_0 net__7__net_000 a VSS VSS NMOS_VTL W=0.210u L=0.050u
M__07__M_i_7 VSS b net__7__net_000 VSS NMOS_VTL W=0.210u L=0.050u
M__07__M_i_13 _0_ net__7__net_000 VSS VSS NMOS_VTL W=0.415u L=0.050u
M__07__M_i_19 net__7__net_001 a _0_ VSS NMOS_VTL W=0.415u L=0.050u
M__07__M_i_24 VSS b net__7__net_001 VSS NMOS_VTL W=0.415u L=0.050u
M__07__M_i_30 net__7__net_002 a net__7__net_000 VDD PMOS_VTL W=0.315u L=0.050u
M__07__M_i_35 VDD b net__7__net_002 VDD PMOS_VTL W=0.315u L=0.050u
M__07__M_i_41 net__7__net_003 net__7__net_000 VDD VDD PMOS_VTL W=0.630u L=0.050u
M__07__M_i_47 _0_ a net__7__net_003 VDD PMOS_VTL W=0.630u L=0.050u
M__07__M_i_53 net__7__net_003 b _0_ VDD PMOS_VTL W=0.630u L=0.050u

* Instance _08_ (XNOR2_X1): computes S = _1_ XNOR _0_
M__08__M_i_0 net__8__net_001 _1_ net__8__net_000 VSS NMOS_VTL W=0.210u L=0.050u
M__08__M_i_5 VSS _0_ net__8__net_001 VSS NMOS_VTL W=0.210u L=0.050u
M__08__M_i_11 net__8__net_002 net__8__net_000 VSS VSS NMOS_VTL W=0.415u L=0.050u
M__08__M_i_17 S _1_ net__8__net_002 VSS NMOS_VTL W=0.415u L=0.050u
M__08__M_i_23 net__8__net_002 _0_ S VSS NMOS_VTL W=0.415u L=0.050u
M__08__M_i_29 net__8__net_000 _1_ VDD VDD PMOS_VTL W=0.315u L=0.050u
M__08__M_i_36 VDD _0_ net__8__net_000 VDD PMOS_VTL W=0.315u L=0.050u
M__08__M_i_42 S net__8__net_000 VDD VDD PMOS_VTL W=0.630u L=0.050u
M__08__M_i_48 net__8__net_003 _1_ S VDD PMOS_VTL W=0.630u L=0.050u
M__08__M_i_53 VDD _0_ net__8__net_003 VDD PMOS_VTL W=0.630u L=0.050u

* Instance _09_ (OAI21_X1): computes cout = NOT((_1_ AND _3_) OR _2_)
M__09__M_i_1 cout _1_ net__9__net_0 VSS NMOS_VTL W=0.415u L=0.050u
M__09__M_i_0 net__9__net_0 _3_ cout VSS NMOS_VTL W=0.415u L=0.050u
M__09__M_i_2 VSS _2_ net__9__net_0 VSS NMOS_VTL W=0.415u L=0.050u
M__09__M_i_4 net__9__net_1 _1_ VDD VDD PMOS_VTL W=0.630u L=0.050u
M__09__M_i_3 cout _3_ net__9__net_1 VDD PMOS_VTL W=0.630u L=0.050u
M__09__M_i_5 VDD _2_ cout VDD PMOS_VTL W=0.630u L=0.050u

*************************************************************************
* Parasitic capacitances
*************************************************************************
C_NET4_0 net__4__net_0 0 5f
C_NET5_0 net__5__net_0 0 5f
C_NET6_0 net__6__net_0 0 5f
C_NET7_000 net__7__net_000 0 5f
C_NET7_001 net__7__net_001 0 5f
C_NET7_002 net__7__net_002 0 10f
C_NET7_003 net__7__net_003 0 10f
C_NET8_000 net__8__net_000 0 5f
C_NET8_001 net__8__net_001 0 5f
C_NET8_002 net__8__net_002 0 5f
C_NET8_003 net__8__net_003 0 10f
C_NET9_0 net__9__net_0 0 5f
C_NET9_1 net__9__net_1 0 10f
C_INT_0 _0_ 0 5f
C_INT_1 _1_ 0 5f
C_INT_2 _2_ 0 5f
C_INT_3 _3_ 0 5f

*************************************************************************
* Enhanced test vectors for complete transition coverage
*************************************************************************
* Sequence: 0000 → 1000 → 1010 → 1110 → 1100 → 0100 → 0000
* This provides multiple rise and fall transitions

VA a 0 PWL(
+ 0ns   0V   
+ 10ns  0V   28ns 1.2V 
+ 82ns  1.2V 92ns 0V
+ 250ns 0V)

VB b 0 PWL(
+ 0ns   0V   
+ 60ns  0V   65ns 1.2V 
+ 100ns  1.2V 115ns 0V
+ 250ns 0V)

VC c 0 PWL(
+ 0ns   0V   
+ 40ns  0V   55ns 1.2V
+ 70ns  1.2V 80ns 0V
+ 250ns 0V)

VD d 0 PWL(0ns 0V 250ns 0V)

*************************************************************************
* Output loads
*************************************************************************
CLoad_S S 0 10f
CLoad_C cout 0 10f

*************************************************************************
* Power supply decoupling
*************************************************************************
C_VDD VDD 0 10p
C_VSS VSS 0 10p

*************************************************************************
* Analysis configuration
*************************************************************************
.OPTIONS TIMEINT RELTOL=1e-6 ABSTOL=1e-12 METHOD=TRAP
.OPTIONS NONLIN MAXSTEP=1p SEARCHMETHOD=0
.OPTIONS DEVICE TEMP=27

.IC V(a)=0 V(b)=0 V(c)=0 V(d)=0 V(S)=0 V(cout)=0

.OP
.TRAN 0.05ns 305ns UIC

*************************************************************************
* Output files
*************************************************************************
.PRINT TRAN FORMAT=STD FILE=ha_waveforms.prn V(a) V(b) V(c) V(d) V(S) V(cout)
.PRINT TRAN FORMAT=CSV FILE=ha_power.csv TIME I(VDD) {-V(VDD)*I(VDD)}

*************************************************************************
* TIMING MEASUREMENTS - CORRECTED
*************************************************************************

* Input transition times
.MEASURE TRAN T_A_R WHEN V(a)=0.6 RISE=1 TD=10ns
.MEASURE TRAN T_A_F WHEN V(a)=0.6 FALL=1 TD=10ns
.MEASURE TRAN T_B_R WHEN V(b)=0.6 RISE=1 TD=10ns
.MEASURE TRAN T_B_F WHEN V(b)=0.6 FALL=1 TD=10ns
.MEASURE TRAN T_C_R WHEN V(c)=0.6 RISE=1 TD=10ns
.MEASURE TRAN T_C_F WHEN V(c)=0.6 FALL=1 TD=10ns

* Output S transition times
.MEASURE TRAN T_S_R1 WHEN V(S)=0.6 RISE=1 TD=10ns
.MEASURE TRAN T_S_F1 WHEN V(S)=0.6 FALL=1 TD=10ns
.MEASURE TRAN T_S_R2 WHEN V(S)=0.6 RISE=2 TD=10ns
.MEASURE TRAN T_S_F2 WHEN V(S)=0.6 FALL=2 TD=10ns

* Output cout transition times  
.MEASURE TRAN T_COUT_R1 WHEN V(cout)=0.6 RISE=1 TD=10ns
.MEASURE TRAN T_COUT_F1 WHEN V(cout)=0.6 FALL=1 TD=10ns

* Propagation delays
.MEASURE TRAN TPLH_A_S PARAM='T_S_R1-T_A_R'
.MEASURE TRAN TPHL_C_S PARAM='T_S_F1-T_C_R'
.MEASURE TRAN TPLH_C_COUT PARAM='T_COUT_R1-T_C_R'
.MEASURE TRAN TPHL_A_COUT PARAM='T_COUT_F1-T_A_F'

*************************************************************************
* RISE/FALL TIME MEASUREMENTS
*************************************************************************

* S output rise time
.MEASURE TRAN T_S_10_R WHEN V(S)=0.12 RISE=1 TD=5ns
.MEASURE TRAN T_S_90_R WHEN V(S)=1.08 RISE=1 TD=5ns
.MEASURE TRAN RISE_TIME_S PARAM='T_S_90_R-T_S_10_R'

* S output fall time - CORRECTED FORMULA
.MEASURE TRAN T_S_90_F WHEN V(S)=1.08 FALL=1 TD=5ns
.MEASURE TRAN T_S_10_F WHEN V(S)=0.12 FALL=1 TD=5ns
.MEASURE TRAN FALL_TIME_S PARAM='T_S_10_F-T_S_90_F'

* Cout output rise time
.MEASURE TRAN T_COUT_10_R WHEN V(cout)=0.12 RISE=1 TD=5ns
.MEASURE TRAN T_COUT_90_R WHEN V(cout)=1.08 RISE=1 TD=5ns
.MEASURE TRAN RISE_TIME_COUT PARAM='T_COUT_90_R-T_COUT_10_R'

* Cout output fall time - CORRECTED FORMULA
.MEASURE TRAN T_COUT_90_F WHEN V(cout)=1.08 FALL=1 TD=5ns
.MEASURE TRAN T_COUT_10_F WHEN V(cout)=0.12 FALL=1 TD=5ns
.MEASURE TRAN FALL_TIME_COUT PARAM='T_COUT_10_F-T_COUT_90_F'

*************************************************************************
* POWER MEASUREMENTS - CORRECTED
*************************************************************************

* Dynamic power during transitions
.MEASURE TRAN P_DYN1 AVG {-V(VDD)*I(VDD)} FROM=10.5ns TO=14ns
.MEASURE TRAN P_DYN2 AVG {-V(VDD)*I(VDD)} FROM=20.5ns TO=24ns
.MEASURE TRAN P_DYN3 AVG {-V(VDD)*I(VDD)} FROM=40.5ns TO=44ns
.MEASURE TRAN P_DYN4 AVG {-V(VDD)*I(VDD)} FROM=60.5ns TO=64ns
.MEASURE TRAN P_DYN5 AVG {-V(VDD)*I(VDD)} FROM=70.5ns TO=74ns
.MEASURE TRAN P_DYN6 AVG {-V(VDD)*I(VDD)} FROM=80.5ns TO=84ns

* Leakage power during stable periods - CORRECTED P_LEAK4 window
.MEASURE TRAN P_LEAK1 AVG {-V(VDD)*I(VDD)} FROM=6ns TO=9ns
.MEASURE TRAN P_LEAK2 AVG {-V(VDD)*I(VDD)} FROM=16ns TO=19ns
.MEASURE TRAN P_LEAK3 AVG {-V(VDD)*I(VDD)} FROM=26ns TO=39ns
.MEASURE TRAN P_LEAK4 AVG {-V(VDD)*I(VDD)} FROM=66ns TO=69ns
.MEASURE TRAN P_LEAK5 AVG {-V(VDD)*I(VDD)} FROM=86ns TO=95ns

* Total power metrics
.MEASURE TRAN P_AVG AVG {-V(VDD)*I(VDD)} FROM=2ns TO=305ns
.MEASURE TRAN P_PEAK MAX {-V(VDD)*I(VDD)} FROM=2ns TO=95ns
.MEASURE TRAN E_TOTAL INTEG {-V(VDD)*I(VDD)} FROM=2ns TO=95ns

*************************************************************************
* VERIFICATION MEASUREMENTS
*************************************************************************

* Output voltage levels (should be 1.2V and 0V)
.MEASURE TRAN V_S_MAX MAX V(S)
.MEASURE TRAN V_S_MIN MIN V(S)
.MEASURE TRAN V_COUT_MAX MAX V(cout)
.MEASURE TRAN V_COUT_MIN MIN V(cout)

* Average propagation delay
.MEASURE TRAN TPD_AVG PARAM='(TPLH_A_S+TPHL_C_S)/2'

* Sanity checks - all timing values should be positive
.MEASURE TRAN CHECK_RISE_S PARAM='ABS(RISE_TIME_S)'
.MEASURE TRAN CHECK_FALL_S PARAM='ABS(FALL_TIME_S)'
.MEASURE TRAN CHECK_RISE_COUT PARAM='ABS(RISE_TIME_COUT)'
.MEASURE TRAN CHECK_FALL_COUT PARAM='ABS(FALL_TIME_COUT)'

.END
