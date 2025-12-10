* Xyce-compatible netlist for AP1
* Generated from Verilog netlist
* Design: AP1 - Approximate 4-2 Compressor
* Date: 2025-11-12 20:25:20
* All standard cells are flattened to transistor level
* Modified for complete PPA analysis

.INCLUDE ../stdcells.spice

* Simplified MOS Models for Testing
.MODEL NMOS_VTL NMOS (LEVEL=1 VTO=0.5 KP=200E-6)
.MODEL PMOS_VTL PMOS (LEVEL=1 VTO=-0.5 KP=150E-6)

*************************************************************************
* Power supplies
*************************************************************************
VDD VDD 0 DC 1.2
VSS VSS 0 DC 0

*************************************************************************
* Main circuit: AP1 (58 transistors)
*************************************************************************

* Flattened instance: _06_ (OAI22_X1)
M__06__M_i_3 VSS d net__06__net_0 VSS NMOS_VTL W=0.415u L=0.050u
M__06__M_i_2 net__06__net_0 cin VSS VSS NMOS_VTL W=0.415u L=0.050u
M__06__M_i_0 _03_ a net__06__net_0 VSS NMOS_VTL W=0.415u L=0.050u
M__06__M_i_1 net__06__net_0 b _03_ VSS NMOS_VTL W=0.415u L=0.050u
M__06__M_i_7 net__06__net_2 d VDD VDD PMOS_VTL W=0.630u L=0.050u
M__06__M_i_6 _03_ cin net__06__net_2 VDD PMOS_VTL W=0.630u L=0.050u
M__06__M_i_4 net__06__net_1 a _03_ VDD PMOS_VTL W=0.630u L=0.050u
M__06__M_i_5 VDD b net__06__net_1 VDD PMOS_VTL W=0.630u L=0.050u
* End of _06_ (8 MOS transistors)

* Flattened instance: _07_ (NAND2_X1)
M__07__M_i_1 net__07__net_0 d VSS VSS NMOS_VTL W=0.415u L=0.050u
M__07__M_i_0 _04_ cin net__07__net_0 VSS NMOS_VTL W=0.415u L=0.050u
M__07__M_i_3 _04_ d VDD VDD PMOS_VTL W=0.630u L=0.050u
M__07__M_i_2 VDD cin _04_ VDD PMOS_VTL W=0.630u L=0.050u
* End of _07_ (4 MOS transistors)

* Flattened instance: _08_ (NAND2_X1)
M__08__M_i_1 net__08__net_0 b VSS VSS NMOS_VTL W=0.415u L=0.050u
M__08__M_i_0 _05_ a net__08__net_0 VSS NMOS_VTL W=0.415u L=0.050u
M__08__M_i_3 _05_ b VDD VDD PMOS_VTL W=0.630u L=0.050u
M__08__M_i_2 VDD a _05_ VDD PMOS_VTL W=0.630u L=0.050u
* End of _08_ (4 MOS transistors)

* Flattened instance: _09_ (NAND3_X1)
M__09__M_i_2 net__09__net_1 _05_ VSS VSS NMOS_VTL W=0.415u L=0.050u
M__09__M_i_1 net__09__net_0 _04_ net__09__net_1 VSS NMOS_VTL W=0.415u L=0.050u
M__09__M_i_0 C _03_ net__09__net_0 VSS NMOS_VTL W=0.415u L=0.050u
M__09__M_i_5 C _05_ VDD VDD PMOS_VTL W=0.630u L=0.050u
M__09__M_i_4 VDD _04_ C VDD PMOS_VTL W=0.630u L=0.050u
M__09__M_i_3 C _03_ VDD VDD PMOS_VTL W=0.630u L=0.050u
* End of _09_ (6 MOS transistors)

* Flattened instance: _10_ (XOR2_X1)
M__10__M_i_0 net__10__net_000 a VSS VSS NMOS_VTL W=0.210u L=0.050u
M__10__M_i_7 VSS b net__10__net_000 VSS NMOS_VTL W=0.210u L=0.050u
M__10__M_i_13 _00_ net__10__net_000 VSS VSS NMOS_VTL W=0.415u L=0.050u
M__10__M_i_19 net__10__net_001 a _00_ VSS NMOS_VTL W=0.415u L=0.050u
M__10__M_i_24 VSS b net__10__net_001 VSS NMOS_VTL W=0.415u L=0.050u
M__10__M_i_30 net__10__net_002 a net__10__net_000 VDD PMOS_VTL W=0.315u L=0.050u
M__10__M_i_35 VDD b net__10__net_002 VDD PMOS_VTL W=0.315u L=0.050u
M__10__M_i_41 net__10__net_003 net__10__net_000 VDD VDD PMOS_VTL W=0.630u L=0.050u
M__10__M_i_47 _00_ a net__10__net_003 VDD PMOS_VTL W=0.630u L=0.050u
M__10__M_i_53 net__10__net_003 b _00_ VDD PMOS_VTL W=0.630u L=0.050u
* End of _10_ (10 MOS transistors)

* Flattened instance: _11_ (XOR2_X1)
M__11__M_i_0 net__11__net_000 cin VSS VSS NMOS_VTL W=0.210u L=0.050u
M__11__M_i_7 VSS d net__11__net_000 VSS NMOS_VTL W=0.210u L=0.050u
M__11__M_i_13 _01_ net__11__net_000 VSS VSS NMOS_VTL W=0.415u L=0.050u
M__11__M_i_19 net__11__net_001 cin _01_ VSS NMOS_VTL W=0.415u L=0.050u
M__11__M_i_24 VSS d net__11__net_001 VSS NMOS_VTL W=0.415u L=0.050u
M__11__M_i_30 net__11__net_002 cin net__11__net_000 VDD PMOS_VTL W=0.315u L=0.050u
M__11__M_i_35 VDD d net__11__net_002 VDD PMOS_VTL W=0.315u L=0.050u
M__11__M_i_41 net__11__net_003 net__11__net_000 VDD VDD PMOS_VTL W=0.630u L=0.050u
M__11__M_i_47 _01_ cin net__11__net_003 VDD PMOS_VTL W=0.630u L=0.050u
M__11__M_i_53 net__11__net_003 d _01_ VDD PMOS_VTL W=0.630u L=0.050u
* End of _11_ (10 MOS transistors)

* Flattened instance: _12_ (XNOR2_X1)
M__12__M_i_0 net__12__net_001 _00_ net__12__net_000 VSS NMOS_VTL W=0.210u L=0.050u
M__12__M_i_5 VSS _01_ net__12__net_001 VSS NMOS_VTL W=0.210u L=0.050u
M__12__M_i_11 net__12__net_002 net__12__net_000 VSS VSS NMOS_VTL W=0.415u L=0.050u
M__12__M_i_17 _02_ _00_ net__12__net_002 VSS NMOS_VTL W=0.415u L=0.050u
M__12__M_i_23 net__12__net_002 _01_ _02_ VSS NMOS_VTL W=0.415u L=0.050u
M__12__M_i_29 net__12__net_000 _00_ VDD VDD PMOS_VTL W=0.315u L=0.050u
M__12__M_i_36 VDD _01_ net__12__net_000 VDD PMOS_VTL W=0.315u L=0.050u
M__12__M_i_42 _02_ net__12__net_000 VDD VDD PMOS_VTL W=0.630u L=0.050u
M__12__M_i_48 net__12__net_003 _00_ _02_ VDD PMOS_VTL W=0.630u L=0.050u
M__12__M_i_53 VDD _01_ net__12__net_003 VDD PMOS_VTL W=0.630u L=0.050u
* End of _12_ (10 MOS transistors)

* Flattened instance: _13_ (OAI21_X1)
M__13__M_i_1 S _04_ net__13__net_0 VSS NMOS_VTL W=0.415u L=0.050u
M__13__M_i_0 net__13__net_0 _05_ S VSS NMOS_VTL W=0.415u L=0.050u
M__13__M_i_2 VSS _02_ net__13__net_0 VSS NMOS_VTL W=0.415u L=0.050u
M__13__M_i_4 net__13__net_1 _04_ VDD VDD PMOS_VTL W=0.630u L=0.050u
M__13__M_i_3 S _05_ net__13__net_1 VDD PMOS_VTL W=0.630u L=0.050u
M__13__M_i_5 VDD _02_ S VDD PMOS_VTL W=0.630u L=0.050u
* End of _13_ (6 MOS transistors)

* Total MOS transistors: 58
* Total standard cell instances: 8

*************************************************************************
* Parasitic capacitances for internal nodes
*************************************************************************
C_NET06_0 net__06__net_0 0 5f
C_NET06_1 net__06__net_1 0 5f
C_NET06_2 net__06__net_2 0 10f
C_NET07_0 net__07__net_0 0 5f
C_NET08_0 net__08__net_0 0 5f
C_NET09_0 net__09__net_0 0 5f
C_NET09_1 net__09__net_1 0 5f
C_NET10_000 net__10__net_000 0 5f
C_NET10_001 net__10__net_001 0 5f
C_NET10_002 net__10__net_002 0 5f
C_NET10_003 net__10__net_003 0 10f
C_NET11_000 net__11__net_000 0 5f
C_NET11_001 net__11__net_001 0 5f
C_NET11_002 net__11__net_002 0 5f
C_NET11_003 net__11__net_003 0 10f
C_NET12_000 net__12__net_000 0 5f
C_NET12_001 net__12__net_001 0 5f
C_NET12_002 net__12__net_002 0 5f
C_NET12_003 net__12__net_003 0 10f
C_NET13_0 net__13__net_0 0 5f
C_NET13_1 net__13__net_1 0 10f
C_INT_00 _00_ 0 5f
C_INT_01 _01_ 0 5f
C_INT_02 _02_ 0 5f
C_INT_03 _03_ 0 5f
C_INT_04 _04_ 0 5f
C_INT_05 _05_ 0 5f

* Initial conditions
.IC V(_00_)=0.6 V(_01_)=0.6 V(_02_)=0.6
.IC V(_03_)=0.6 V(_04_)=0.6 V(_05_)=0.6
.IC V(S)=0.0 V(C)=0.0

*************************************************************************
* Test Vectors - Comprehensive Coverage
*************************************************************************
* Pattern sequence covering all transitions:
* T=0-10ns:   d=0→1  (0001, sum=1) → S=1, C=0
* T=10-30ns:  cin=0→1 (0011, sum=2) → S=0, C=1
* T=30-50ns:  b=0→1  (0111, sum=3) → S=1, C=1
* T=50-70ns:  cin=1→0 (0110, sum=2) → S=0, C=1
* T=70-100ns: a,d flip (1111, sum=4) → S=0, C=2
* T=100-130ns: all→0 (0000, sum=0) → S=0, C=0
* T=130-200ns: b,cin=1 (0110, sum=2) → S=0, C=1

VA a 0 PWL(
+ 0ns 0V 
+ 10ns 0V
+ 70ns 0V 80ns 1.2V
+ 100ns 1.2V 110ns 0V
+ 200ns 0V)

VB b 0 PWL(
+ 0ns 0V
+ 30ns 0V 40ns 1.2V
+ 100ns 1.2V 110ns 0V
+ 130ns 0V 140ns 1.2V
+ 200ns 1.2V)

VCIN cin 0 PWL(
+ 0ns 0V
+ 12ns 0V 22ns 1.2V
+ 50ns 1.2V 60ns 0V
+ 70ns 0V 80ns 1.2V
+ 100ns 1.2V 110ns 0V
+ 130ns 0V 140ns 1.2V
+ 200ns 1.2V)

VD d 0 PWL(
+ 0ns 0V 10ns 1.2V
+ 30ns 1.2V 
+ 70ns 1.2V 80ns 0V
+ 100ns 0V 110ns 1.2V
+ 130ns 1.2V 140ns 0V
+ 200ns 0V)

* Output load capacitances
CLoad_S S 0 10f
CLoad_C C 0 10f

* Power supply decoupling
C_VDD VDD 0 10p
C_VSS VSS 0 10p

*************************************************************************
* Analysis Setup
*************************************************************************

.OPTIONS TIMEINT RELTOL=1e-3 ABSTOL=1e-6 METHOD=TRAP
.OPTIONS NONLIN MAXSTEP=50 SEARCHMETHOD=0
.OPTIONS DEVICE TEMP=27

.OP
.TRAN 0.05ns 200ns 0 0.2ns

*************************************************************************
* Output Files
*************************************************************************

.PRINT TRAN FORMAT=STD FILE=AP1_waveforms.prn 
+ V(a) V(b) V(cin) V(d) V(S) V(C) 
+ V(_04_) V(_05_) V(_01_) V(_02_) V(_03_) V(_00_)

.PRINT TRAN FORMAT=CSV FILE=AP1_power.csv
+ TIME I(VDD) {V(VDD)*I(VDD)} {-V(VDD)*I(VDD)}

*************************************************************************
* PERFORMANCE Measurements
*************************************************************************

* ===== Pattern 1: d rises at 10ns, S should rise (0001) =====
.MEASURE TRAN T_D_R1 WHEN V(d)=0.6 RISE=1 TD=5ns
.MEASURE TRAN T_S_R1 WHEN V(S)=0.6 RISE=1 TD=5ns
.MEASURE TRAN TPLH_D_S_P1 PARAM='T_S_R1-T_D_R1'

* ===== Pattern 2: cin rises at 20ns, C rises & S falls (0011) =====
.MEASURE TRAN T_CIN_R1 WHEN V(cin)=0.6 RISE=1 TD=15ns
.MEASURE TRAN T_C_R1 WHEN V(C)=0.6 RISE=1 TD=15ns
.MEASURE TRAN T_S_F1 WHEN V(S)=0.6 FALL=1 TD=15ns
.MEASURE TRAN TPLH_CIN_C_P2 PARAM='T_C_R1-T_CIN_R1'
.MEASURE TRAN TPHL_CIN_S_P2 PARAM='T_S_F1-T_CIN_R1'

* ===== Pattern 3: b rises at 40ns, S rises (0111) =====
.MEASURE TRAN T_B_R1 WHEN V(b)=0.6 RISE=1 TD=35ns
.MEASURE TRAN T_S_R2 WHEN V(S)=0.6 RISE=1 TD=35ns
.MEASURE TRAN TPLH_B_S_P3 PARAM='T_S_R2-T_B_R1'

* ===== Pattern 4: cin falls at 60ns, S falls (0110) =====
.MEASURE TRAN T_CIN_F1 WHEN V(cin)=0.6 FALL=1 TD=55ns
.MEASURE TRAN T_S_F2 WHEN V(S)=0.6 FALL=1 TD=55ns
.MEASURE TRAN TPHL_CIN_S_P4 PARAM='T_S_F2-T_CIN_F1'

* ===== Pattern 5: a,cin rise; d falls at 80ns, S rises (1111) =====
.MEASURE TRAN T_A_R1 WHEN V(a)=0.6 RISE=1 TD=75ns
.MEASURE TRAN T_S_R3 WHEN V(S)=0.6 RISE=1 TD=75ns
.MEASURE TRAN TPLH_A_S_P5 PARAM='T_S_R3-T_A_R1'

* ===== Pattern 6: All inputs fall at 110ns, S & C fall (0000) =====
* NOTE: Multiple simultaneous transitions - only measure S delay
.MEASURE TRAN T_A_F1 WHEN V(a)=0.6 FALL=1 TD=105ns
.MEASURE TRAN T_S_F3 WHEN V(S)=0.6 FALL=1 TD=105ns
.MEASURE TRAN TPHL_A_S_P6 PARAM='T_S_F3-T_A_F1'

* ===== Average Propagation Delays =====
.MEASURE TRAN AVG_DELAY_S_RISE PARAM='(TPLH_D_S_P1+TPLH_B_S_P3+TPLH_A_S_P5)/3'
.MEASURE TRAN AVG_DELAY_S_FALL PARAM='(TPHL_CIN_S_P2+TPHL_CIN_S_P4+TPHL_A_S_P6)/3'
.MEASURE TRAN AVG_DELAY_S PARAM='(AVG_DELAY_S_RISE+AVG_DELAY_S_FALL)/2'

.MEASURE TRAN AVG_DELAY_C PARAM='TPLH_CIN_C_P2'

* ===== Rise/Fall Times =====
.MEASURE TRAN T_S_10 WHEN V(S)=0.12 RISE=1 TD=5ns
.MEASURE TRAN T_S_90 WHEN V(S)=1.08 RISE=1 TD=5ns
.MEASURE TRAN RISE_TIME_S PARAM='T_S_90-T_S_10'

.MEASURE TRAN T_S_90F WHEN V(S)=1.08 FALL=1 TD=15ns
.MEASURE TRAN T_S_10F WHEN V(S)=0.12 FALL=1 TD=15ns
.MEASURE TRAN FALL_TIME_S PARAM='T_S_10F-T_S_90F'

.MEASURE TRAN T_C_10 WHEN V(C)=0.12 RISE=1 TD=15ns
.MEASURE TRAN T_C_90 WHEN V(C)=1.08 RISE=1 TD=15ns
.MEASURE TRAN RISE_TIME_C PARAM='T_C_90-T_C_10'

.MEASURE TRAN T_C_90F WHEN V(C)=1.08 FALL=1 TD=105ns
.MEASURE TRAN T_C_10F WHEN V(C)=0.12 FALL=1 TD=105ns
.MEASURE TRAN FALL_TIME_C PARAM='T_C_10F-T_C_90F'

*************************************************************************
* POWER Measurements - Improved Accuracy
*************************************************************************

* Dynamic power during switching windows (narrower windows for accuracy)
.MEASURE TRAN I_DYN_P1 AVG {-I(VDD)} FROM=6.5ns TO=32.5ns
.MEASURE TRAN P_DYN_P1 AVG {-V(VDD)*I(VDD)} FROM=6.5ns TO=32.5ns
.MEASURE TRAN E_DYN_P1 INTEG {-V(VDD)*I(VDD)} FROM=6.5ns TO=32.5ns

.MEASURE TRAN I_DYN_P2 AVG {-I(VDD)} FROM=40ns TO=68ns
.MEASURE TRAN P_DYN_P2 AVG {-V(VDD)*I(VDD)} FROM=40ns TO=68ns
.MEASURE TRAN E_DYN_P2 INTEG {-V(VDD)*I(VDD)} FROM=40ns TO=68ns

.MEASURE TRAN I_DYN_P3 AVG {-I(VDD)} FROM=78ns TO=105ns
.MEASURE TRAN P_DYN_P3 AVG {-V(VDD)*I(VDD)} FROM=78ns TO=105ns
.MEASURE TRAN E_DYN_P3 INTEG {-V(VDD)*I(VDD)} FROM=78ns TO=105ns

.MEASURE TRAN I_DYN_P4 AVG {-I(VDD)} FROM=110.5ns TO=135.5ns
.MEASURE TRAN P_DYN_P4 AVG {-V(VDD)*I(VDD)} FROM=110.5ns TO=135.5ns
.MEASURE TRAN E_DYN_P4 INTEG {-V(VDD)*I(VDD)} FROM=110.5ns TO=135.5ns

.MEASURE TRAN P_DYNAMIC_AVG PARAM='(P_DYN_P1+P_DYN_P2+P_DYN_P3+P_DYN_P4)/4'

* Static/Leakage power during stable periods (avoid transient settling)
.MEASURE TRAN I_LEAK_1 AVG {-I(VDD)} FROM=18ns TO=25ns
.MEASURE TRAN P_LEAK_1 AVG {-V(VDD)*I(VDD)} FROM=18ns TO=25ns

.MEASURE TRAN I_LEAK_2 AVG {-I(VDD)} FROM=62ns TO=72ns
.MEASURE TRAN P_LEAK_2 AVG {-V(VDD)*I(VDD)} FROM=62ns TO=72ns

.MEASURE TRAN I_LEAK_3 AVG {-I(VDD)} FROM=175ns TO=195ns
.MEASURE TRAN P_LEAK_3 AVG {-V(VDD)*I(VDD)} FROM=175ns TO=195ns

.MEASURE TRAN P_STATIC_AVG PARAM='(P_LEAK_1+P_LEAK_2+P_LEAK_3)/3'

* Total power metrics
.MEASURE TRAN P_TOTAL_CALC PARAM='P_DYNAMIC_AVG+P_STATIC_AVG'
.MEASURE TRAN P_TOTAL_AVG AVG {-V(VDD)*I(VDD)} FROM=16ns TO=179ns
.MEASURE TRAN P_PEAK MAX {-V(VDD)*I(VDD)} FROM=16ns TO=179ns

* Energy metrics
.MEASURE TRAN E_TOTAL INTEG {-V(VDD)*I(VDD)} FROM=5ns TO=200ns
.MEASURE TRAN E_PER_OP PARAM='E_TOTAL/6'

* Power breakdown percentage
.MEASURE TRAN PWR_DYN_PERCENT PARAM='100*P_DYNAMIC_AVG/P_TOTAL_CALC'
.MEASURE TRAN PWR_STAT_PERCENT PARAM='100*P_STATIC_AVG/P_TOTAL_CALC'

.END