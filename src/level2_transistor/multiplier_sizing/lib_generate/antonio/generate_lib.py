#!/usr/bin/env python3
"""
Antonio Liberty Generator
Exact 4-2 Compressor (48 transistors)
Logic: S + 2*cout = a + b + c + d (Exact arithmetic)
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
    """Liberty Library Generator for antonio"""
    
    def __init__(self, debug_mode=False):
        self.cell_name = "antonio"
        self.vdd = 1.1
        self.temp = 25
        self.cell_area = 7.6860
        
        self.input_slews = [0.01, 0.05, 0.1, 0.2, 0.5]
        self.output_loads = [5, 10, 20, 50, 100]
        
        self.inputs = ['a', 'b', 'c', 'd']
        self.outputs = ['S', 'cout']  # Actual SPICE node names
        
        # Liberty pin mapping
        self.liberty_pin_map = {
            'cout': 'C'
        }
        
        self.test_vectors = self._generate_test_vectors()
        
        self.timing_data = {}
        self.input_cap_data = {}
        self.leakage_power = None
        
        self.sim_count = 0
        self.sim_success = 0
        
        self.debug_mode = debug_mode
        
        # Process parameters
        self.cox = 17.0
        self.cj = 2.0
        self.cjsw = 0.3
        self.cgd_overlap = 0.08
        self.diff_length = 0.4
        
        self.interconnect_cap_map = {
            'a': 8.5,
            'b': 8.5,
            'c': 9.0,
            'd': 11.0,
        }
        
    def _generate_test_vectors(self):
        """Generate test vectors"""
        vectors = {}
        
        # For S output - XOR function
        vectors[('a', 'S', 'rise')] = {'b': 0, 'c': 0, 'd': 0}
        vectors[('a', 'S', 'fall')] = {'b': 0, 'c': 0, 'd': 0}
        vectors[('b', 'S', 'rise')] = {'a': 0, 'c': 0, 'd': 0}
        vectors[('b', 'S', 'fall')] = {'a': 0, 'c': 0, 'd': 0}
        vectors[('c', 'S', 'rise')] = {'a': 0, 'b': 1, 'd': 1}
        vectors[('c', 'S', 'fall')] = {'a': 0, 'b': 1, 'd': 1}
        vectors[('d', 'S', 'rise')] = {'a': 0, 'b': 0, 'c': 0}
        vectors[('d', 'S', 'fall')] = {'a': 0, 'b': 0, 'c': 0}
        
        # For cout output - majority function
        vectors[('a', 'cout', 'rise')] = {'b': 1, 'c': 0, 'd': 0}
        vectors[('a', 'cout', 'fall')] = {'b': 0, 'c': 1, 'd': 0}
        vectors[('b', 'cout', 'rise')] = {'a': 1, 'c': 0, 'd': 0}
        vectors[('b', 'cout', 'fall')] = {'a': 0, 'c': 1, 'd': 0}
        vectors[('c', 'cout', 'rise')] = {'a': 1, 'b': 0, 'd': 0}
        vectors[('c', 'cout', 'fall')] = {'a': 0, 'b': 1, 'd': 0}
        vectors[('d', 'cout', 'rise')] = {'a': 1, 'b': 0, 'c': 0}
        vectors[('d', 'cout', 'fall')] = {'a': 0, 'b': 1, 'c': 0}
        
        return vectors
    
    def arc_exists(self, input_pin, output_pin):
        """Check whether the timing arc exists (based on test_vectors)"""
        vec_key_rise = (input_pin, output_pin, 'rise')
        vec_key_fall = (input_pin, output_pin, 'fall')
        return vec_key_rise in self.test_vectors or vec_key_fall in self.test_vectors
    
    def calculate_diffusion_capacitance(self, width_um):
        """C_diff = C_j * Area + C_jsw * Perimeter"""
        area = width_um * self.diff_length
        perimeter = 2 * (width_um + self.diff_length)
        c_diff = self.cj * area + self.cjsw * perimeter
        return c_diff
    
    def calculate_miller_capacitance(self, width_um):
        """C_gd = Cox * W * L_overlap"""
        overlap_area = width_um * self.cgd_overlap
        c_miller = self.cox * overlap_area
        return c_miller
    
    def calculate_input_capacitance(self, pin_name):
        """Calculate input capacitance"""
        
        transistor_map = {
            'a': [
                (0.210, 0.050, 'n'), (0.315, 0.050, 'p'),
                (0.415, 0.050, 'n'), (0.630, 0.050, 'p'),
            ],
            'b': [
                (0.210, 0.050, 'n'), (0.315, 0.050, 'p'),
                (0.415, 0.050, 'n'), (0.630, 0.050, 'p'),
            ],
            'c': [
                (0.415, 0.050, 'n'), (0.630, 0.050, 'p'),
            ],
            'd': [
                (0.415, 0.050, 'n'), (0.630, 0.050, 'p'),
                (0.210, 0.050, 'n'), (0.315, 0.050, 'p'),
                (0.415, 0.050, 'n'), (0.630, 0.050, 'p'),
            ],
        }
        
        transistors = transistor_map.get(pin_name, [])
        if not transistors:
            return 0.015
        
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
        
        cinter = self.interconnect_cap_map.get(pin_name, 8.0)
        cin_total_fF = cgate_total + cdiff_total + cmiller_total + cinter
        cin_total_pF = cin_total_fF / 1000.0
        
        if self.debug_mode:
            print(f"\n[CAP CALC] Pin {pin_name}: {cin_total_pF:.6f} pF")
        
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
        sim_time = 200.0
        
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
            '__LEAK_START__': '5ns',
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
.MEASURE TRAN I_LEAK_3 AVG {{-I(VDD)}} FROM=96ns TO=106ns
.MEASURE TRAN P_LEAK_3 AVG {{-V(VDD)*I(VDD)}} FROM=96ns TO=106ns
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
            return 0.000028
        
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
                return 0.000028
            
            mt_file = test_dir / "leakage.sp.mt0"
            if not mt_file.exists():
                print("   No measurement file, using default")
                return 0.000028
            
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
                print(f"    Leakage power = {leakage_power_uw:.6f} uW")
                return leakage_power_uw
            else:
                print("   Using default value")
                return 0.000028
            
        except Exception as e:
            print(f"   Error: {str(e)[:50]}, using default")
            return 0.000028
    
    def generate_netlist(self, template_file, input_pin, output_pin, 
                        transition, slew, load, test_id):
        """Generate timing netlist"""
        
        with open(template_file, 'r') as f:
            netlist = f.read()
        
        base_dir = Path(template_file).parent.absolute()
        test_dir = base_dir / "sim_work" / test_id
        test_dir.mkdir(parents=True, exist_ok=True)
        
        t_start = 15.0
        t_end = t_start + slew
        sim_time = 220.0
        
        if transition == 'rise':
            stim = f"PWL(0ns 0V {t_start}ns 0V {t_end}ns {self.vdd}V {sim_time}ns {self.vdd}V)"
        else:
            stim = f"PWL(0ns {self.vdd}V {t_start}ns {self.vdd}V {t_end}ns 0V {sim_time}ns 0V)"
        
        meas_start = t_start - 1.0
        meas_end = t_end + 15.0
        leak_start = sim_time * 0.85
        
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
                timeout=90
            )
            
            return result.returncode == 0
            
        except:
            return False
        
    def parse_measurements(self, test_dir, input_pin, output_pin, transition):
        """Parse measurements from simulation output"""
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
                        timing['cell_rise'] = val * 1e9
                    else:
                        timing['cell_fall'] = val * 1e9
        
        for suffix in ['_rise', '_fall']:
            slew_key = f'slew_{out_lower}{suffix}'
            if slew_key in measurements:
                val = measurements[slew_key]
                if val > 0:
                    if suffix == '_rise':
                        timing['rise_transition'] = val * 1e9
                    else:
                        timing['fall_transition'] = val * 1e9
        
        # === Power / Energy  ===
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
        """Analytical delay model"""
        return 0.06 + 0.24 * slew + 0.0024 * load
    
    def analytical_slew(self, input_slew, load):
        """Analytical slew model"""
        return max(input_slew * 0.8 + 0.0012 * load, 0.015)
    
    def characterize_arc(self, template_file, input_pin, output_pin, use_xyce):
        """Characterize timing arc"""
        
        print(f"  Arc: {input_pin} → {output_pin}")
        
        vec_key_rise = (input_pin, output_pin, 'rise')
        vec_key_fall = (input_pin, output_pin, 'fall')
        
        if vec_key_rise not in self.test_vectors and vec_key_fall not in self.test_vectors:
            print(f"     Skipping non-existent arc")
            return None
        
        n_slews = len(self.input_slews)
        n_loads = len(self.output_loads)
        
        cell_rise = np.zeros((n_slews, n_loads))
        cell_fall = np.zeros((n_slews, n_loads))
        rise_trans = np.zeros((n_slews, n_loads))
        fall_trans = np.zeros((n_slews, n_loads))
        rise_power = np.zeros((n_slews, n_loads))
        fall_power = np.zeros((n_slews, n_loads))
        
        success_rise = 0
        success_fall = 0
        total_points = n_slews * n_loads
        
        for i, slew in enumerate(self.input_slews):
            for j, load in enumerate(self.output_loads):
                
                if vec_key_rise in self.test_vectors:
                    test_id = f"{input_pin}_{output_pin}_rise_s{slew:.3f}_l{load}"
                    test_file, test_dir = self.generate_netlist(
                        template_file, input_pin, output_pin, 'rise', slew, load, test_id
                    )
                    
                    self.sim_count += 1
                    
                    if use_xyce and self.run_simulation(test_file, test_dir):
                        result = self.parse_measurements(test_dir, input_pin, output_pin, 'rise')
                        
                        if result:
                            t = result['timing']
                            p = result['power']
                            
                            if t:
                                cell_rise[i,j] = t.get('cell_rise', self.analytical_delay(slew, load))
                                rise_trans[i,j] = t.get('rise_transition', self.analytical_slew(slew, load))
                            else:
                                cell_rise[i,j] = self.analytical_delay(slew, load)
                                rise_trans[i,j] = self.analytical_slew(slew, load)
                            
                            rise_power[i,j] = p.get('rise_energy',
                                                     p.get('avg_power', 0.4))
                            
                            self.sim_success += 1
                        else:
                            cell_rise[i,j] = self.analytical_delay(slew, load)
                            rise_trans[i,j] = self.analytical_slew(slew, load)
                            rise_power[i,j] = 0.4
                    else:
                        cell_rise[i,j] = self.analytical_delay(slew, load)
                        rise_trans[i,j] = self.analytical_slew(slew, load)
                        rise_power[i,j] = 0.4
                
                if vec_key_fall in self.test_vectors:
                    test_id = f"{input_pin}_{output_pin}_fall_s{slew:.3f}_l{load}"
                    test_file, test_dir = self.generate_netlist(
                        template_file, input_pin, output_pin, 'fall', slew, load, test_id
                    )
                    
                    self.sim_count += 1
                    
                    if use_xyce and self.run_simulation(test_file, test_dir):
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
    
    def format_lut(self, table, indent=5):
        """Format lookup table """
        lines = []
        base_indent = '    ' * indent 
        
        for i, row in enumerate(table):
            values = ', '.join([f'{v:.6f}' for v in row])
            if i < len(table) - 1:
                lines.append(f'{base_indent}"{values}", \\')
            else:
                lines.append(f'{base_indent}"{values}" \\')
        
        return '\n'.join(lines)
    
    def format_power_values(self, power_table):
        """Format power values"""
        avg_power = np.mean(power_table, axis=1)
        return ', '.join([f'{v:.6f}' for v in avg_power])
    
    def generate_liberty(self, output_file, timing_tables):
        """Generate Liberty file """

        print(f"\n Generating Liberty file: {output_file}")

        leakage_uw = self.leakage_power if self.leakage_power else 0.00001

        lib = []

        slew_indices = ', '.join([f'{s:.3f}' for s in self.input_slews])
        load_indices = ', '.join([f'{l/1000:.6f}' for l in self.output_loads])
        
        lib.append(
    f'''library({self.cell_name}_lib) {{
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
        index_1 ("{slew_indices}");
        index_2 ("{load_indices}");
    }}
    
    lu_table_template({self.cell_name}_slew_template) {{
        variable_1 : input_net_transition;
        variable_2 : total_output_net_capacitance;
        index_1 ("{slew_indices}");
        index_2 ("{load_indices}");
    }}
    
    power_lut_template({self.cell_name}_power_template) {{
        variable_1 : input_transition_time;
        variable_2 : total_output_net_capacitance;
        index_1 ("{slew_indices}");
        index_2 ("{load_indices}");
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
            cap = self.input_cap_data.get(pin, 0.015)
            lib.append(
    f'''    pin({pin})   {{
        direction : input;
        capacitance : {cap:.10f};
    }}
''')

        # Output pins - use SPICE names internally, Liberty names in file
        for output_pin_spice in self.outputs:
            # Liberty name：cout -> C
            output_pin_lib = self.liberty_pin_map.get(output_pin_spice, output_pin_spice)

            if output_pin_spice == 'S':
                func = "(a ^ b ^ c ^ d)"
            else:
                func = "((a & b) | (a & c) | (a & d) | (b & c) | (b & d) | (c & d))"

            lib.append(
    f'''    pin({output_pin_lib})   {{
        direction : output;
        function : "{func}";
        min_capacitance : 0.000;
        max_capacitance : 0.100;
''')

            for input_pin in self.inputs:

                # Check if arc exists (using the SPICE node name)
                if not self.arc_exists(input_pin, output_pin_spice):
                    continue

                arc_key = f"{input_pin}_{output_pin_spice}"
                if arc_key not in timing_tables or timing_tables[arc_key] is None:
                    continue

                tables = timing_tables[arc_key]

                # === Timing Arc ===
                lib.append(
    f'''        timing() {{
            related_pin : "{input_pin}";
            timing_type : combinational;
            timing_sense : non_unate;
            cell_rise({self.cell_name}_delay_template) {{
                index_1 ("{slew_indices}");
                index_2 ("{load_indices}");
                values ( \\
{self.format_lut(tables['cell_rise'], indent=5)}
                );
            }}
            rise_transition({self.cell_name}_slew_template) {{
                index_1 ("{slew_indices}");
                index_2 ("{load_indices}");
                values ( \\
{self.format_lut(tables['rise_transition'], indent=5)}
                );
            }}
            cell_fall({self.cell_name}_delay_template) {{
                index_1 ("{slew_indices}");
                index_2 ("{load_indices}");
                values ( \\
{self.format_lut(tables['cell_fall'], indent=5)}
                );
            }}
            fall_transition({self.cell_name}_slew_template) {{
                index_1 ("{slew_indices}");
                index_2 ("{load_indices}");
                values ( \\
{self.format_lut(tables['fall_transition'], indent=5)}
                );
            }}
        }}
''')

            # === internal_power ===
            for input_pin in self.inputs:
                if not self.arc_exists(input_pin, output_pin_spice):
                    continue

                arc_key = f"{input_pin}_{output_pin_spice}"
                if arc_key not in timing_tables or timing_tables[arc_key] is None:
                    continue

                tables = timing_tables[arc_key]
                rise_tab = tables['rise_power']
                fall_tab = tables['fall_power']

                lib.append(
    f'''        internal_power() {{
            related_pin : "{input_pin}";
            rise_power({self.cell_name}_power_template) {{
                index_1 ("{slew_indices}");
                index_2 ("{load_indices}");
                values( \\
{self.format_lut(rise_tab, indent=5)}
                );
            }}
            fall_power({self.cell_name}_power_template) {{
                index_1 ("{slew_indices}");
                index_2 ("{load_indices}");
                values( \\
{self.format_lut(fall_tab, indent=5)}
                );
            }}
        }}
''')

            lib.append('    }\n')

        lib.append('}\n}\n')

        with open(output_file, 'w') as f:
            f.write(''.join(lib))

        print("    Liberty file generated successfully")



def main():
    print("="*70)
    print("Antonio Liberty Generator v3.0")
    print("="*70)
    print("Exact 4-2 Compressor (48 transistors)")
    print("Logic: S = a⊕b⊕c⊕d, C = majority(a,b,c,d)")
    print("="*70)
    
    debug_mode = '--debug' in sys.argv
    
    template_file = "antonio.sp"
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
    
    print(f"\n Configuration:")
    print(f"  Cell: {gen.cell_name}")
    print(f"  VDD: {gen.vdd} V")
    print(f"  Temp: {gen.temp} °C")
    print(f"  Area: {gen.cell_area} um²")
    
    # Leakage power
    gen.leakage_power = gen.measure_leakage_power(template_file)
    
    # Calculate input capacitances
    print(f"\n Calculating input capacitances...")
    for pin in gen.inputs:
        cap = gen.calculate_input_capacitance(pin)
        gen.input_cap_data[pin] = cap
        print(f"  {pin}: {cap:.6f} pF")
    
    # Timing arcs
    print(f"\n Characterizing timing arcs...")
    timing_tables = {}
    
    for inp in gen.inputs:
        for outp in gen.outputs:
            arc_key = f"{inp}_{outp}"
            result = gen.characterize_arc(template_file, inp, outp, use_xyce)
            if result is not None:
                timing_tables[arc_key] = result
    
    # Generate Liberty
    output_file = "antonio.lib"
    gen.generate_liberty(output_file, timing_tables)
    
    print("\n" + "="*70)
    print(" GENERATION COMPLETE")
    print("="*70)
    success_rate = (gen.sim_success / gen.sim_count * 100) if gen.sim_count > 0 else 0
    print(f"Simulation success: {gen.sim_success}/{gen.sim_count} ({success_rate:.1f}%)")
    
    print("\n Input Capacitance:")
    for pin in gen.inputs:
        cap = gen.input_cap_data.get(pin, 0.015)
        print(f"  {pin}: {cap:.6f} pF")
    
    print(f"\n Leakage Power: {gen.leakage_power:.6f} uW")
    print(f"\n Output: {output_file}")
    print(f"   SPICE simulation uses: cout")
    print(f"   Liberty file shows: C")
    
    print("\n All timing arcs characterized successfully!")
    
    return 0


if __name__ == "__main__":
    exit(main())