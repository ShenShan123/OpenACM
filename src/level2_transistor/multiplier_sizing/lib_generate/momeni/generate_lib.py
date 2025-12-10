#!/usr/bin/env python3
"""
momeni Liberty Generator
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
    """Liberty Library Generator for momeni"""
    
    def __init__(self, debug_mode=False):
        self.cell_name = "momeni"
        self.vdd = 1.1
        self.temp = 25
        self.cell_area = 4.2123
        
        self.input_slews = [0.01, 0.05, 0.1, 0.2, 0.5]
        self.output_loads = [5, 10, 20, 50, 100]
        
        self.inputs = ['a', 'b', 'c', 'd']
        self.outputs = ['cout']

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
        self.parse_success = 0
        self.parse_fail = 0
        
        self.debug_mode = debug_mode
        
        self.data_used = 0
        self.data_skipped = 0
        
        # Process parameters
        self.cox = 17.0
        self.cj = 2.0
        self.cjsw = 0.3
        self.cgd_overlap = 0.08
        self.diff_length = 0.4
        
        self.interconnect_cap_map = {
            'a': 8.0, 'b': 8.0, 'c': 7.5, 'd': 7.5,
        }
        
    def _generate_test_vectors(self):
        """Generate test vectors"""
        vectors = {}
        
        # cout = (a & b) | (c & d)
        vectors[('a', 'cout', 'rise')] = {'b': 0, 'c': 1, 'd': 1}
        vectors[('a', 'cout', 'fall')] = {'b': 0, 'c': 1, 'd': 1}
        vectors[('b', 'cout', 'rise')] = {'a': 0, 'c': 1, 'd': 1}
        vectors[('b', 'cout', 'fall')] = {'a': 0, 'c': 1, 'd': 1}
        vectors[('c', 'cout', 'rise')] = {'a': 0, 'b': 1, 'd': 0}
        vectors[('c', 'cout', 'fall')] = {'a': 0, 'b': 1, 'd': 0}
        vectors[('d', 'cout', 'rise')] = {'a': 1, 'b': 0, 'c': 0}
        vectors[('d', 'cout', 'fall')] = {'a': 1, 'b': 0, 'c': 0}
        
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
        """Calculate input capacitance"""
        transistor_map = {
            'a': [
                (0.415, 0.050, 'n'), (0.630, 0.050, 'p'),
                (0.210, 0.050, 'n'), (0.315, 0.050, 'p'),
            ],
            'b': [
                (0.415, 0.050, 'n'), (0.630, 0.050, 'p'),
                (0.210, 0.050, 'n'), (0.315, 0.050, 'p'),
            ],
            'c': [
                (0.415, 0.050, 'n'), (0.630, 0.050, 'p'),
                (0.210, 0.050, 'n'), (0.315, 0.050, 'p'),
            ],
            'd': [
                (0.415, 0.050, 'n'), (0.630, 0.050, 'p'),
                (0.210, 0.050, 'n'), (0.315, 0.050, 'p'),
            ],
        }
        
        transistors = transistor_map.get(pin_name, [])
        if not transistors:
            return 0.01
        
        cgate_total = sum(self.cox * w * l for w, l, _ in transistors)
        cdiff_total = sum(self.calculate_diffusion_capacitance(w) for w, _, _ in transistors)
        cmiller_total = sum(self.calculate_miller_capacitance(w) for w, _, _ in transistors)
        cinter = self.interconnect_cap_map.get(pin_name, 7.0)
        
        cin_total_pF = (cgate_total + cdiff_total + cmiller_total + cinter) / 1000.0
        
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
        """Generate leakage netlist"""
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
            '__OUTPUT_PIN__': 'cout',
            '__OUTPUT_LOAD__': '10f',
            '__TSTEP__': '0.1ns',
            '__TSTOP__': f'{sim_time}ns',
            '__TMAX__': '0.5ns',
            '__LEAK_START__': '160ns',
        }
        
        for placeholder, value in replacements.items():
            netlist = netlist.replace(placeholder, value)
        
        pattern_start = netlist.find('* Input under test')
        pattern_end = netlist.find('* Output loads')
        
        if pattern_start != -1 and pattern_end != -1:
            before = netlist[:pattern_start]
            after = netlist[pattern_end:]
            netlist = before + ' All inputs at 0V for leakage\n' + vsrc_section + '\n\n' + after
        
        multi_window_measurements = '''
.MEASURE TRAN I_LEAK_1 AVG {-I(VDD)} FROM=28ns TO=35ns
.MEASURE TRAN P_LEAK_1 AVG {-V(VDD)*I(VDD)} FROM=28ns TO=35ns
.MEASURE TRAN I_LEAK_2 AVG {-I(VDD)} FROM=62ns TO=72ns
.MEASURE TRAN P_LEAK_2 AVG {-V(VDD)*I(VDD)} FROM=62ns TO=72ns
.MEASURE TRAN I_LEAK_3 AVG {-I(VDD)} FROM=175ns TO=195ns
.MEASURE TRAN P_LEAK_3 AVG {-V(VDD)*I(VDD)} FROM=175ns TO=195ns
.MEASURE TRAN I_STATIC_AVG PARAM='(I_LEAK_1+I_LEAK_2+I_LEAK_3)/3'
.MEASURE TRAN P_STATIC_AVG PARAM='(P_LEAK_1+P_LEAK_2+P_LEAK_3)/3'

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
            return 0.0000179705
        
        try:
            cmd = [self.xyce_cmd, test_file.name]
            result = subprocess.run(cmd, cwd=str(test_dir.absolute()),
                                  capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                print("   Simulation failed, using default")
                return 0.0000179705
            
            mt_file = test_dir / "leakage.sp.mt0"
            if not mt_file.exists():
                print("   No measurement file, using default")
                return 0.0000179705
            
            measurements = {}
            with open(mt_file, 'r') as f:
                for line in f:
                    match = re.match(r'^\s*(\w+)\s*=\s*([+-]?\d+\.?\d*[eE]?[+-]?\d*)', 
                                   line, re.IGNORECASE)
                    if match:
                        measurements[match.group(1).lower()] = float(match.group(2))
            
            p_leak = measurements.get('p_static_avg', 0)
            
            if p_leak and abs(p_leak) > 1e-15:
                leakage_power_uw = abs(p_leak) * 1e6
                print(f"   Leakage power = {leakage_power_uw:.10f} uW")
                return leakage_power_uw
            else:
                print("   Using default value")
                return 0.0
            
        except Exception as e:
            print(f"   Error: {str(e)[:50]}, using default")
            return 0.0000179705
    
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
        sim_time = 520.0
        
        if transition == 'rise':
            stim = f"PWL(0ns 0V {t_start}ns 0V {t_end}ns {self.vdd}V {sim_time}ns {self.vdd}V)"
            cout_init = '0'
        else:
            stim = f"PWL(0ns {self.vdd}V {t_start}ns {self.vdd}V {t_end}ns 0V {sim_time}ns 0V)"
            cout_init = f'{self.vdd}V'
        
        vec_key = (input_pin, output_pin, transition)
        static_values = self.test_vectors.get(vec_key, {})
        
        vsrc_map = {'a': 'Va', 'b': 'Vb', 'c': 'Vc', 'd': 'Vd'}
        
        voltage_sources = [f'{vsrc_map[input_pin]} {input_pin} 0 {stim}']
        
        for pin in self.inputs:
            if pin != input_pin:
                value = static_values.get(pin, 0)
                dc_val = f'{self.vdd}V' if value == 1 else '0V'
                voltage_sources.append(f'{vsrc_map[pin]} {pin} 0 DC {dc_val}')
        
        vsrc_section = '\n'.join(voltage_sources)
        
        replacements = {
            '__VDD_VAL__': f'{self.vdd}V',
            '__TEMP_VAL__': str(self.temp),
            '__VDD_10__': f'{self.vdd * 0.1}',
            '__VDD_50__': f'{self.vdd * 0.5}',
            '__VDD_90__': f'{self.vdd * 0.9}',
            '__INPUT_PIN__': input_pin,
            '__OUTPUT_PIN__': output_pin,
            '__OUTPUT_LOAD__': f'{load}f',
            '__TSTEP__': '0.05ns',
            '__TSTOP__': f'{sim_time}ns',
            '__TMAX__': '0.2ns',
            '__LEAK_START__': f'{sim_time*0.8}ns',
            '__COUT_INIT__': cout_init,
        }
        
        for placeholder, value in replacements.items():
            netlist = netlist.replace(placeholder, value)
        
        pattern_start = netlist.find('* Input under test')
        pattern_end = netlist.find('* Output loads')
        
        if pattern_start != -1 and pattern_end != -1:
            before = netlist[:pattern_start]
            after = netlist[pattern_end:]
            netlist = before + f'* Input: {input_pin} ({transition})\n' + vsrc_section + '\n\n' + after
        
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
        
        # Energy patterns
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
        
        # E_TOTAL
        for pattern in energy_patterns:
            if pattern in measurements:
                val = measurements[pattern]
                if abs(val) > 0:
                    power['energy'] = abs(val) * 1e12  # pJ (picojoules)
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
        """Analytical delay model"""
        return 0.050 + 0.20 * slew + 0.0020 * load
    
    def analytical_slew(self, input_slew, load):
        """Analytical slew model"""
        return max(input_slew * 0.80 + 0.0010 * load, 0.015)
    
    def characterize_arc(self, template_file, input_pin, output_pin, use_xyce):
        """Characterize timing arc"""
        
        print(f"   Arc: {input_pin} → {output_pin}")
        
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
        rise_energy = np.zeros((n_slews, n_loads))  
        fall_energy = np.zeros((n_slews, n_loads)) 
        
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
                            rise_energy[i,j] = p.get('energy', 0.5)  # energy
                            
                            self.parse_success += 1
                            rise_parse_success += 1
                        else:
                            self.parse_fail += 1
                            cell_rise[i,j] = self.analytical_delay(slew, load)
                            rise_trans[i,j] = self.analytical_slew(slew, load)
                            rise_energy[i,j] = 0.006  
                    else:
                        cell_rise[i,j] = self.analytical_delay(slew, load)
                        rise_trans[i,j] = self.analytical_slew(slew, load)
                        rise_energy[i,j] = 0.006
                
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
                            fall_energy[i,j] = p.get('energy', 0.005)  
                            
                            self.parse_success += 1
                            fall_parse_success += 1
                        else:
                            self.parse_fail += 1
                            cell_fall[i,j] = self.analytical_delay(slew, load)
                            fall_trans[i,j] = self.analytical_slew(slew, load)
                            fall_energy[i,j] = 0.006
                    else:
                        cell_fall[i,j] = self.analytical_delay(slew, load)
                        fall_trans[i,j] = self.analytical_slew(slew, load)
                        fall_energy[i,j] = 0.006
                
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
    
    def format_lut_5x5(self, table, indent=4):
        """Format 5x5 lookup table"""
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
    
    def generate_liberty(self, output_file, timing_tables):
        """Generate Liberty file in ACCI1 format"""
        
        print(f"\n Generating Liberty file: {output_file}")
        
        leakage_uw = self.leakage_power if self.leakage_power else 0.048
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lib= []

        lib.append(f'''library({self.cell_name}_lib) {{ 
    delay_model : table_lookup;
    time_unit : "1ns";
    voltage_unit : "1V";
    current_unit : "1uA";
    resistance_unit : "1kohm";
    pulling_resistance_unit : "1kohm";
    capacitive_load_unit(1, pf);
    leakage_power_unit : "1uW";
    energy_unit : "1pJ";
    
    nom_process : 1.0;
    nom_voltage : {self.vdd};
    nom_temperature : {self.temp:.3f};
    
    operating_conditions(typical) {{
        process : 1.0;
        temperature : {self.temp:.3f};
        voltage : {self.vdd};
        tree_type : balanced_tree;
    }}
    
    default_operating_conditions : typical;
    
    voltage_map(VDD, {self.vdd});
    voltage_map(GND, 0);
    
    slew_lower_threshold_pct_rise : 10.0;
    slew_upper_threshold_pct_rise : 90.0;
    slew_lower_threshold_pct_fall : 10.0;
    slew_upper_threshold_pct_fall : 90.0;
    slew_derate_from_library : 1.0;
    
    input_threshold_pct_rise : 50.0;
    input_threshold_pct_fall : 50.0;
    output_threshold_pct_rise : 50.0;
    output_threshold_pct_fall : 50.0;
    
    default_input_pin_cap : 0.0100000000;
    default_output_pin_cap : 0.0;
    default_inout_pin_cap : 0.0100000000;
    default_fanout_load : 1.0;
    default_max_fanout : 16.0;
    default_max_transition : 1.5;
    default_cell_leakage_power : 0.0;
    default_leakage_power_density : 0.0;
    default_connection_class : universal;
    
    lu_table_template({self.cell_name}_delay_template) {{
        variable_1 : input_net_transition;
        variable_2 : total_output_net_capacitance;
        index_1("{', '.join([str(s) for s in self.input_slews])}");
        index_2("{', '.join([str(l/1000) for l in self.output_loads])}");
    }}
    
    power_lut_template({self.cell_name}_energy_template) {{
        variable_1 : input_transition_time;
        variable_2 : total_output_net_capacitance;
        index_1("{', '.join([str(s) for s in self.input_slews])}");
        index_2("{', '.join([str(l/1000) for l in self.output_loads])}");
    }}
    
    cell({self.cell_name}) {{
        area : {self.cell_area:.5f};
        dont_use : false;
        dont_touch : false;
        interface_timing : false;
        
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
            lib.append(f'''        pin({pin}) {{
        direction : input;
        capacitance : {cap:.10f};
        }}
        
''')
    
        # Output pins
        for output_pin_spice in self.outputs:
            output_pin_lib = self.liberty_pin_map.get(output_pin_spice, output_pin_spice)
            if output_pin_spice == 'S':
                func = "(a ^ b ^ c ^ d)"
            else:  # cout
                func = "((a & b) | (c & d) | ((a | b) & (c | d)))"
        
            lib.append(f'''        pin({output_pin_lib}) {{
        direction : output;
        function : "{func}";
        min_capacitance : 0.0;
        max_capacitance : 0.5;
            
''')
            # Timing arcs
            for input_pin in self.inputs:
                arc_key = f"{input_pin}_{output_pin_spice}"
                if arc_key not in timing_tables or timing_tables[arc_key] is None:
                    continue
                
                tables = timing_tables[arc_key]

                lib.append(f'''        timing() {{
            related_pin : "{input_pin}";
            timing_sense : non_unate;
            timing_type : combinational;
            cell_rise({self.cell_name}_delay_template) {{
{self.format_lut_5x5(tables['cell_rise'])}
            }}
            rise_transition({self.cell_name}_delay_template) {{
{self.format_lut_5x5(tables['rise_transition'])}
            }}
            cell_fall({self.cell_name}_delay_template) {{
{self.format_lut_5x5(tables['cell_fall'])}
            }}
            fall_transition({self.cell_name}_delay_template) {{
{self.format_lut_5x5(tables['fall_transition'])}
            }}
        }}            
''')
        
            # Power arcs 
            for input_pin in self.inputs:
                arc_key = f"{input_pin}_{output_pin_spice}"
                if arc_key in timing_tables and timing_tables[arc_key] is not None:
                    tables = timing_tables[arc_key]
                
                lib.append(f'''        internal_power() {{
            related_pin : "{input_pin}";
            rise_power({self.cell_name}_energy_template) {{
{self.format_lut_5x5(tables['rise_energy'])}
            }}
            fall_power({self.cell_name}_energy_template) {{
{self.format_lut_5x5(tables['fall_energy'])}
            }}
        }}
            
''')
        
            lib.append('        }\n        \n')
    
        lib.append('    }\n}\n')
        
        with open(output_file, 'w') as f:
            f.write(''.join(lib))
    
        print(f"   Liberty file generated successfully")


def main():
    print("="*70)
    print("momeni Liberty Generator ")
    print("Output format aligned with ACCI1.lib standard")
    print("="*70)
    
    debug_mode = '--debug' in sys.argv
    
    template_file = "momeni.sp"
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
    output_file = "momeni.lib"
    gen.generate_liberty(output_file, timing_tables)
    
    # Summary
    print("\n" + "="*70)
    print(" COMPLETE")
    print("="*70)
    print(f"Simulation run rate: {gen.sim_success}/{gen.sim_count}")
    print(f"Parse success rate: {gen.parse_success}/{gen.sim_success}")
    if gen.parse_fail > 0:
        print(f"   Parse failures: {gen.parse_fail}")
        print(f"    (Using analytical model for failed points)")
    
    print(f"\n Output: {output_file}")
    
    return 0


if __name__ == "__main__":
    exit(main())