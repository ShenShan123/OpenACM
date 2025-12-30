* Xyce netlist for sabetz - Approximate 4-2 Compressor
* Version 1.3: FIXED - Redesigned test vectors for proper transitions
* Date: 2025-10-22
* Design: sabetz (14 transistors, S always = 1)
* Logic: cout = a·d + a·c + d·c (majority function of a,c,d)


* Simplified MOS Models for Testing
.MODEL NMOS_VTL NMOS (LEVEL=1 VTO=0.5 KP=200E-6)
.MODEL PMOS_VTL PMOS (LEVEL=1 VTO=-0.5 KP=150E-6)

*************************************************************************
* Power supplies
*************************************************************************
VDD VDD 0 DC 1.2
VSS VSS 0 DC 0

*************************************************************************
* Main circuit: sabetz
*************************************************************************

* Constant assignment: S = 1 (always high)
VS S 0 DC 1.2

* Instance _2_ (NAND2_X1): computes a NAND d -> _0_
M__2__M_i_1 net__2__net_0 d VSS VSS NMOS_VTL W=0.415u L=0.050u
M__2__M_i_0 _0_ a net__2__net_0 VSS NMOS_VTL W=0.415u L=0.050u
M__2__M_i_3 _0_ d VDD VDD PMOS_VTL W=0.630u L=0.050u
M__2__M_i_2 VDD a _0_ VDD PMOS_VTL W=0.630u L=0.050u

* Instance _3_ (OAI21_X1): computes (a+d)*!c -> _1_
* Logic: _1_ = !((a OR d) AND c) = (a+d)*!c
M__3__M_i_1 _1_ a net__3__net_0 VSS NMOS_VTL W=0.415u L=0.050u
M__3__M_i_0 net__3__net_0 d _1_ VSS NMOS_VTL W=0.415u L=0.050u
M__3__M_i_2 VSS c net__3__net_0 VSS NMOS_VTL W=0.415u L=0.050u
M__3__M_i_4 net__3__net_1 a VDD VDD PMOS_VTL W=0.630u L=0.050u
M__3__M_i_3 _1_ d net__3__net_1 VDD PMOS_VTL W=0.630u L=0.050u
M__3__M_i_5 VDD c _1_ VDD PMOS_VTL W=0.630u L=0.050u

* Instance _4_ (NAND2_X1): computes cout = _0_ NAND _1_
M__4__M_i_1 net__4__net_0 _1_ VSS VSS NMOS_VTL W=0.415u L=0.050u
M__4__M_i_0 cout _0_ net__4__net_0 VSS NMOS_VTL W=0.415u L=0.050u
M__4__M_i_3 cout _1_ VDD VDD PMOS_VTL W=0.630u L=0.050u
M__4__M_i_2 VDD _0_ cout VDD PMOS_VTL W=0.630u L=0.050u

*************************************************************************
* Parasitic capacitances
*************************************************************************
C_NET2_0 net__2__net_0 0 5f
C_NET3_0 net__3__net_0 0 5f
C_NET3_1 net__3__net_1 0 10f
C_NET4_0 net__4__net_0 0 5f
C_INT_0 _0_ 0 5f
C_INT_1 _1_ 0 5f

*************************************************************************
* Input test vectors
* 
* CRITICAL: RISE/FALL counts what Xyce ACTUALLY finds AFTER the TD time
*
* From Xyce diagnostics, we know:
* - After TD=128ns: d has only 1 more RISE (at 135ns)
* - After TD=188ns: d has only 1 more FALL (at 195ns)  
* - After TD=208ns: a has only 1 more RISE (at 215ns)
* - After TD=228ns: c has only 1 more FALL (at 235ns)
*
* Therefore we must use RISE=1 and FALL=1 for all patterns!
*************************************************************************

VA a 0 PWL(
+ 0ns 0V
+ 70ns 0V 83ns 1.2V
+ 170ns 1.2V 175ns 0V
+ 210ns 0V 223ns 1.2V
+ 260ns 1.2V)

VC c 0 PWL(
+ 0ns 0V
+ 50ns 0V 63ns 1.2V
+ 110ns 1.2V 115ns 0V
+ 150ns 0V 163ns 1.2V
+ 230ns 1.2V 235ns 0V
+ 260ns 0V)

VD d 0 PWL(
+ 0ns 0V
+ 30ns 0V 40ns 1.2V
+ 90ns 1.2V 95ns 0V
+ 130ns 0V 140ns 1.2V
+ 190ns 1.2V 195ns 0V
+ 260ns 0V)

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
* Analysis configuration
*************************************************************************
.OPTIONS TIMEINT RELTOL=1e-3 ABSTOL=1e-6 METHOD=TRAP
.OPTIONS NONLIN MAXSTEP=100 SEARCHMETHOD=0 
.OPTIONS NONLIN-TRAN MAXSTEP=100 SEARCHMETHOD=0
.OPTIONS DEVICE TEMP=27 GMIN=1e-15

.OP
.TRAN 0.1ns 520ns 0ns 0.05ns

*************************************************************************
* Output files
*************************************************************************
.PRINT TRAN FORMAT=STD FILE=sabetz_waveforms.prn 
+ V(a) V(c) V(d) V(S) V(cout) V(_0_) V(_1_)

.PRINT TRAN FORMAT=CSV FILE=sabetz_power.csv
+ TIME I(VDD) {V(VDD)*I(VDD)} {-V(VDD)*I(VDD)}

*************************************************************************
* Propagation delay measurements
*************************************************************************

* Pattern 1: C rises (50→55ns), expect cout RISE
.MEASURE TRAN T_C_R1 WHEN V(c)=0.6 RISE=1 TD=48ns
.MEASURE TRAN T_cout_R1 WHEN V(cout)=0.6 RISE=1 TD=48ns
.MEASURE TRAN TPLH_C_cout_P1 PARAM='T_cout_R1-T_C_R1'

* Pattern 2: C falls (110→115ns), expect cout FALL
.MEASURE TRAN T_C_F1 WHEN V(c)=0.6 FALL=1 TD=108ns
.MEASURE TRAN T_cout_F1 WHEN V(cout)=0.6 FALL=1 TD=108ns
.MEASURE TRAN TPHL_C_cout_P2 PARAM='T_cout_F1-T_C_F1'

* Pattern 3: D rises (130→135ns), expect cout RISE
.MEASURE TRAN T_D_R_P3 WHEN V(d)=0.6 RISE=1 TD=128ns
.MEASURE TRAN T_cout_R_P3 WHEN V(cout)=0.6 RISE=1 TD=128ns
.MEASURE TRAN TPLH_D_cout_P3 PARAM='T_cout_R_P3-T_D_R_P3'

* Pattern 4: D falls (190→195ns), expect cout FALL
.MEASURE TRAN T_D_F_P4 WHEN V(d)=0.6 FALL=1 TD=188ns
.MEASURE TRAN T_cout_F_P4 WHEN V(cout)=0.6 FALL=1 TD=188ns
.MEASURE TRAN TPHL_D_cout_P4 PARAM='T_cout_F_P4-T_D_F_P4'

* Pattern 5: A rises (210→215ns), expect cout RISE
.MEASURE TRAN T_A_R_P5 WHEN V(a)=0.6 RISE=1 TD=208ns
.MEASURE TRAN T_cout_R_P5 WHEN V(cout)=0.6 RISE=1 TD=208ns
.MEASURE TRAN TPLH_A_cout_P5 PARAM='T_cout_R_P5-T_A_R_P5'

* Pattern 6: C falls (230→235ns), expect cout FALL
.MEASURE TRAN T_C_F_P6 WHEN V(c)=0.6 FALL=1 TD=228ns
.MEASURE TRAN T_cout_F_P6 WHEN V(cout)=0.6 FALL=1 TD=228ns
.MEASURE TRAN TPHL_C_cout_P6 PARAM='T_cout_F_P6-T_C_F_P6'

*************************************************************************
* Rise/Fall time measurements
*************************************************************************

* Cout rise time (10% to 90%)
.MEASURE TRAN T_cout_10R WHEN V(cout)=0.12 RISE=1 TD=48ns
.MEASURE TRAN T_cout_90R WHEN V(cout)=1.08 RISE=1 TD=48ns
.MEASURE TRAN RISE_TIME_cout PARAM='T_cout_90R-T_cout_10R'

* Cout fall time (90% to 10%)
.MEASURE TRAN T_cout_90F WHEN V(cout)=1.08 FALL=1 TD=108ns
.MEASURE TRAN T_cout_10F WHEN V(cout)=0.12 FALL=1 TD=108ns
.MEASURE TRAN FALL_TIME_cout PARAM='T_cout_10F-T_cout_90F'

* S is constant
.MEASURE TRAN RISE_TIME_S PARAM='0'
.MEASURE TRAN FALL_TIME_S PARAM='0'

*************************************************************************
* Power measurements
*************************************************************************

* Average power over entire simulation (after settling)
.MEASURE TRAN P_AVG AVG {-V(VDD)*I(VDD)} FROM=115ns TO=520ns
.MEASURE TRAN P_PEAK MAX {-V(VDD)*I(VDD)} FROM=20ns TO=260ns
.MEASURE TRAN E_TOTAL INTEG {-V(VDD)*I(VDD)} FROM=20ns TO=260ns

* Dynamic power during switching patterns
.MEASURE TRAN P_DYN1 AVG {-V(VDD)*I(VDD)} FROM=48ns TO=63ns
.MEASURE TRAN P_DYN2 AVG {-V(VDD)*I(VDD)} FROM=108ns TO=123ns
.MEASURE TRAN P_DYN3 AVG {-V(VDD)*I(VDD)} FROM=128ns TO=143ns
.MEASURE TRAN P_DYN4 AVG {-V(VDD)*I(VDD)} FROM=188ns TO=203ns
.MEASURE TRAN P_DYN5 AVG {-V(VDD)*I(VDD)} FROM=208ns TO=223ns
.MEASURE TRAN P_DYN6 AVG {-V(VDD)*I(VDD)} FROM=228ns TO=243ns

* Static/leakage power during stable periods
.MEASURE TRAN P_STATIC1 AVG {-V(VDD)*I(VDD)} FROM=35ns TO=48ns
.MEASURE TRAN P_STATIC2 AVG {-V(VDD)*I(VDD)} FROM=97ns TO=108ns
.MEASURE TRAN P_STATIC3 AVG {-V(VDD)*I(VDD)} FROM=245ns TO=258ns

*************************************************************************
* Functional verification - Check cout at stable points
*************************************************************************
.MEASURE TRAN V_S_CHECK FIND V(S) AT=130ns

* Check cout values after each transition
.MEASURE TRAN V_cout_40NS FIND V(cout) AT=40ns   
.MEASURE TRAN V_cout_60NS FIND V(cout) AT=60ns   
.MEASURE TRAN V_cout_80NS FIND V(cout) AT=80ns   
.MEASURE TRAN V_cout_100NS FIND V(cout) AT=100ns 
.MEASURE TRAN V_cout_120NS FIND V(cout) AT=120ns 
.MEASURE TRAN V_cout_140NS FIND V(cout) AT=140ns 
.MEASURE TRAN V_cout_160NS FIND V(cout) AT=160ns 
.MEASURE TRAN V_cout_180NS FIND V(cout) AT=180ns 
.MEASURE TRAN V_cout_200NS FIND V(cout) AT=200ns 
.MEASURE TRAN V_cout_220NS FIND V(cout) AT=220ns 
.MEASURE TRAN V_cout_240NS FIND V(cout) AT=240ns 

*************************************************************************
* Performance statistics
*************************************************************************

* Average propagation delays
.MEASURE TRAN AVG_TPLH PARAM='(TPLH_C_cout_P1+TPLH_D_cout_P3+TPLH_A_cout_P5)/3'
.MEASURE TRAN AVG_TPHL PARAM='(TPHL_C_cout_P2+TPHL_D_cout_P4+TPHL_C_cout_P6)/3'
.MEASURE TRAN AVG_TP PARAM='(AVG_TPLH+AVG_TPHL)/2'

* Power-Delay Product
.MEASURE TRAN PDP PARAM='P_AVG*AVG_TP'
.MEASURE TRAN EDP PARAM='E_TOTAL*AVG_TP'

* Average dynamic power (excluding static)
.MEASURE TRAN P_DYN_AVG PARAM='(P_DYN1+P_DYN2+P_DYN3+P_DYN4+P_DYN5+P_DYN6)/6'
.MEASURE TRAN P_STATIC_AVG PARAM='(P_STATIC1+P_STATIC2+P_STATIC3)/3'

.END

