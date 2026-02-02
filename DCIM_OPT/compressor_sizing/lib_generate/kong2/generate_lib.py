#!/usr/bin/env python3
"""
kong2 Liberty Generator 
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
    """Liberty Library Generator for kong2"""
    
    def __init__(self, debug_mode=False):
        self.cell_name = "kong2"
        self.vdd = 1.1
        self.temp = 25
        self.cell_area = 7.6825
        
        self.input_slews = [0.01, 0.05, 0.1, 0.2, 0.5]
        self.output_loads = [5, 10, 20, 50, 100]
        
        # SPICE domain: actual netlist node names
        self.inputs = ['a', 'b', 'c', 'd']
        self.outputs = ['S', 'cout']

        # Liberty domain: standard pin names for Liberty file
        # Map: SPICE name → Liberty name
        self.liberty_pin_map = {
            'cout': 'C'
        }
        
        self.test_vectors = self._generate_test_vectors()
        
        self.timing_data = {}
        self.input_cap_data = {}
        self.leakage_power = None
        
        self.sim_count = 0
        self.sim_success = 0
        self.parse_success = 0
        self.parse_fail = 0
        
        self.debug_mode = debug_mode
        
        # Process parameters
        self.cox = 17.0
        self.cj = 2.0
        self.cjsw = 0.3
        self.cgd_overlap = 0.08
        self.diff_length = 0.4
        
        self.interconnect_cap_map = {
            'a': 9.0, 'b': 9.0, 'c': 8.5, 'd': 8.5,
        }
    
    def get_liberty_pin_name(self, spice_name):
        """Convert SPICE pin name to Liberty pin name"""
        return self.liberty_pin_map.get(spice_name, spice_name)
    
    def _generate_test_vectors(self):
        """Generate test vectors for timing arcs"""
        vectors = {}
        
        # S output
        vectors[('a', 'S', 'rise')] = {'b': 1, 'c': 0, 'd': 1}
        vectors[('a', 'S', 'fall')] = {'b': 1, 'c': 0, 'd': 1}
        vectors[('b', 'S', 'rise')] = {'a': 1, 'c': 0, 'd': 1}
        vectors[('b', 'S', 'fall')] = {'a': 1, 'c': 0, 'd': 1}
        vectors[('c', 'S', 'rise')] = {'a': 1, 'b': 0, 'd': 1}
        vectors[('c', 'S', 'fall')] = {'a': 1, 'b': 0, 'd': 1}
        vectors[('d', 'S', 'rise')] = {'a': 1, 'b': 0, 'c': 1}
        vectors[('d', 'S', 'fall')] = {'a': 1, 'b': 0, 'c': 1}
        
        # cout output
        vectors[('a', 'cout', 'rise')] = {'b': 1, 'c': 0, 'd': 0}
        vectors[('a', 'cout', 'fall')] = {'b': 1, 'c': 0, 'd': 0}
        vectors[('b', 'cout', 'rise')] = {'a': 1, 'c': 0, 'd': 0}
        vectors[('b', 'cout', 'fall')] = {'a': 1, 'c': 0, 'd': 0}
        vectors[('c', 'cout', 'rise')] = {'a': 0, 'b': 0, 'd': 1}
        vectors[('c', 'cout', 'fall')] = {'a': 0, 'b': 0, 'd': 1}
        vectors[('d', 'cout', 'rise')] = {'a': 0, 'b': 0, 'c': 1}
        vectors[('d', 'cout', 'fall')] = {'a': 0, 'b': 0, 'c': 1}
        
        return vectors
    
    def calculate_diffusion_capacitance(self, width_um):
        area = width_um * self.diff_length
        perimeter = 2 * (width_um + self.diff_length)
        c_diff = self.cj * area + self.cjsw * perimeter
        return c_diff
    
    def calculate_miller_capacitance(self, width_um):
        overlap_area = width_um * self.cgd_overlap
        c_miller = self.cox * overlap_area
        return c_miller
    
    def calculate_input_capacitance(self, pin_name):
        """Calculate input capacitance using transistor dimensions"""
        
        transistor_map = {
            'a': [
                (0.415, 0.050, 'n'), (0.630, 0.050, 'p'),
                (0.415, 0.050, 'n'), (0.630, 0.050, 'p'),
                (0.210, 0.050, 'n'), (0.415, 0.050, 'n'),
                (0.315, 0.050, 'p'), (0.630, 0.050, 'p'),
            ],
            'b': [
                (0.415, 0.050, 'n'), (0.630, 0.050, 'p'),
                (0.415, 0.050, 'n'), (0.630, 0.050, 'p'),
                (0.210, 0.050, 'n'), (0.415, 0.050, 'n'),
                (0.315, 0.050, 'p'), (0.630, 0.050, 'p'),
            ],
            'c': [
                (0.415, 0.050, 'n'), (0.630, 0.050, 'p'),
                (0.415, 0.050, 'n'), (0.630, 0.050, 'p'),
                (0.415, 0.050, 'n'), (0.630, 0.050, 'p'),
            ],
            'd': [
                (0.415, 0.050, 'n'), (0.630, 0.050, 'p'),
                (0.415, 0.050, 'n'), (0.630, 0.050, 'p'),
                (0.415, 0.050, 'n'), (0.630, 0.050, 'p'),
            ],
        }
        
        transistors = transistor_map.get(pin_name, [])
        if not transistors:
            return 0.01
        
        cgate_total = sum(self.cox * w * l for w, l, _ in transistors)
        cdiff_total = sum(self.calculate_diffusion_capacitance(w) for w, _, _ in transistors)
        cmiller_total = sum(self.calculate_miller_capacitance(w) for w, _, _ in transistors)
        cinter = self.interconnect_cap_map.get(pin_name, 7.5)
        
        cin_total_pF = (cgate_total + cdiff_total + cmiller_total + cinter) / 1000.0
        
        if self.debug_mode:
            print(f"\n[CAP] {pin_name}: {cin_total_pF:.10f} pF")
        
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
        
        voltage_sources = [f'V{pin} {pin} 0 DC 0V' for pin in self.inputs]
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
            '__LEAK_START__': '160ns',
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
        cleaned_lines = [f'* REMOVED: {line}' if line.strip().lower().startswith(('.include', '.lib')) else line 
                        for line in lines]
        netlist = '\n'.join(cleaned_lines)
        
        multi_window_measurements = '''
.MEASURE TRAN I_LEAK_1 AVG {-I(VDD)} FROM=28ns TO=35ns
.MEASURE TRAN P_LEAK_1 AVG {-V(VDD)*I(VDD)} FROM=28ns TO=35ns
.MEASURE TRAN I_LEAK_2 AVG {-I(VDD)} FROM=62ns TO=72ns
.MEASURE TRAN P_LEAK_2 AVG {-V(VDD)*I(VDD)} FROM=62ns TO=72ns
.MEASURE TRAN I_LEAK_3 AVG {-I(VDD)} FROM=175ns TO=195ns
.MEASURE TRAN P_LEAK_3 AVG {-V(VDD)*I(VDD)} FROM=175ns TO=195ns
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
            return 0.0000299558
        
        try:
            cmd = [self.xyce_cmd, test_file.name]
            result = subprocess.run(cmd, cwd=str(test_dir.absolute()),
                                  capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                if self.debug_mode:
                    print(f"   Simulation stderr: {result.stderr[:200]}")
                print("   Simulation failed, using default")
                return 0.0000299558
            
            mt_file = test_dir / "leakage.sp.mt0"
            if not mt_file.exists():
                print("   No measurement file, using default")
                return 0.0000299558
            
            measurements = {}
            with open(mt_file, 'r') as f:
                content = f.read()
                for line in content.split('\n'):
                    match = re.match(r'^\s*(\w+)\s*=\s*([+-]?\d+\.?\d*[eE]?[+-]?\d*)', 
                                   line, re.IGNORECASE)
                    if match:
                        name = match.group(1).lower()
                        value = float(match.group(2))
                        measurements[name] = value
            
            p_leak = measurements.get('p_static_avg', 0)
            
            if p_leak and abs(p_leak) > 1e-15:
                leakage_power_uw = abs(p_leak) * 1e6
                print(f"   Leakage power = {leakage_power_uw:.10f} uW")
                return leakage_power_uw
            else:
                print("   Using default value")
                return 0.0000299558
            
        except Exception as e:
            if self.debug_mode:
                import traceback
                print(f"   Full error: {traceback.format_exc()}")
            print(f"   Error: {str(e)[:50]}, using default")
            return 0.0000299558
    
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
        sim_time = 220.0
        
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
        filtered_lines = [line for line in lines 
                         if not ('V__INPUT_PIN__' in line and line.strip().startswith('V__INPUT_PIN__'))]
        netlist = '\n'.join(filtered_lines)
        
        netlist = re.sub(r'\.MEASURE.*Q_INPUT.*\n', '', netlist, flags=re.IGNORECASE)
        
        lines = netlist.split('\n')
        cleaned_lines = [f'* REMOVED: {line}' if line.strip().lower().startswith(('.include', '.lib')) else line 
                        for line in lines]
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
            result = subprocess.run(cmd, cwd=str(test_dir.absolute()),
                                  capture_output=True, text=True, timeout=60)
            return result.returncode == 0
        except:
            return False
    
    def parse_measurements(self, test_dir, input_pin, output_pin):
        """Parse measurements with enhanced pattern matching"""
        mt_file = test_dir / "test.sp.mt0"
        
        if not mt_file.exists():
            if self.debug_mode:
                print(f"\n      [PARSE FAIL] .mt0 file not found")
            return None
        
        measurements = {}
        try:
            with open(mt_file, 'r') as f:
                content = f.read()
                
                if self.debug_mode:
                    print(f"\n      [PARSE] Reading {mt_file.name}")
                
                for line in content.split('\n'):
                    match = re.match(r'^\s*(\w+)\s*=\s*([+-]?\d+\.?\d*(?:[eE][+-]?\d+)?)', 
                                line, re.IGNORECASE)
                    if match:
                        name = match.group(1).lower()
                        try:
                            value = float(match.group(2))
                            measurements[name] = value
                        except ValueError:
                            continue
        except Exception as e:
            if self.debug_mode:
                print(f"\n      [PARSE FAIL] Error reading file: {e}")
            return None
        
        if not measurements:
            if self.debug_mode:
                print(f"      [PARSE FAIL] No measurements parsed")
            return None
        
        if self.debug_mode:
            print(f"      [PARSE] Found {len(measurements)} measurements")
        
        timing = {}
        power = {}
        
        out_lower = output_pin.lower()
        
        delay_rise_patterns = [
            f'delay_{out_lower}_rise', f'delay{out_lower}rise', 
            f'delay___{out_lower}___rise', f'delay_rise_{out_lower}',
            f'{out_lower}_delay_rise', 'delay_rise', 't_delay_rise',
        ]
        
        delay_fall_patterns = [
            f'delay_{out_lower}_fall', f'delay{out_lower}fall',
            f'delay___{out_lower}___fall', f'delay_fall_{out_lower}',
            f'{out_lower}_delay_fall', 'delay_fall', 't_delay_fall',
        ]
        
        slew_rise_patterns = [
            f'slew_{out_lower}_rise', f'slew{out_lower}rise',
            f'slew___{out_lower}___rise', f'slew_rise_{out_lower}',
            f'{out_lower}_slew_rise', 'slew_rise', 't_slew_rise', 'rise_time',
        ]
        
        slew_fall_patterns = [
            f'slew_{out_lower}_fall', f'slew{out_lower}fall',
            f'slew___{out_lower}___fall', f'slew_fall_{out_lower}',
            f'{out_lower}_slew_fall', 'slew_fall', 't_slew_fall', 'fall_time',
        ]
        
        energy_patterns = ['e_total', 'etotal', 'energy_total', 'energy']
        
        for pattern in delay_rise_patterns:
            if pattern in measurements:
                val = measurements[pattern]
                if 0 < val < 1e-6:
                    timing['cell_rise'] = val * 1e9
                    if self.debug_mode:
                        print(f"      [PARSE]  Matched {pattern} = {val*1e9:.6f} ns -> cell_rise")
                    break
        
        for pattern in delay_fall_patterns:
            if pattern in measurements:
                val = measurements[pattern]
                if 0 < val < 1e-6:
                    timing['cell_fall'] = val * 1e9
                    if self.debug_mode:
                        print(f"      [PARSE]  Matched {pattern} = {val*1e9:.6f} ns -> cell_fall")
                    break
        
        for pattern in slew_rise_patterns:
            if pattern in measurements:
                val = measurements[pattern]
                if 0 < val < 1e-6:
                    timing['rise_transition'] = val * 1e9
                    if self.debug_mode:
                        print(f"      [PARSE]  Matched {pattern} = {val*1e9:.6f} ns -> rise_transition")
                    break
        
        for pattern in slew_fall_patterns:
            if pattern in measurements:
                val = measurements[pattern]
                if 0 < val < 1e-6:
                    timing['fall_transition'] = val * 1e9
                    if self.debug_mode:
                        print(f"      [PARSE]  Matched {pattern} = {val*1e9:.6f} ns -> fall_transition")
                    break
        
        for pattern in energy_patterns:
            if pattern in measurements:
                val = measurements[pattern]
                if abs(val) > 0:
                    power['energy'] = abs(val) * 1e12  # J -> pJ
                    if self.debug_mode:
                        print(f"      [PARSE]  Matched {pattern} = {power['energy']:.6f} pJ -> energy")
                    break
        
        if 'p_avg' in measurements and measurements['p_avg'] > 0:
            power['avg_power'] = measurements['p_avg'] * 1e6
            if self.debug_mode:
                print(f"      [PARSE]  Power = {power['avg_power']:.6f} uW")
        
        if not timing:
            if self.debug_mode:
                print(f"      [PARSE FAIL] No valid timing data extracted")
            return None
        
        if self.debug_mode:
            print(f"      [PARSE SUCCESS] Extracted {len(timing)} timing values")
        
        return {'timing': timing, 'power': power}
    
    def analytical_delay(self, slew, load):
        return 0.055 + 0.22 * slew + 0.0022 * load
    
    def analytical_slew(self, input_slew, load):
        return max(input_slew * 0.85 + 0.0011 * load, 0.016)
    
    def arc_exists(self, input_pin, output_pin):
        """Check if this timing arc exists"""
        vec_key_rise = (input_pin, output_pin, 'rise')
        vec_key_fall = (input_pin, output_pin, 'fall')
        return vec_key_rise in self.test_vectors or vec_key_fall in self.test_vectors
    
    def characterize_arc(self, template_file, input_pin, output_pin, use_xyce):
        """Characterize timing arc"""
        
        print(f"  Arc: {input_pin} → {output_pin}")
        
        if not self.arc_exists(input_pin, output_pin):
            print(f"    Skipping non-existent arc")
            return None
        
        n_slews = len(self.input_slews)
        n_loads = len(self.output_loads)
        
        cell_rise = np.zeros((n_slews, n_loads))
        cell_fall = np.zeros((n_slews, n_loads))
        rise_trans = np.zeros((n_slews, n_loads))
        fall_trans = np.zeros((n_slews, n_loads))
        rise_energy = np.zeros((n_slews, n_loads))
        fall_energy = np.zeros((n_slews, n_loads))
        
        vec_key_rise = (input_pin, output_pin, 'rise')
        vec_key_fall = (input_pin, output_pin, 'fall')
        
        rise_parse_success = 0
        fall_parse_success = 0
        
        for i, slew in enumerate(self.input_slews):
            for j, load in enumerate(self.output_loads):
                
                # Rise
                if vec_key_rise in self.test_vectors:
                    test_id = f"{input_pin}_{output_pin}_rise_s{slew:.3f}_l{load}"
                    test_file, test_dir = self.generate_netlist(
                        template_file, input_pin, output_pin, 'rise', slew, load, test_id
                    )
                    
                    self.sim_count += 1
                    
                    if use_xyce and self.run_simulation(test_file, test_dir):
                        self.sim_success += 1
                        result = self.parse_measurements(test_dir, input_pin, output_pin)
                        
                        if result and result['timing']:
                            t = result['timing']
                            p = result['power']
                            
                            cell_rise[i,j] = t.get('cell_rise', self.analytical_delay(slew, load))
                            rise_trans[i,j] = t.get('rise_transition', self.analytical_slew(slew, load))
                            rise_energy[i,j] = p.get('energy', 0.6)
                            
                            self.parse_success += 1
                            rise_parse_success += 1
                        else:
                            self.parse_fail += 1
                            cell_rise[i,j] = self.analytical_delay(slew, load)
                            rise_trans[i,j] = self.analytical_slew(slew, load)
                            rise_energy[i,j] = 0.6
                    else:
                        cell_rise[i,j] = self.analytical_delay(slew, load)
                        rise_trans[i,j] = self.analytical_slew(slew, load)
                        rise_energy[i,j] = 0.6
                
                # Fall
                if vec_key_fall in self.test_vectors:
                    test_id = f"{input_pin}_{output_pin}_fall_s{slew:.3f}_l{load}"
                    test_file, test_dir = self.generate_netlist(
                        template_file, input_pin, output_pin, 'fall', slew, load, test_id
                    )
                    
                    self.sim_count += 1
                    
                    if use_xyce and self.run_simulation(test_file, test_dir):
                        self.sim_success += 1
                        result = self.parse_measurements(test_dir, input_pin, output_pin)
                        
                        if result and result['timing']:
                            t = result['timing']
                            p = result['power']
                            
                            cell_fall[i,j] = t.get('cell_fall', self.analytical_delay(slew, load))
                            fall_trans[i,j] = t.get('fall_transition', self.analytical_slew(slew, load))
                            fall_energy[i,j] = p.get('energy', 0.6)
                            
                            self.parse_success += 1
                            fall_parse_success += 1
                        else:
                            self.parse_fail += 1
                            cell_fall[i,j] = self.analytical_delay(slew, load)
                            fall_trans[i,j] = self.analytical_slew(slew, load)
                            fall_energy[i,j] = 0.6
                    else:
                        cell_fall[i,j] = self.analytical_delay(slew, load)
                        fall_trans[i,j] = self.analytical_slew(slew, load)
                        fall_energy[i,j] = 0.6
                
                completed = (i * n_loads + j + 1)
                total = n_slews * n_loads
                print(f"\r    Progress: {completed}/{total} points", end='', flush=True)
        
        print(f"\n    Parse success: Rise={rise_parse_success}/25, Fall={fall_parse_success}/25")
        
        return {
            'cell_rise': cell_rise,
            'cell_fall': cell_fall,
            'rise_transition': rise_trans,
            'fall_transition': fall_trans,
            'rise_energy': rise_energy,
            'fall_energy': fall_energy,
        }
    
    def format_lut(self, table, indent=4):
        """Format lookup table with index_1, index_2, values() - unified format"""
        ind = '    ' * indent
        ind_values = '    ' * (indent + 1)
        
        idx1 = ', '.join([f'{s:.3f}' for s in self.input_slews])
        idx2 = ', '.join([f'{l/1000:.6f}' for l in self.output_loads])
        
        lines = []
        lines.append(f'{ind}index_1 ("{idx1}");')
        lines.append(f'{ind}index_2 ("{idx2}");')
        lines.append(f'{ind}values( \\')
        
        for i, row in enumerate(table):
            values = ', '.join([f'{v:.6f}' for v in row])
            if i < len(table) - 1:
                lines.append(f'{ind_values}"{values}", \\')
            else:
                lines.append(f'{ind_values}"{values}" \\')
        
        lines.append(f'{ind});')
        return '\n'.join(lines)
    
    def generate_liberty(self, output_file, timing_tables):
        """Generate Liberty file with standardized v2.1 format"""
        
        print(f"\n▸ Generating Liberty file: {output_file}")
        
        leakage_uw = self.leakage_power if self.leakage_power else 0.055
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        lib = []
        
        # Header and library definition
        lib.append(f'''
library({self.cell_name}_lib) {{
    delay_model : table_lookup;
    time_unit : "1ns";
    voltage_unit : "1V";
    current_unit : "1uA";
    resistance_unit : "1kohm";
    capacitive_load_unit(1, pF);
    leakage_power_unit : "1uW";
    energy_unit : "1pJ";
    pulling_resistance_unit : "1kohm";
    
    operating_conditions(typical) {{
        process : 1.0;
        temperature : {self.temp:.3f};
        voltage : {self.vdd};
        tree_type : balanced_tree;
    }}
    
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
    
    default_cell_leakage_power : 0.0;
    default_fanout_load : 1.0;
    default_max_fanout : 16.0;
    default_connection_class : universal;
    default_inout_pin_cap : 1.0;
    default_input_pin_cap : 1.0;
    default_output_pin_cap : 0.0;
    default_max_transition : 1.5;
    default_leakage_power_density : 0.0;
    
    voltage_map ( VDD, {self.vdd} );
    voltage_map ( GND, 0 );
    
    lu_table_template({self.cell_name}_delay_template) {{
        variable_1 : input_net_transition;
        variable_2 : total_output_net_capacitance;
        index_1 ("{', '.join([f'{s:.3f}' for s in self.input_slews])}");
        index_2 ("{', '.join([f'{l/1000:.6f}' for l in self.output_loads])}");
    }}
    
    power_lut_template({self.cell_name}_energy_template) {{
        variable_1 : input_transition_time;
        variable_2 : total_output_net_capacitance;
        index_1 ("{', '.join([f'{s:.3f}' for s in self.input_slews])}");
        index_2 ("{', '.join([f'{l/1000:.6f}' for l in self.output_loads])}");
    }}
    
cell({self.cell_name}) {{
    area : {self.cell_area:.5f};
    dont_use : false;
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
    cell_leakage_power : {leakage_uw:.10f};''')

        # Input pins
        for pin in self.inputs:
            cap = self.input_cap_data.get(pin, 0.01)
            lib.append(f'''
    pin({pin}) {{
        direction : input;
        capacitance : {cap:.10f};
    }}''')

        # Output pins
        for output_pin_spice in self.outputs:
            output_pin_lib = self.get_liberty_pin_name(output_pin_spice)
            
            if output_pin_spice == 'S':
                func = "(a ^ b ^ c ^ d)"
            else:  # cout
                func = "((a & b) | (c & d) | ((a | b) & (c | d)))"
            
            lib.append(f'''
    pin({output_pin_lib}) {{
        direction : output;
        function : "{func}";
        min_capacitance : 0.000;
        max_capacitance : 0.500;''')
            
            # Timing arcs
            for input_pin in self.inputs:
                arc_key = f"{input_pin}_{output_pin_spice}"
                
                if arc_key not in timing_tables or timing_tables[arc_key] is None:
                    continue
                
                tables = timing_tables[arc_key]
                
                lib.append(f'''
        timing() {{
            related_pin : "{input_pin}";
            timing_type : combinational;
            timing_sense : non_unate;
            cell_rise({self.cell_name}_delay_template) {{
{self.format_lut(tables['cell_rise'], indent=4)}
            }}
            rise_transition({self.cell_name}_delay_template) {{
{self.format_lut(tables['rise_transition'], indent=4)}
            }}
            cell_fall({self.cell_name}_delay_template) {{
{self.format_lut(tables['cell_fall'], indent=4)}
            }}
            fall_transition({self.cell_name}_delay_template) {{
{self.format_lut(tables['fall_transition'], indent=4)}
            }}
        }}''')
            
            # Power arcs
            for input_pin in self.inputs:
                arc_key = f"{input_pin}_{output_pin_spice}"
                
                if arc_key not in timing_tables or timing_tables[arc_key] is None:
                    continue
                
                tables = timing_tables[arc_key]
                
                lib.append(f'''
        internal_power() {{
            related_pin : "{input_pin}";
            rise_power({self.cell_name}_energy_template) {{
{self.format_lut(tables['rise_energy'], indent=4)}
            }}
            fall_power({self.cell_name}_energy_template) {{
{self.format_lut(tables['fall_energy'], indent=4)}
            }}
        }}''')
            
            lib.append(f'''
    }}''')
        
        # Close cell and library
        lib.append(f'''
}}
}}''')
        
        with open(output_file, 'w') as f:
            f.write(''.join(lib))
        
        print(f"   Liberty file generated successfully")


def main():
    print("="*70)
    print("kong2 Liberty Generator v2.1 - Format Fixed & Standardized")
    print("Dual naming: cout (SPICE) → C (Liberty)")
    print("="*70)
    
    debug_mode = '--debug' in sys.argv
    
    template_file = "kong2.sp"
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
        print("  Will show detailed measurement parsing info")
    
    print(f"\n Configuration:")
    print(f"  Cell: {gen.cell_name}")
    print(f"  VDD: {gen.vdd}V")
    print(f"  Temp: {gen.temp}°C")
    print(f"  Area: {gen.cell_area} um²")
    print(f"  Pin mapping: cout (SPICE) → C (Liberty)")
    
    # Leakage power
    gen.leakage_power = gen.measure_leakage_power(template_file)
    
    # Calculate input capacitances
    print(f"\n Calculating input capacitances...")
    for pin in gen.inputs:
        cap = gen.calculate_input_capacitance(pin)
        gen.input_cap_data[pin] = cap
        print(f"  {pin}: {cap:.10f} pF")
    
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
    output_file = "kong2.lib"
    gen.generate_liberty(output_file, timing_tables)
    
    # Summary
    print("\n" + "="*70)
    print(" COMPLETE")
    print("="*70)
    print(f"Simulation run rate: {gen.sim_success}/{gen.sim_count}")
    print(f"Parse success rate: {gen.parse_success}/{gen.sim_success}")
    if gen.parse_fail > 0:
        print(f"  Parse failures: {gen.parse_fail}")
        print(f"  (Using analytical model for failed points)")
    
    print(f"\n▸ Output: {output_file}")
    
    return 0


if __name__ == "__main__":
    exit(main())