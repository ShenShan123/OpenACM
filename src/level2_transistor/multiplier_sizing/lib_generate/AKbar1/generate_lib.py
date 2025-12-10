#!/usr/bin/env python3
"""
akbar1 Liberty Generator
Approximate 4-2 Compressor (24 transistors)
Logic: S = (a XNOR b) NAND (c XNOR d), cout = d
Liberty output: S and C (C mapped from cout)
usage: python3 generate_lib.py
"""

import os
import re
import subprocess
import numpy as np
from pathlib import Path
from datetime import datetime
import sys

class LibGenerator:
    """Liberty Library Generator for akbar1"""
    
    def __init__(self, debug_mode=False):
        self.cell_name = "akbar1"
        self.vdd = 1
        self.temp = 25
        self.cell_area = 4.2105
        
        self.input_slews = [0.01, 0.05, 0.1, 0.2, 0.5]
        self.output_loads = [5, 10, 20, 50, 100]
        
        self.inputs = ['a', 'b', 'c', 'd']
        self.outputs = ['S', 'cout']  # Actual SPICE node names
        
        # Liberty file pin name mapping
        self.liberty_pin_map = {
            'S': 'S',
            'cout': 'C'  # cout in SPICE -> C in Liberty
        }
        
        self.test_vectors = self._generate_test_vectors()
        
        self.timing_data = {}
        self.input_cap_data = {}
        self.leakage_power = None
        
        self.sim_count = 0
        self.sim_success = 0
        
        self.debug_mode = debug_mode
        
        # Process parameters for capacitance calculation
        self.cox = 17.0       # fF/um^2
        self.cj = 2.0         # fF/um^2
        self.cjsw = 0.3       # fF/um
        self.cgd_overlap = 0.08  # um
        self.diff_length = 0.4   # um
        
        # Pin-specific interconnect capacitance
        self.interconnect_cap_map = {
            'a': 7.0,
            'b': 7.0,
            'c': 7.0,
            'd': 6.5,
        }
        
    def _generate_test_vectors(self):
        """Generate test vectors for timing arcs
        S = (a XNOR b) NAND (c XNOR d)
        cout = d
        """
        vectors = {}
        
        # For S output - test each input
        for inp in self.inputs:
            others = [p for p in self.inputs if p != inp]
            # Use vectors that will cause transitions on S
            if inp == 'a':
                vectors[(inp, 'S', 'rise')] = {'b': 0, 'c': 1, 'd': 1}
                vectors[(inp, 'S', 'fall')] = {'b': 0, 'c': 1, 'd': 1}
            elif inp == 'b':
                vectors[(inp, 'S', 'rise')] = {'a': 0, 'c': 1, 'd': 1}
                vectors[(inp, 'S', 'fall')] = {'a': 0, 'c': 1, 'd': 1}
            elif inp == 'c':
                vectors[(inp, 'S', 'rise')] = {'a': 1, 'b': 1, 'd': 0}
                vectors[(inp, 'S', 'fall')] = {'a': 1, 'b': 1, 'd': 0}
            elif inp == 'd':
                vectors[(inp, 'S', 'rise')] = {'a': 1, 'b': 1, 'c': 0}
                vectors[(inp, 'S', 'fall')] = {'a': 1, 'b': 1, 'c': 0}
        
        # For cout output - only d affects cout (cout = d)
        vectors[('d', 'cout', 'rise')] = {'a': 0, 'b': 0, 'c': 0}
        vectors[('d', 'cout', 'fall')] = {'a': 0, 'b': 0, 'c': 0}
        
        return vectors
    
    def calculate_diffusion_capacitance(self, width_um):
        """C_diff = C_j * Area + C_jsw * Perimeter"""
        area = width_um * self.diff_length
        perimeter = 2 * (width_um + self.diff_length)
        c_diff = self.cj * area + self.cjsw * perimeter
        return c_diff  # fF
    
    def calculate_miller_capacitance(self, width_um):
        """C_gd = Cox * W * L_overlap"""
        overlap_area = width_um * self.cgd_overlap
        c_miller = self.cox * overlap_area
        return c_miller  # fF
    
    def calculate_input_capacitance(self, pin_name):
        """Calculate input capacitance using transistor dimensions
        
        akbar1 structure:
        - Instance _2_ (XNOR2): a XNOR b -> _0_
        - Instance _3_ (XNOR2): c XNOR d -> _1_
        - Instance _4_ (NAND2): _0_ NAND _1_ -> S
        - Instance _5_ (BUF): d -> cout
        """
        
        # Transistor map: (width_um, length_um, type)
        transistor_map = {
            'a': [
                # From instance _2_ (XNOR2)
                (0.210, 0.050, 'n'),  # M__2__M_i_0
                (0.415, 0.050, 'n'),  # M__2__M_i_17
                (0.315, 0.050, 'p'),  # M__2__M_i_29
                (0.630, 0.050, 'p'),  # M__2__M_i_48
            ],
            'b': [
                # From instance _2_ (XNOR2)
                (0.210, 0.050, 'n'),  # M__2__M_i_5
                (0.415, 0.050, 'n'),  # M__2__M_i_23
                (0.315, 0.050, 'p'),  # M__2__M_i_36
                (0.630, 0.050, 'p'),  # M__2__M_i_53
            ],
            'c': [
                # From instance _3_ (XNOR2)
                (0.210, 0.050, 'n'),  # M__3__M_i_0
                (0.415, 0.050, 'n'),  # M__3__M_i_17
                (0.315, 0.050, 'p'),  # M__3__M_i_29
                (0.630, 0.050, 'p'),  # M__3__M_i_48
            ],
            'd': [
                # From instance _3_ (XNOR2)
                (0.210, 0.050, 'n'),  # M__3__M_i_5
                (0.415, 0.050, 'n'),  # M__3__M_i_23
                (0.315, 0.050, 'p'),  # M__3__M_i_36
                (0.630, 0.050, 'p'),  # M__3__M_i_53
                # From instance _5_ (BUF)
                (0.210, 0.050, 'n'),  # M__5__M_i_2
                (0.315, 0.050, 'p'),  # M__5__M_i_3
            ],
        }
        
        transistors = transistor_map.get(pin_name, [])
        if not transistors:
            return 0.01
        
        cgate_total = 0.0
        cdiff_total = 0.0
        cmiller_total = 0.0
        
        for w_um, l_um, ttype in transistors:
            cgate = self.cox * w_um * l_um
            cgate_total += cgate
            
            cdiff = self.calculate_diffusion_capacitance(w_um)
            cdiff_total += cdiff
            
            cmiller = self.calculate_miller_capacitance(w_um)
            cmiller_total += cmiller
        
        cinter = self.interconnect_cap_map.get(pin_name, 7.0)
        
        cin_total_fF = cgate_total + cdiff_total + cmiller_total + cinter
        cin_total_pF = cin_total_fF / 1000.0
        
        if self.debug_mode:
            print(f"\n[CAP CALC] Pin {pin_name}:")
            print(f"  Transistors: {len(transistors)}")
            print(f"  Cgate:   {cgate_total:.3f} fF ({cgate_total/cin_total_fF*100:.1f}%)")
            print(f"  Cdiff:   {cdiff_total:.3f} fF ({cdiff_total/cin_total_fF*100:.1f}%)")
            print(f"  Cmiller: {cmiller_total:.3f} fF ({cmiller_total/cin_total_fF*100:.1f}%)")
            print(f"  Cinter:  {cinter:.3f} fF ({cinter/cin_total_fF*100:.1f}%)")
            print(f"  Total:   {cin_total_pF:.6f} pF")
        
        return cin_total_pF
        
    def check_xyce(self):
        """Check for Xyce"""
        for cmd in ['Xyce', 'xyce', '/home/wangyk/.conda/envs/openyield/bin/Xyce']:
            try:
                result = subprocess.run([cmd, '--version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print(f" Xyce found: {cmd}")
                    self.xyce_cmd = cmd
                    return True
            except:
                continue
        
        try:
            result = subprocess.run(['which', 'Xyce'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                xyce_path = result.stdout.strip()
                self.xyce_cmd = xyce_path
                print(f" Xyce found at: {xyce_path}")
                return True
        except:
            pass
        
        print(" Xyce not found")
        self.xyce_cmd = None
        return False
    
    def generate_leakage_netlist(self, template_file):
        """Generate leakage measurement netlist"""
        
        with open(template_file, 'r') as f:
            netlist = f.read()
        
        base_dir = Path(template_file).parent.absolute()
        test_dir = base_dir / "sim_work" / "leakage_measurement"
        test_dir.mkdir(parents=True, exist_ok=True)
        
        voltage_sources = []
        for pin in self.inputs:
            voltage_sources.append(f'V{pin} {pin} 0 DC 0V')
        
        vsrc_section = '\n'.join(voltage_sources)
        
        sim_time = 300.0
        
        replacements = {
            '__VDD_VAL__': f'{self.vdd}V',
            '__TEMP_VAL__': str(self.temp),
            '__VDD_10__': f'{self.vdd * 0.1}',
            '__VDD_50__': f'{self.vdd * 0.5}',
            '__VDD_90__': f'{self.vdd * 0.9}',
            '__INPUT_PIN__': 'a',
            '__OUTPUT_PIN__': 'S',
            '__OUTPUT_LOAD__': '10f',
            '__TSTEP__': '0.05ns',
            '__TSTOP__': f'{sim_time}ns',
            '__TMAX__': '0.2ns',
            '__LEAK_START__': '0ns',
            '__MEAS_START__': '0ns',
            '__MEAS_END__': f'{sim_time}ns',
            '__INPUT_START__': '0ns',
            '__INPUT_END__': '1ns',
        }
        
        for placeholder, value in replacements.items():
            netlist = netlist.replace(placeholder, value)
        
        pattern_start = netlist.find('* Input under test')
        pattern_end = netlist.find('* Output loads')
        
        if pattern_start != -1 and pattern_end != -1:
            before = netlist[:pattern_start]
            after = netlist[pattern_end:]
            vsrc_header = '* All inputs at 0V for leakage measurement\n'
            netlist = before + vsrc_header + vsrc_section + '\n\n' + after
        
        netlist = re.sub(r'V__INPUT_PIN__.*', '* Removed placeholder', netlist)
        
        lines = netlist.split('\n')
        cleaned_lines = []
        for line in lines:
            if line.strip().lower().startswith(('.include', '.lib')):
                cleaned_lines.append(f'* REMOVED: {line}')
            else:
                cleaned_lines.append(line)
        netlist = '\n'.join(cleaned_lines)
        
        multi_window_measurements = f'''
* Multi-window Leakage Measurement
.MEASURE TRAN I_LEAK_1 AVG {{-I(VDD)}} FROM=28ns TO=35ns
.MEASURE TRAN P_LEAK_1 AVG {{-V(VDD)*I(VDD)}} FROM=28ns TO=35ns
.MEASURE TRAN I_LEAK_2 AVG {{-I(VDD)}} FROM=62ns TO=72ns
.MEASURE TRAN P_LEAK_2 AVG {{-V(VDD)*I(VDD)}} FROM=62ns TO=72ns
.MEASURE TRAN I_LEAK_3 AVG {{-I(VDD)}} FROM=175ns TO=195ns
.MEASURE TRAN P_LEAK_3 AVG {{-V(VDD)*I(VDD)}} FROM=175ns TO=195ns
.MEASURE TRAN P_STATIC_AVG PARAM='(P_LEAK_1+P_LEAK_2+P_LEAK_3)/3'
.MEASURE TRAN I_STATIC_AVG PARAM='(I_LEAK_1+I_LEAK_2+I_LEAK_3)/3'
'''
        
        netlist = netlist.replace('.END', multi_window_measurements + '\n.END')
        
        test_file = test_dir / "leakage.sp"
        with open(test_file, 'w') as f:
            f.write(netlist)
        
        return test_file, test_dir
    
    def measure_leakage_power(self, template_file):
        """Measure leakage power"""
        print("\n Measuring leakage power...")
        
        test_file, test_dir = self.generate_leakage_netlist(template_file)
        
        if not self.xyce_cmd:
            print("   Using default leakage value")
            return 0.0000028845  
        
        try:
            cmd = [self.xyce_cmd, test_file.name]
            result = subprocess.run(
                cmd,
                cwd=str(test_dir.absolute()),
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                print("   Simulation failed, using default")
                return 0.0000028845
            
            mt_file = test_dir / "leakage.sp.mt0"
            if not mt_file.exists():
                print("   No measurement file, using default")
                return 0.0000028845
            
            measurements = {}
            with open(mt_file, 'r') as f:
                for line in f:
                    match = re.match(r'^\s*(\w+)\s*=\s*([+-]?\d+\.?\d*[eE]?[+-]?\d*)', 
                                   line, re.IGNORECASE)
                    if match:
                        name = match.group(1).lower()
                        value = float(match.group(2))
                        measurements[name] = value
            
            p_leak = measurements.get('p_static_avg', 0)
            
            if p_leak and abs(p_leak) > 1e-15:
                leakage_power_uw = abs(p_leak) * 1e6
                print(f"   Leakage power = {leakage_power_uw:.6f} uW")
                return leakage_power_uw
            else:
                print("   Using default value")
                return 0.0000028845
            
        except Exception as e:
            print(f"   Error: {str(e)[:50]}, using default")
            return 0.0000028845
    
    def generate_netlist(self, template_file, input_pin, output_pin, 
                        transition, slew, load, test_id):
        """Generate timing netlist"""
        
        with open(template_file, 'r') as f:
            netlist = f.read()
        
        base_dir = Path(template_file).parent.absolute()
        test_dir = base_dir / "sim_work" / test_id
        test_dir.mkdir(parents=True, exist_ok=True)
        
        t_start = 10.0
        t_end = t_start + slew
        sim_time = 500.0
        
        if transition == 'rise':
            stim = f"PWL(0ns 0V {t_start}ns 0V {t_end}ns {self.vdd}V {sim_time}ns {self.vdd}V)"
        else:
            stim = f"PWL(0ns {self.vdd}V {t_start}ns {self.vdd}V {t_end}ns 0V {sim_time}ns 0V)"
        
        meas_start = t_start - 1.0
        meas_end = t_end + 10.0
        leak_start = sim_time * 0.8
        
        vdd_10 = self.vdd * 0.1
        vdd_50 = self.vdd * 0.5
        vdd_90 = self.vdd * 0.9
        
        vec_key = (input_pin, output_pin, transition)
        static_values = self.test_vectors.get(vec_key, {})
        
        vsrc_map = {'a': 'Va', 'b': 'Vb', 'c': 'Vc', 'd': 'Vd'}
        
        voltage_sources = []
        active_vsrc = vsrc_map[input_pin]
        voltage_sources.append(f'{active_vsrc} {input_pin} 0 {stim}')
        
        for pin in self.inputs:
            if pin != input_pin:
                vsrc_name = vsrc_map[pin]
                value = static_values.get(pin, 0)
                dc_val = f'{self.vdd}V' if value == 1 else '0V'
                voltage_sources.append(f'{vsrc_name} {pin} 0 DC {dc_val}')
        
        vsrc_section = '\n'.join(voltage_sources)
        
        replacements = {
            '__VDD_VAL__': f'{self.vdd}V',
            '__TEMP_VAL__': str(self.temp),
            '__VDD_10__': f'{vdd_10}',
            '__VDD_50__': f'{vdd_50}',
            '__VDD_90__': f'{vdd_90}',
            '__INPUT_PIN__': input_pin,
            '__OUTPUT_PIN__': output_pin,
            '__OUTPUT_LOAD__': f'{load}f',
            '__TSTEP__': '0.05ns',
            '__TSTOP__': f'{sim_time}ns',
            '__TMAX__': '0.2ns',
            '__MEAS_START__': f'{meas_start}ns',
            '__MEAS_END__': f'{meas_end}ns',
            '__INPUT_START__': f'{t_start-0.5}ns',
            '__INPUT_END__': f'{t_end+2.0}ns',
            '__LEAK_START__': f'{leak_start}ns',
        }
        
        for placeholder, value in replacements.items():
            netlist = netlist.replace(placeholder, value)
        
        pattern_start = netlist.find('* Input under test')
        pattern_end = netlist.find('* Output loads')
        
        if pattern_start != -1 and pattern_end != -1:
            before = netlist[:pattern_start]
            after = netlist[pattern_end:]
            vsrc_header = f'* Input under test: {input_pin} ({transition})\n'
            netlist = before + vsrc_header + vsrc_section + '\n\n' + after
        
        lines = netlist.split('\n')
        filtered_lines = []
        for line in lines:
            if 'V__INPUT_PIN__' in line and line.strip().startswith('V__INPUT_PIN__'):
                continue
            else:
                filtered_lines.append(line)
        netlist = '\n'.join(filtered_lines)
        
        netlist = re.sub(r'\.MEASURE.*Q_INPUT.*\n', '', netlist, flags=re.IGNORECASE)
        
        lines = netlist.split('\n')
        cleaned_lines = []
        for line in lines:
            if line.strip().lower().startswith(('.include', '.lib')):
                cleaned_lines.append(f'* REMOVED: {line}')
            else:
                cleaned_lines.append(line)
        netlist = '\n'.join(cleaned_lines)
        
        test_file = test_dir / "test.sp"
        with open(test_file, 'w') as f:
            f.write(netlist)
        
        return test_file, test_dir
    
    def run_simulation(self, test_file, test_dir):
        """Run Xyce simulation"""
        if not self.xyce_cmd:
            return False
        
        try:
            cmd = [self.xyce_cmd, test_file.name]
            result = subprocess.run(
                cmd,
                cwd=str(test_dir.absolute()),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return result.returncode == 0
            
        except:
            return False
    
    def parse_measurements(self, test_dir, input_pin, output_pin, transition):
        """Parse measurements (timing + power/energy) with E_TOTAL support
        
        Args:
            test_dir: Test directory containing .mt0 file
            input_pin: Input pin name
            output_pin: Output pin name
            transition: 'rise' or 'fall'
        """
        mt_file = test_dir / "test.sp.mt0"
        
        if not mt_file.exists():
            return None
        
        measurements = {}
        try:
            with open(mt_file, 'r') as f:
                for line in f:
                    match = re.match(r'^\s*(\w+)\s*=\s*([+-]?\d+\.?\d*[eE]?[+-]?\d*)', line)
                    if match:
                        name = match.group(1).lower()
                        value = float(match.group(2))
                        measurements[name] = value
        except:
            return None
        
        if not measurements:
            return None
        
        timing = {}
        power = {}
        
        out_lower = output_pin.lower()
        
        # === Timing ===
        for suffix in ['_rise', '_fall']:
            delay_key = f'delay_{out_lower}{suffix}'
            if delay_key in measurements:
                val = measurements[delay_key]
                if val > 0:
                    if suffix == '_rise':
                        timing['cell_rise'] = val * 1e9  # s → ns
                    else:
                        timing['cell_fall'] = val * 1e9  # s → ns
        
        for suffix in ['_rise', '_fall']:
            slew_key = f'slew_{out_lower}{suffix}'
            if slew_key in measurements:
                val = measurements[slew_key]
                if val > 0:
                    if suffix == '_rise':
                        timing['rise_transition'] = val * 1e9  # s → ns
                    else:
                        timing['fall_transition'] = val * 1e9  # s → ns
        
        # === Power / Energy ===
        if 'p_avg' in measurements and measurements['p_avg'] > 0:
            power['avg_power'] = measurements['p_avg'] * 1e6  # W → uW
        
        e_r = measurements.get('e_tog_r', None)
        e_f = measurements.get('e_tog_f', None)
        e_total = measurements.get('e_total', None)
        
        if self.debug_mode:
            print(f"\n[ENERGY PARSE] {input_pin}→{output_pin} {transition}")
            print(f"  e_tog_r: {e_r}")
            print(f"  e_tog_f: {e_f}")
            print(f"  e_total: {e_total}")

        if e_r is not None and e_r != 0.0:
            power['rise_energy'] = abs(e_r) * 1e12  # J → pJ
        if e_f is not None and e_f != 0.0:
            power['fall_energy'] = abs(e_f) * 1e12  # J → pJ
        
        if e_total is not None and e_total != 0.0:
            if transition == 'rise' and 'rise_energy' not in power:
                power['rise_energy'] = abs(e_total) * 1e12  # J → pJ
            elif transition == 'fall' and 'fall_energy' not in power:
                power['fall_energy'] = abs(e_total) * 1e12  # J → pJ
        
        if self.debug_mode:
            print(f"  Final power dict: {power}")
        
        return {
            'timing': timing,
            'power': power,
        }
    
    def analytical_delay(self, slew, load):
        """Analytical delay model - slightly faster than ACCI1"""
        return 0.04 + 0.18 * slew + 0.0018 * load
    
    def analytical_slew(self, input_slew, load):
        """Analytical slew model"""
        return max(input_slew * 0.75 + 0.0009 * load, 0.012)
    
    def characterize_arc(self, template_file, input_pin, output_pin, use_xyce):
        """Characterize timing arc"""
        
        print(f"  Arc: {input_pin} → {output_pin}")
        
        # Check if this arc exists
        vec_key_rise = (input_pin, output_pin, 'rise')
        vec_key_fall = (input_pin, output_pin, 'fall')
        
        if vec_key_rise not in self.test_vectors and vec_key_fall not in self.test_vectors:
            print(f"    Skipping non-existent arc")
            return None
        
        n_slews = len(self.input_slews)
        n_loads = len(self.output_loads)
        
        cell_rise = np.zeros((n_slews, n_loads))
        cell_fall = np.zeros((n_slews, n_loads))
        rise_trans = np.zeros((n_slews, n_loads))
        fall_trans = np.zeros((n_slews, n_loads))
        rise_power = np.zeros((n_slews, n_loads))
        fall_power = np.zeros((n_slews, n_loads))
        
        for i, slew in enumerate(self.input_slews):
            for j, load in enumerate(self.output_loads):
                
                # Rise transition
                if vec_key_rise in self.test_vectors:
                    test_id = f"{input_pin}_{output_pin}_rise_s{slew:.3f}_l{load}"
                    test_file, test_dir = self.generate_netlist(
                        template_file, input_pin, output_pin, 'rise', slew, load, test_id
                    )
                    
                    self.sim_count += 1
                    
                    if use_xyce and self.run_simulation(test_file, test_dir):
                        # Pass the transition parameter
                        result = self.parse_measurements(test_dir, input_pin, output_pin, 'rise')
                        
                        if result:
                            t = result['timing']
                            p = result['power']
                            
                            # timing
                            if t:
                                cell_rise[i,j] = t.get('cell_rise', self.analytical_delay(slew, load))
                                rise_trans[i,j] = t.get('rise_transition', self.analytical_slew(slew, load))
                            else:
                                cell_rise[i,j] = self.analytical_delay(slew, load)
                                rise_trans[i,j] = self.analytical_slew(slew, load)
                            
                            # power
                            rise_power[i,j] = p.get('rise_energy',
                                                     p.get('avg_power', 0.004))
                            
                            self.sim_success += 1
                        else:
                            cell_rise[i,j] = self.analytical_delay(slew, load)
                            rise_trans[i,j] = self.analytical_slew(slew, load)
                            rise_power[i,j] = 0.004
                    else:
                        cell_rise[i,j] = self.analytical_delay(slew, load)
                        rise_trans[i,j] = self.analytical_slew(slew, load)
                        rise_power[i,j] = 0.004
                
                # Fall transition
                if vec_key_fall in self.test_vectors:
                    test_id = f"{input_pin}_{output_pin}_fall_s{slew:.3f}_l{load}"
                    test_file, test_dir = self.generate_netlist(
                        template_file, input_pin, output_pin, 'fall', slew, load, test_id
                    )
                    
                    self.sim_count += 1
                    
                    if use_xyce and self.run_simulation(test_file, test_dir):
                        # Pass the transition parameter
                        result = self.parse_measurements(test_dir, input_pin, output_pin, 'fall')
                        
                        if result:
                            t = result['timing']
                            p = result['power']
                            
                            if t:
                                cell_fall[i,j] = t.get('cell_fall', self.analytical_delay(slew, load))
                                fall_trans[i,j] = t.get('fall_transition', self.analytical_slew(slew, load))
                            else:
                                cell_fall[i,j] = self.analytical_delay(slew, load)
                                fall_trans[i,j] = self.analytical_slew(slew, load)
                            
                            fall_power[i,j] = p.get('fall_energy',
                                                     p.get('avg_power', 0.4))
                            
                            self.sim_success += 1
                        else:
                            cell_fall[i,j] = self.analytical_delay(slew, load)
                            fall_trans[i,j] = self.analytical_slew(slew, load)
                            fall_power[i,j] = 0.4
                    else:
                        cell_fall[i,j] = self.analytical_delay(slew, load)
                        fall_trans[i,j] = self.analytical_slew(slew, load)
                        fall_power[i,j] = 0.4
                
                completed = (i * n_loads + j + 1)
                total = n_slews * n_loads
                print(f"\r    Progress: {completed}/{total} points", end='', flush=True)
        
        print()
        
        return {
            'cell_rise': cell_rise,
            'cell_fall': cell_fall,
            'rise_transition': rise_trans,
            'fall_transition': fall_trans,
            'rise_power': rise_power,
            'fall_power': fall_power,
        }
    
    def format_lut(self, table, indent=4):
        """Format lookup table for timing - matches power format"""
        lines = []
        ind = '    ' * indent
        ind_inner = '    ' * (indent + 1)
        
        # Add index lines
        idx1 = ', '.join([f'{s:.3f}' for s in self.input_slews])
        idx2 = ', '.join([f'{l/1000:.6f}' for l in self.output_loads])
        lines.append(f'{ind}index_1 ("{idx1}");')
        lines.append(f'{ind}index_2 ("{idx2}");')
        lines.append(f'{ind}values ( \\')
        
        # Add data rows
        for i, row in enumerate(table):
            values = ', '.join([f'{v:.6f}' for v in row])
            if i < len(table) - 1:
                lines.append(f'{ind_inner}"{values}", \\')
            else:
                lines.append(f'{ind_inner}"{values}" \\')
        
        lines.append(f'{ind});')
        return '\n'.join(lines)
    
    def format_power_lut(self, table, indent=4):
        """Format 2D power LUT"""
        lines = []
        ind = '    ' * indent
        
        # Add index lines
        idx1 = ', '.join([f'{s:.3f}' for s in self.input_slews])
        idx2 = ', '.join([f'{l/1000:.6f}' for l in self.output_loads])
        lines.append(f'{ind}index_1 ("{idx1}");')
        lines.append(f'{ind}index_2 ("{idx2}");')
        lines.append(f'{ind}values( \\')
        
        # Add data rows
        for i, row in enumerate(table):
            values = ', '.join([f'{v:.6f}' for v in row])
            if i < len(table) - 1:
                lines.append(f'{ind}    "{values}", \\')
            else:
                lines.append(f'{ind}    "{values}" \\')
        
        lines.append(f'{ind});')
        return '\n'.join(lines)

    def format_power_values(self, power_table):
        avg_power = np.mean(power_table, axis=1)
        return ', '.join([f'{v:.6f}' for v in avg_power])
    
    def generate_liberty(self, output_file, timing_tables):
        """Generate Liberty file in format matching example"""
        
        print(f"\n Generating Liberty file: {output_file}")
        
        leakage_uw = self.leakage_power if self.leakage_power else 0.035
        
        # Start building the Liberty file
        lib = []
        
        # Header with energy_unit added
        lib.append(f'''library({self.cell_name}_lib) {{
    delay_model : table_lookup;
    time_unit : "1ns";
    voltage_unit : "1V";
    current_unit : "1uA";
    resistance_unit : "1kohm";
    capacitive_load_unit(1, pF) ;
    leakage_power_unit : "1uW";
    pulling_resistance_unit : "1kohm";
    energy_unit : "1pJ";

    operating_conditions(typical) {{
        process : 1.0;
        temperature : {self.temp:.3f};
        voltage : {self.vdd};
        tree_type : balanced_tree;
    }}
    /* threshold definitions */
    slew_derate_from_library : 1.000;
    slew_lower_threshold_pct_fall : 10.000;
    slew_upper_threshold_pct_fall : 90.000;
    slew_lower_threshold_pct_rise : 10.000;
    slew_upper_threshold_pct_rise : 90.000;
    input_threshold_pct_fall : 50.000;
    input_threshold_pct_rise : 50.000;
    output_threshold_pct_fall : 50.000;
    output_threshold_pct_rise : 50.000;

    nom_process : 1.0;
    nom_temperature : {self.temp:.3f};
    nom_voltage : {self.vdd};

    /* default attributes */
    default_cell_leakage_power : 0.0;
    default_fanout_load : 1.0;
    default_max_fanout : 4.0;
    default_connection_class : universal;
    default_inout_pin_cap : 1.0;
    default_input_pin_cap : 1.0;
    default_output_pin_cap : 0.0;
    default_max_transition : 2.0;
    default_operating_conditions : typical;
    default_leakage_power_density : 0.0;

    voltage_map ( VDD, {self.vdd} );
    voltage_map ( GND, 0 );
    
    lu_table_template({self.cell_name}_delay_template) {{
        variable_1 : input_net_transition;
        variable_2 : total_output_net_capacitance;
        index_1 ("{', '.join([f'{s:.3f}' for s in self.input_slews])}");
        index_2 ("{', '.join([f'{l/1000:.6f}' for l in self.output_loads])}");
    }}
    
    lu_table_template({self.cell_name}_slew_template) {{
        variable_1 : input_net_transition;
        variable_2 : total_output_net_capacitance;
        index_1 ("{', '.join([f'{s:.3f}' for s in self.input_slews])}");
        index_2 ("{', '.join([f'{l/1000:.6f}' for l in self.output_loads])}");
    }}
    
    power_lut_template({self.cell_name}_power_template) {{
        variable_1 : input_transition_time;
        variable_2 : total_output_net_capacitance;
        index_1 ("{', '.join([f'{s:.3f}' for s in self.input_slews])}");
        index_2 ("{', '.join([f'{l/1000:.6f}' for l in self.output_loads])}");
    }}

cell({self.cell_name}) {{
    area : {self.cell_area:.5f};
    dont_use  : false;
    dont_touch : false;
    interface_timing : true;
    pg_pin(VDD) {{
        voltage_name : VDD;
        pg_type : primary_power;
    }}
    pg_pin(GND) {{
        voltage_name : GND;
        pg_type : primary_ground;
    }}
    leakage_power() {{
        value : {leakage_uw:.10f};
    }}
    cell_leakage_power : {leakage_uw:.10f};
    
''')
        
        # Input pins
        for pin in self.inputs:
            cap = self.input_cap_data.get(pin, 0.01)
            lib.append(f'''    pin({pin})   {{
        direction : input;
        capacitance : {cap:.10f};
    }}
''')
        
        # Output pins - use SPICE names internally, Liberty names in file
        for spice_pin in self.outputs:
            # Get Liberty name for this pin
            liberty_pin = self.liberty_pin_map[spice_pin]
            
            # Logic functions
            if spice_pin == 'S':
                func = "!((!(a ^ b)) & (!(c ^ d)))"
            else:  # cout -> C
                func = "d"
            
            lib.append(f'''    pin({liberty_pin})   {{
        direction : output;
        function : "{func}";
        min_capacitance : 0.000;
        max_capacitance : 0.100;
''')
            
            # Timing arcs - use SPICE names for keys
            for input_pin in self.inputs:
                arc_key = f"{input_pin}_{spice_pin}"  # Use SPICE name
                if arc_key not in timing_tables or timing_tables[arc_key] is None:
                    continue
                
                tables = timing_tables[arc_key]
                
                # Determine timing_sense: positive_unate for d->cout, non_unate for others
                if spice_pin == 'cout' and input_pin == 'd':
                    timing_sense = "positive_unate"
                else:
                    timing_sense = "non_unate"
                
                lib.append(f'''        timing() {{
            related_pin : "{input_pin}";
            timing_type : combinational;
            timing_sense : {timing_sense};
            cell_rise({self.cell_name}_delay_template) {{
{self.format_lut(tables['cell_rise'])}
            }}
            rise_transition({self.cell_name}_slew_template) {{
{self.format_lut(tables['rise_transition'])}
            }}
            cell_fall({self.cell_name}_delay_template) {{
{self.format_lut(tables['cell_fall'])}
            }}
            fall_transition({self.cell_name}_slew_template) {{
{self.format_lut(tables['fall_transition'])}
            }}
        }}
''')
            
            # Power arcs - only for arcs that exist
            for input_pin in self.inputs:
                arc_key = f"{input_pin}_{spice_pin}"  # Use SPICE name
                
                # Only generate power arc if timing arc exists
                if arc_key in timing_tables and timing_tables[arc_key] is not None:
                    tables = timing_tables[arc_key]
                    rise_table = tables['rise_power']
                    fall_table = tables['fall_power']
                    
                    rise_block = self.format_power_lut(rise_table)
                    fall_block = self.format_power_lut(fall_table)
                    
                    lib.append(f'''        internal_power() {{
            related_pin : "{input_pin}";
            rise_power({self.cell_name}_power_template) {{
{rise_block}
            }}
            fall_power({self.cell_name}_power_template) {{
{fall_block}
            }}
        }}
''')
            
            lib.append('    }\n')
        
        lib.append('}\n}\n')
        
        with open(output_file, 'w') as f:
            f.write(''.join(lib))
        
        print(f"    Liberty file generated successfully")


def main():
    print("="*70)
    print("AKbar1 Liberty Generator (with E_TOTAL support)")
    print("Approximate 4-2 Compressor (24 transistors)")
    print("SPICE: S, cout | Liberty: S, C")
    print("="*70)
    
    debug_mode = '--debug' in sys.argv
    
    template_file = "AKbar1.sp"
    if not os.path.exists(template_file):
        print(f" Template not found: {template_file}")
        return 1
    
    print(f" Template found: {template_file}")
    
    gen = LibGenerator(debug_mode=debug_mode)
    use_xyce = gen.check_xyce()
    
    if not use_xyce:
        print("\n Cannot proceed without Xyce")
        return 1
    
    if debug_mode:
        print("\n[DEBUG MODE ENABLED]")
    
    print(f"\n  Configuration:")
    print(f"  Cell: {gen.cell_name}")
    print(f"  VDD: {gen.vdd} V")
    print(f"  Temp: {gen.temp} °C")
    print(f"  Area: {gen.cell_area} um²")
    print(f"  Logic: S = (a XNOR b) NAND (c XNOR d), cout = d")
    
    # Leakage power
    gen.leakage_power = gen.measure_leakage_power(template_file)
    
    # Calculate input capacitances
    print(f"\n Calculating input capacitances...")
    for pin in gen.inputs:
        cap = gen.calculate_input_capacitance(pin)
        gen.input_cap_data[pin] = cap
        print(f"  {pin}: {cap:.6f} pF")
    
    # Timing arcs
    print(f"\n  Characterizing timing arcs...")
    timing_tables = {}
    
    for inp in gen.inputs:
        for outp in gen.outputs:
            arc_key = f"{inp}_{outp}"
            result = gen.characterize_arc(template_file, inp, outp, use_xyce)
            if result is not None:
                timing_tables[arc_key] = result
    
    # Generate Liberty
    output_file = "AKbar1.lib"
    gen.generate_liberty(output_file, timing_tables)
    
    # Summary
    print("\n" + "="*70)
    print(" COMPLETE")
    print("="*70)
    print(f"Simulation success rate: {gen.sim_success}/{gen.sim_count}")
    
    print("\n Input Capacitance Summary:")
    for pin in gen.inputs:
        cap = gen.input_cap_data.get(pin, 0.01)
        print(f"  {pin}: {cap:.6f} pF")
    
    print(f"\n Leakage Power: {gen.leakage_power:.6f} uW")
    print(f"\n Output: {output_file}")
    
    return 0


if __name__ == "__main__":
    exit(main())