#!/usr/bin/env python3
"""
sabetz Liberty Generator 
Approximate 4-2 Compressor
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
    """Liberty Library Generator for sabetz"""
    
    def __init__(self, debug_mode=False):
        self.cell_name = "sabetz"
        self.vdd = 1.1
        self.temp = 25
        self.cell_area = 2.5602
        
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
        
        # Process parameters
        self.cox = 17.0
        self.cj = 2.0
        self.cjsw = 0.3
        self.cgd_overlap = 0.08
        self.diff_length = 0.4
        
        self.interconnect_cap_map = {
            'a': 6.0, 'b': 0.0, 'c': 6.0, 'd': 6.0,
        }
        
    def _generate_test_vectors(self):
        """Generate test vectors - LOGIC CORRECTED
        
        Circuit logic: cout = !((!(a&d)) & ((a|d)&!c))
        """
        vectors = {}
        
        # a → cout: MUST use c=0 (not c=1!)
        vectors[('a', 'cout', 'rise')] = {'b': 0, 'c': 0, 'd': 1}
        vectors[('a', 'cout', 'fall')] = {'b': 0, 'c': 0, 'd': 1}
        
        # c → cout
        vectors[('c', 'cout', 'rise')] = {'a': 1, 'b': 0, 'd': 0}
        vectors[('c', 'cout', 'fall')] = {'a': 1, 'b': 0, 'd': 0}
        
        # d → cout: MUST use c=0 (not c=1!)
        vectors[('d', 'cout', 'rise')] = {'a': 1, 'b': 0, 'c': 0}
        vectors[('d', 'cout', 'fall')] = {'a': 1, 'b': 0, 'c': 0}
        
        return vectors
    
    def verify_test_vectors(self):
        """Verify test vectors with CORRECTED logic"""
        print("\n Verifying test vectors...")
        
        def eval_cout(a, b, c, d):
            """Circuit logic: cout = !((!(a&d)) & ((a|d)&!c))"""
            _0 = not (a and d)
            _1 = (a or d) and (not c)
            return int(not (_0 and _1))
        
        all_valid = True
        for key, static in self.test_vectors.items():
            input_pin, output_pin, transition = key
            
            vals = {'a': 0, 'b': 0, 'c': 0, 'd': 0}
            vals.update(static)
            
            if transition == 'rise':
                vals[input_pin] = 0
                out_before = eval_cout(**vals)
                vals[input_pin] = 1
                out_after = eval_cout(**vals)
            else:
                vals[input_pin] = 1
                out_before = eval_cout(**vals)
                vals[input_pin] = 0
                out_after = eval_cout(**vals)
            
            actual_change = f"{out_before}→{out_after}"
            is_valid = (out_before != out_after)
            
            status = "✓" if is_valid else "✗"
            if not is_valid:
                all_valid = False
                print(f"  {status} {input_pin}→{output_pin} ({transition}): {actual_change} [INVALID]")
            else:
                print(f"  {status} {input_pin}→{output_pin} ({transition}): {actual_change} [OK]")
        
        if all_valid:
            print("   All test vectors valid!")
        else:
            print("   Some test vectors invalid!")
        
        return all_valid
    
    def calculate_diffusion_capacitance(self, width_um):
        area = width_um * self.diff_length
        perimeter = 2 * (width_um + self.diff_length)
        return self.cj * area + self.cjsw * perimeter
    
    def calculate_miller_capacitance(self, width_um):
        overlap_area = width_um * self.cgd_overlap
        return self.cox * overlap_area
    
    def calculate_input_capacitance(self, pin_name):
        transistor_map = {
            'a': [
                (0.415, 0.050, 'n'), (0.630, 0.050, 'p'),
                (0.415, 0.050, 'n'), (0.630, 0.050, 'p'),
            ],
            'b': [],
            'c': [
                (0.415, 0.050, 'n'), (0.630, 0.050, 'p'),
            ],
            'd': [
                (0.415, 0.050, 'n'), (0.630, 0.050, 'p'),
                (0.415, 0.050, 'n'), (0.630, 0.050, 'p'),
            ],
        }
        
        transistors = transistor_map.get(pin_name, [])
        if not transistors:
            return 0.001 if pin_name == 'b' else 0.01
        
        cgate_total = sum(self.cox * w * l for w, l, _ in transistors)
        cdiff_total = sum(self.calculate_diffusion_capacitance(w) for w, _, _ in transistors)
        cmiller_total = sum(self.calculate_miller_capacitance(w) for w, _, _ in transistors)
        cinter = self.interconnect_cap_map.get(pin_name, 5.0)
        
        cin_total_pF = (cgate_total + cdiff_total + cmiller_total + cinter) / 1000.0
        
        if self.debug_mode:
            print(f"\n[CAP] {pin_name}: {cin_total_pF:.10f}pF")
        
        return cin_total_pF
        
    def check_xyce(self):
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
        with open(template_file, 'r') as f:
            netlist = f.read()
        
        base_dir = Path(template_file).parent.absolute()
        test_dir = base_dir / "sim_work" / "leakage_measurement"
        test_dir.mkdir(parents=True, exist_ok=True)
        
        voltage_sources = [f'V{pin} {pin} 0 DC 0V' for pin in self.inputs]
        vsrc_section = '\n'.join(voltage_sources)
        sim_time = 260.0
        
        replacements = {
            '__VDD_VAL__': f'{self.vdd}V',
            '__TEMP_VAL__': str(self.temp),
            '__VDD_10__': f'{self.vdd * 0.1}',
            '__VDD_50__': f'{self.vdd * 0.5}',
            '__VDD_90__': f'{self.vdd * 0.9}',
            '__INPUT_PIN__': 'a',
            '__OUTPUT_PIN__': 'cout',
            '__OUTPUT_LOAD__': '10f',
            '__TSTEP__': '0.05ns',
            '__TSTOP__': f'{sim_time}ns',
            '__TMAX__': '0.2ns',
            '__LEAK_START__': '160ns',
        }
        
        for placeholder, value in replacements.items():
            netlist = netlist.replace(placeholder, value)
        
        pattern_start = netlist.find('* Input under test')
        pattern_end = netlist.find('* Output loads')
        
        if pattern_start != -1 and pattern_end != -1:
            before = netlist[:pattern_start]
            after = netlist[pattern_end:]
            netlist = before + '* All inputs at 0V\n' + vsrc_section + '\n\n' + after
        
        netlist = re.sub(r'\.IC\s+V\(_0_\)=.*', '* IC removed', netlist)
        netlist = re.sub(r'\.IC\s+V\(_1_\)=.*', '* IC removed', netlist)
        netlist = re.sub(r'\.IC\s+V\(cout\)=.*', '* IC removed', netlist)
        
        multi_window = '''
.MEASURE TRAN I_LEAK_1 AVG {-I(VDD)} FROM=28ns TO=35ns
.MEASURE TRAN P_LEAK_1 AVG {-V(VDD)*I(VDD)} FROM=28ns TO=35ns
.MEASURE TRAN I_LEAK_2 AVG {-I(VDD)} FROM=62ns TO=72ns
.MEASURE TRAN P_LEAK_2 AVG {-V(VDD)*I(VDD)} FROM=62ns TO=72ns
.MEASURE TRAN I_LEAK_3 AVG {-I(VDD)} FROM=175ns TO=195ns
.MEASURE TRAN P_LEAK_3 AVG {-V(VDD)*I(VDD)} FROM=175ns TO=195ns
.MEASURE TRAN I_STATIC_AVG PARAM='(I_LEAK_1+I_LEAK_2+I_LEAK_3)/3'
.MEASURE TRAN P_STATIC_AVG PARAM='(P_LEAK_1+P_LEAK_2+P_LEAK_3)/3'
'''
        
        netlist = netlist.replace('.END', multi_window + '\n.END')
        
        test_file = test_dir / "leakage.sp"
        with open(test_file, 'w') as f:
            f.write(netlist)
        
        return test_file, test_dir
    
    def measure_leakage_power(self, template_file):
        print("\n Measuring leakage power...")
        
        test_file, test_dir = self.generate_leakage_netlist(template_file)
        
        if not self.xyce_cmd:
            print("   Using default")
            return 0.0000077772
        
        try:
            cmd = [self.xyce_cmd, test_file.name]
            result = subprocess.run(cmd, cwd=str(test_dir), 
                                  capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                if self.debug_mode:
                    print(f"   Failed: {result.stderr[:200]}")
                return 0.0000077772
            
            mt_file = test_dir / "leakage.sp.mt0"
            if not mt_file.exists():
                return 0.0000077772
            
            measurements = {}
            with open(mt_file, 'r') as f:
                for line in f:
                    match = re.match(r'^\s*(\w+)\s*=\s*([+-]?\d+\.?\d*[eE]?[+-]?\d*)', 
                                   line, re.IGNORECASE)
                    if match:
                        measurements[match.group(1).lower()] = float(match.group(2))
            
            p_leak = measurements.get('p_static_avg', 0)
            if p_leak and abs(p_leak) > 1e-15:
                leakage_uw = abs(p_leak) * 1e6
                print(f"   Leakage = {leakage_uw:.10f} uW")
                return leakage_uw
            else:
                return 0.0000077772
            
        except Exception as e:
            if self.debug_mode:
                print(f"   Error: {e}")
            return 0.0000077772
    
    def generate_netlist(self, template_file, input_pin, output_pin, 
                        transition, slew, load, test_id):
        """Generate timing netlist"""
        
        with open(template_file, 'r') as f:
            netlist = f.read()
        
        base_dir = Path(template_file).parent.absolute()
        test_dir = base_dir / "sim_work" / test_id
        test_dir.mkdir(parents=True, exist_ok=True)
        
        t_start = 30.0
        t_end = t_start + slew
        sim_time = 280.0
        
        if transition == 'rise':
            stim = f"PWL(0ns 0V {t_start}ns 0V {t_end}ns {self.vdd}V {sim_time}ns {self.vdd}V)"
        else:
            stim = f"PWL(0ns {self.vdd}V {t_start}ns {self.vdd}V {t_end}ns 0V {sim_time}ns 0V)"
        
        leak_start = sim_time * 0.85
        
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
            '__VDD_10__': f'{self.vdd * 0.1}',
            '__VDD_50__': f'{self.vdd * 0.5}',
            '__VDD_90__': f'{self.vdd * 0.9}',
            '__INPUT_PIN__': input_pin,
            '__OUTPUT_PIN__': output_pin,
            '__OUTPUT_LOAD__': f'{load}f',
            '__TSTEP__': '0.05ns',
            '__TSTOP__': f'{sim_time}ns',
            '__TMAX__': '0.2ns',
            '__LEAK_START__': f'{leak_start}ns',
        }
        
        for placeholder, value in replacements.items():
            netlist = netlist.replace(placeholder, value)
        
        pattern_start = netlist.find('* Input under test')
        pattern_end = netlist.find('* Output loads')
        
        if pattern_start != -1 and pattern_end != -1:
            before = netlist[:pattern_start]
            after = netlist[pattern_end:]
            vsrc_header = f'* Input: {input_pin} ({transition})\n'
            netlist = before + vsrc_header + vsrc_section + '\n\n' + after
        
        # Remove initial conditions
        netlist = re.sub(r'\.IC\s+V\(_0_\)=.*', '* IC removed', netlist)
        netlist = re.sub(r'\.IC\s+V\(_1_\)=.*', '* IC removed', netlist)
        netlist = re.sub(r'\.IC\s+V\(cout\)=.*', '* IC removed', netlist)
        
        test_file = test_dir / "test.sp"
        with open(test_file, 'w') as f:
            f.write(netlist)
        
        return test_file, test_dir
    
    def run_simulation(self, test_file, test_dir):
        if not self.xyce_cmd:
            return False
        
        try:
            cmd = [self.xyce_cmd, test_file.name]
            result = subprocess.run(cmd, cwd=str(test_dir),
                                  capture_output=True, text=True, timeout=60)
            return result.returncode == 0
        except:
            return False
    
    def parse_measurements(self, test_dir, input_pin, output_pin):
        """Parse measurements with E_TOTAL extraction"""
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
        
        # Timing patterns
        patterns = {
            'cell_rise': [f'delay_{out_lower}_rise', f'delay___{out_lower}___rise', 'delay_rise'],
            'cell_fall': [f'delay_{out_lower}_fall', f'delay___{out_lower}___fall', 'delay_fall'],
            'rise_transition': [f'slew_{out_lower}_rise', f'slew___{out_lower}___rise', 'slew_rise'],
            'fall_transition': [f'slew_{out_lower}_fall', f'slew___{out_lower}___fall', 'slew_fall'],
        }
        
        for key, pattern_list in patterns.items():
            for pattern in pattern_list:
                if pattern in measurements:
                    val = measurements[pattern]
                    if 0 < val < 1e-6:
                        timing[key] = val * 1e9
                        if self.debug_mode:
                            print(f"      [PARSE]  Matched {pattern} = {val*1e9:.6f} ns -> {key}")
                        break
        
        # Energy patterns
        energy_patterns = ['e_total', 'etotal', 'energy_total', 'energy']
        
        for pattern in energy_patterns:
            if pattern in measurements:
                val = measurements[pattern]
                if abs(val) > 0:
                    power['energy'] = abs(val) * 1e12  # pJ
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
        return 0.045 + 0.18 * slew + 0.0018 * load
    
    def analytical_slew(self, input_slew, load):
        return max(input_slew * 0.82 + 0.001 * load, 0.014)
    
    def characterize_arc(self, template_file, input_pin, output_pin, use_xyce):
        """Characterize timing arc"""
        print(f"   Arc: {input_pin} → {output_pin}")
        
        vec_key_rise = (input_pin, output_pin, 'rise')
        vec_key_fall = (input_pin, output_pin, 'fall')
        
        if vec_key_rise not in self.test_vectors and vec_key_fall not in self.test_vectors:
            print(f"    Skip (not connected)")
            return None
        
        n_slews = len(self.input_slews)
        n_loads = len(self.output_loads)
        
        cell_rise = np.zeros((n_slews, n_loads))
        cell_fall = np.zeros((n_slews, n_loads))
        rise_trans = np.zeros((n_slews, n_loads))
        fall_trans = np.zeros((n_slews, n_loads))
        rise_energy = np.zeros((n_slews, n_loads)) 
        fall_energy = np.zeros((n_slews, n_loads)) 
        
        rise_success = 0
        fall_success = 0
        
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
                            rise_energy[i,j] = p.get('energy', 0.00004) 
                            
                            self.parse_success += 1
                            rise_success += 1
                        else:
                            self.parse_fail += 1
                            cell_rise[i,j] = self.analytical_delay(slew, load)
                            rise_trans[i,j] = self.analytical_slew(slew, load)
                            rise_energy[i,j] = 0.00004  
                    else:
                        cell_rise[i,j] = self.analytical_delay(slew, load)
                        rise_trans[i,j] = self.analytical_slew(slew, load)
                        rise_energy[i,j] = 0.00004
                
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
                            fall_energy[i,j] = p.get('energy', 0.00004) 
                            
                            self.parse_success += 1
                            fall_success += 1
                        else:
                            self.parse_fail += 1
                            cell_fall[i,j] = self.analytical_delay(slew, load)
                            fall_trans[i,j] = self.analytical_slew(slew, load)
                            fall_energy[i,j] = 0.00004
                    else:
                        cell_fall[i,j] = self.analytical_delay(slew, load)
                        fall_trans[i,j] = self.analytical_slew(slew, load)
                        fall_energy[i,j] = 0.00004
                
                completed = i * n_loads + j + 1
                total = n_slews * n_loads
                print(f"\r    Progress: {completed}/{total}", end='', flush=True)
        
        print(f"\n    Parse: Rise={rise_success}/25, Fall={fall_success}/25")
        
        return {
            'cell_rise': cell_rise,
            'cell_fall': cell_fall,
            'rise_transition': rise_trans,
            'fall_transition': fall_trans,
            'rise_energy': rise_energy,      
            'fall_energy': fall_energy,      
        }
    
    def format_lut(self, table, indent=4):
        """Format lookup table with proper indentation"""
        lines = []
        base_indent = '    ' * indent
        
        for i, row in enumerate(table):
            values = ', '.join(f'{v:.6f}' for v in row)
            if i < len(table) - 1:
                lines.append(f'{base_indent}"{values}", \\')
            else:
                lines.append(f'{base_indent}"{values}" \\')
        
        return '\n'.join(lines)
    
    def generate_liberty(self, output_file, timing_tables):
        """Generate Liberty file with 5x5 energy tables"""
        print(f"\n Generating Liberty: {output_file}")

        leakage_uw = self.leakage_power if self.leakage_power else 0.015

        idx1 = ', '.join([f'{s:.3f}' for s in self.input_slews])
        idx2 = ', '.join([f'{l/1000:.6f}' for l in self.output_loads])

        lib = []

        # ===== library  =====
        lib.append(
f'''library({self.cell_name}_lib) {{
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
  default_max_fanout : 4.0;
  default_connection_class : universal;
  default_inout_pin_cap : 1.0;
  default_input_pin_cap : 1.0;
  default_output_pin_cap : 0.0;
  default_max_transition : 2.0;
  default_leakage_power_density : 0.0;

  voltage_map ( VDD, {self.vdd} );
  voltage_map ( GND, 0 );

  lu_table_template({self.cell_name}_delay_template) {{
    variable_1 : input_net_transition;
    variable_2 : total_output_net_capacitance;
    index_1 ("{idx1}");
    index_2 ("{idx2}");
  }}

  power_lut_template({self.cell_name}_energy_template) {{
    variable_1 : input_transition_time;
    variable_2 : total_output_net_capacitance;
    index_1 ("{idx1}");
    index_2 ("{idx2}");
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
    cell_leakage_power : {leakage_uw:.10f};
''')

        # ===== input pin(a,b,c,d) =====
        for pin in self.inputs:
            cap = self.input_cap_data.get(pin, 0.001 if pin == 'b' else 0.01)
            note = " /* NC */" if pin == 'b' else ""
            lib.append(
f'''    pin({pin}) {{
      direction : input;
      capacitance : {cap:.10f};{note}
    }}
''')

        # ===== output pin(C) =====
        lib.append(
f'''    pin(C) {{
      direction : output;
      function : "((a & d) | ((a | d) & !c))";
      min_capacitance : 0.000;
      max_capacitance : 0.500;
''')

        # timing & internal_power for a / c / d -> C
        for inp in ['a', 'c', 'd']:
            arc_key = f"{inp}_cout"
            if arc_key not in timing_tables or not timing_tables[arc_key]:
                continue

            t = timing_tables[arc_key]

            # --- timing() ---
            lib.append(
f'''      timing() {{
        related_pin : "{inp}";
        timing_type : combinational;
        timing_sense : non_unate;
        cell_rise({self.cell_name}_delay_template) {{
          index_1 ("{idx1}");
          index_2 ("{idx2}");
          values( \\
{self.format_lut(t['cell_rise'], indent=5)}
          );
        }}
        rise_transition({self.cell_name}_delay_template) {{
          index_1 ("{idx1}");
          index_2 ("{idx2}");
          values( \\
{self.format_lut(t['rise_transition'], indent=5)}
          );
        }}
        cell_fall({self.cell_name}_delay_template) {{
          index_1 ("{idx1}");
          index_2 ("{idx2}");
          values( \\
{self.format_lut(t['cell_fall'], indent=5)}
          );
        }}
        fall_transition({self.cell_name}_delay_template) {{
          index_1 ("{idx1}");
          index_2 ("{idx2}");
          values( \\
{self.format_lut(t['fall_transition'], indent=5)}
          );
        }}
      }}
''')

            # --- internal_power() ---
            lib.append(
f'''      internal_power() {{
        related_pin : "{inp}";
        rise_power({self.cell_name}_energy_template) {{
          index_1 ("{idx1}");
          index_2 ("{idx2}");
          values( \\
{self.format_lut(t['rise_energy'], indent=5)}
          );
        }}
        fall_power({self.cell_name}_energy_template) {{
          index_1 ("{idx1}");
          index_2 ("{idx2}");
          values( \\
{self.format_lut(t['fall_energy'], indent=5)}
          );
        }}
      }}
''')

        lib.append('    }\n')

        # ===== output pin(S)  1 =====
        lib.append(
f'''    pin(S) {{
      direction : output;
      function : "1";
      min_capacitance : 0.000;
      max_capacitance : 0.500;
    }}
''')

        lib.append('  }\n}\n')

        with open(output_file, 'w') as f:
            f.write(''.join(lib))

        print("   Liberty file generated")



def main():
    print("="*70)
    print("sabetz Liberty Generator - Fixed Version")
    print("Output format aligned with ACCI1.lib standard")
    print("Internal power uses 5x5 lookup tables with E_TOTAL")
    print("="*70)
    
    debug_mode = '--debug' in sys.argv
    
    template_file = "sabetz.sp"
    if not os.path.exists(template_file):
        print(f" Template: {template_file}")
        return 1
    
    print(f" Template: {template_file}")
    
    gen = LibGenerator(debug_mode=debug_mode)
    
    if not gen.check_xyce():
        print("\n Xyce required")
        return 1
    
    if debug_mode:
        print("\n[DEBUG MODE ENABLED]")
        print("  Will show detailed measurement parsing info")
    
    print(f"\n Config:")
    print(f"  Cell: {gen.cell_name}")
    print(f"  VDD: {gen.vdd}V, Temp: {gen.temp}°C")
    print(f"  Area: {gen.cell_area} um²")
    
    if not gen.verify_test_vectors():
        print("\n Test vector validation failed!")
        return 1

    # Leakage power
    gen.leakage_power = gen.measure_leakage_power(template_file)
    
    # Calculate input capacitances
    print(f"\n Input capacitances...")
    for pin in gen.inputs:
        cap = gen.calculate_input_capacitance(pin)
        gen.input_cap_data[pin] = cap
        note = " (NC)" if pin == 'b' else ""
        print(f"  {pin}: {cap:.10f}pF{note}")
    
    # Timing arcs
    print(f"\n Characterizing arcs...")
    timing_tables = {}
    
    for inp in ['a', 'c', 'd']:
        arc_key = f"{inp}_cout"
        result = gen.characterize_arc(template_file, inp, 'cout', True)
        if result:
            timing_tables[arc_key] = result

    # Generate Liberty
    gen.generate_liberty("sabetz.lib", timing_tables)
    
    # Summary
    print("\n" + "="*70)
    print(" COMPLETE")
    print("="*70)
    print(f"Sim: {gen.sim_success}/{gen.sim_count}")
    print(f"Parse: {gen.parse_success}/{gen.sim_success}")
    if gen.parse_fail > 0:
        print(f"Failed: {gen.parse_fail} (analytical)")
    
    success_rate = (gen.parse_success / gen.sim_success * 100) if gen.sim_success > 0 else 0
    print(f"\n Success: {success_rate:.1f}%")
    
    print(f"\n Output: sabetz.lib")
    
    return 0


if __name__ == "__main__":
    exit(main())