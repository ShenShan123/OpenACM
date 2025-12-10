#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PPA Analyzer
usage: python3 run_ppa.py
input: width vector
output: [delay, power, area]
"""

import re
import subprocess
import shutil
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import defaultdict


class TransistorModifier:
    """Transistor width modifier"""

    def __init__(self, modifications):
        self.modifications = modifications

    def should_modify(self, cell_type, transistor_type, original_width):
        """Check if specific width type transistors need modification"""
        if cell_type not in self.modifications:
            return False, None
            
        # Find matching width type
        width_key = f"{transistor_type}_{original_width}"
        if width_key in self.modifications[cell_type]:
            return True, self.modifications[cell_type][width_key]
            
        return False, None

    def modify_width(self, line, new_width):
        """Modify transistor width"""
        # Match W=number.u format, keep unit unchanged (note lowercase u)
        return re.sub(r'W=\d+\.\d+u', f'W={new_width}u', line)


class InstanceTracker:
    """Flattened instance tracker"""

    def __init__(self):
        self.instances = defaultdict(list)
        self.cell_order = []
        self.cell_transistor_types = defaultdict(set)

    def add_instance(self, instance_name, cell_type):
        self.instances[cell_type].append(instance_name)
        if cell_type not in self.cell_order:
            self.cell_order.append(cell_type)

    def add_transistor_type(self, cell_type, transistor_type, width):
        """Record transistor types and widths appearing in cell"""
        width_key = f"{transistor_type}_{width}"
        self.cell_transistor_types[cell_type].add(width_key)

    def get_ordered_cell_types(self):
        return self.cell_order

    def get_cell_transistor_info(self, cell_type):
        """Get transistor type information for cell"""
        return sorted(list(self.cell_transistor_types[cell_type]))


class CircuitState:
    """Circuit state"""

    def __init__(self):
        self.current_instance = None
        self.current_cell_type = None

    def parse_flattened_comment(self, line):
        """
        Parse flattened instance comments
        """
        # Format 1: * Flattened instance: _06_ (NAND2_X1)
        match1 = re.match(r'^\*\s*Flattened\s+instance:\s+(\S+)\s+\(([^)]+)\)', line, re.IGNORECASE)
        if match1:
            return match1.group(1), match1.group(2)
        
        # Format 2: * Instance _2_ (XNOR2_X1): computes ...
        match2 = re.match(r'^\*\s*Instance\s+(\S+)\s+\(([^)]+)\)', line, re.IGNORECASE)
        if match2:
            return match2.group(1), match2.group(2)
        
        return None, None

    def is_transistor_line(self, line):
        """Improved transistor line detection"""
        line_stripped = line.strip()
        if not line_stripped.startswith('M'):
            return False
            
        # Check if contains transistor key information
        has_w = 'W=' in line_stripped
        has_l = 'L=' in line_stripped
        has_nmos = 'NMOS' in line_stripped.upper()
        has_pmos = 'PMOS' in line_stripped.upper()
        
        return has_w and has_l and (has_nmos or has_pmos)

    def extract_transistor_width(self, line):
        """Extract transistor width"""
        # Match W=number.u format (note lowercase u)
        match = re.search(r'W=(\d+\.\d+)u', line)
        if match:
            return float(match.group(1))
        return None

    def belongs_to_current_instance(self, transistor_line, current_instance):
        """Check if transistor belongs to current instance"""
        if not current_instance:
            return False
            
        trans_name = transistor_line.split()[0]
        
        # Support multiple naming formats, including Full Adder format
        patterns = [
            f"M_{current_instance}_",      # M_06_M_i_1
            f"M_{current_instance}__",     # M_06__M_i_1
            f"M__{current_instance}__",    # M__06__M_i_1 (first 3 instances use this format)
            f"M_FA_{current_instance}_",   # M_FA_3_M_i_1 (Full Adder single underscore)
            f"M_FA__{current_instance}__", # M_FA__3__M_i_1 (Full Adder double underscore)
        ]
        
        for pattern in patterns:
            if pattern in trans_name:
                return True
                
        return False


class NetlistProcessor:
    """Netlist processor"""

    def __init__(self, netlist_file, modifier, tracker):
        self.netlist_file = Path(netlist_file)
        self.modifier = modifier
        self.tracker = tracker
        self.state = CircuitState()
        self.lines = []
        self.is_flattened = False

    def read_netlist(self):
        with open(self.netlist_file, 'r', encoding='utf-8') as f:
            self.lines = f.readlines()

    def detect_includes(self):
        for line in self.lines:
            if line.strip().upper().startswith('.INCLUDE'):
                match = re.search(r'\.INCLUDE\s+["\']?([^"\']+)["\']?', line, re.IGNORECASE)
                if match:
                    include_file = match.group(1).strip()
                    if 'stdcells' in include_file.lower():
                        self.is_flattened = True

    def analyze_flattened_instances(self, verbose=False):
        """Analyze flattened instances and record transistor types"""
        current_instance = None
        current_cell_type = None
        transistor_count = 0
        
        for line_num, line in enumerate(self.lines):
            line_stripped = line.strip()
            if not line_stripped:
                continue
                
            # Check if it's an instance comment
            instance_name, cell_type = self.state.parse_flattened_comment(line_stripped)
            if instance_name and cell_type:
                if verbose and current_instance:
                    print(f"     Instance {current_instance} found {transistor_count} transistors in total")
                
                current_instance = instance_name
                current_cell_type = cell_type
                transistor_count = 0
                self.tracker.add_instance(instance_name, cell_type)
                if verbose:
                    print(f"   Found instance: {instance_name} -> {cell_type}")
                continue
                
            # Check if it's a transistor line
            if current_instance and current_cell_type and self.state.is_transistor_line(line_stripped):
                belongs = self.state.belongs_to_current_instance(line_stripped, current_instance)
                if belongs:
                    transistor_type = self._get_transistor_type(line_stripped)
                    width = self.state.extract_transistor_width(line_stripped)
                    if transistor_type and width is not None:
                        self.tracker.add_transistor_type(current_cell_type, transistor_type, width)
                        transistor_count += 1
                        if verbose:
                            trans_name = line_stripped.split()[0]
                            print(f"     Recorded transistor: {trans_name} -> {transistor_type}_{width}")
                    elif verbose:
                        print(f"     Warning: Unable to extract transistor type or width: {line_stripped[:80]}")
                elif verbose:
                    trans_name = line_stripped.split()[0]
                    print(f"     Skipped (doesn't belong to current instance): {trans_name}")
        
        # Print statistics for last instance
        if verbose and current_instance:
            print(f"     Instance {current_instance} found {transistor_count} transistors in total")

    def process_modifications(self):
        """Process modifications - support multi-width transistors"""
        modified_lines = []
        current_instance = None
        current_cell_type = None
        
        for line in self.lines:
            original_line = line
            line_stripped = line.strip()
            
            if not line_stripped:
                modified_lines.append(original_line)
                continue
                
            # Check if it's an instance comment
            instance_name, cell_type = self.state.parse_flattened_comment(line_stripped)
            if instance_name and cell_type:
                current_instance = instance_name
                current_cell_type = cell_type
                modified_lines.append(original_line)
                continue
                
            # Check if it's a transistor line
            if self.state.is_transistor_line(line_stripped):
                if current_instance and current_cell_type:
                    # Check if belongs to current instance
                    if self.state.belongs_to_current_instance(line_stripped, current_instance):
                        transistor_type = self._get_transistor_type(line_stripped)
                        original_width = self.state.extract_transistor_width(line_stripped)
                        
                        if transistor_type and original_width is not None:
                            should_modify, new_width = self.modifier.should_modify(
                                current_cell_type, transistor_type, original_width
                            )
                            if should_modify:
                                modified_line = self.modifier.modify_width(original_line, new_width)
                                modified_lines.append(modified_line)
                                continue
                
                # If not modifying, keep as is
                modified_lines.append(original_line)
            else:
                modified_lines.append(original_line)
                
        self.lines = modified_lines

    def _get_transistor_type(self, line):
        line_upper = line.upper()
        if 'NMOS' in line_upper:
            return 'nmos'
        elif 'PMOS' in line_upper:
            return 'pmos'
        return None

    def remove_stdcells_includes(self):
        if not self.is_flattened:
            return
        cleaned_lines = []
        for line in self.lines:
            if line.strip().upper().startswith('.INCLUDE'):
                match = re.search(r'\.INCLUDE\s+["\']?([^"\']+)["\']?', line, re.IGNORECASE)
                if match:
                    include_file = match.group(1).strip()
                    if 'stdcells' in include_file.lower():
                        continue
            cleaned_lines.append(line)
        self.lines = cleaned_lines

    def write_netlist(self, output_file):
        output_path = Path(output_file)
        temp_file = output_path.with_suffix('.sp.tmp')
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.writelines(self.lines)
            if output_path.exists():
                backup_file = output_path.with_suffix('.sp.bak')
                shutil.copy2(output_path, backup_file)
            shutil.move(str(temp_file), str(output_path))
            return True
        except Exception as e:
            print(f"Failed to write netlist: {e}")
            if temp_file.exists():
                temp_file.unlink()
            return False


def find_files_in_directory(directory):
    """Find .sp netlist file and ppa_analyzer.py in directory"""
    dir_path = Path(directory)
    if not dir_path.exists():
        raise FileNotFoundError(f"Directory does not exist: {directory}")
    sp_files = list(dir_path.glob('*.sp'))
    if not sp_files:
        raise FileNotFoundError(f".sp file not found: {directory}")
    netlist_file = sp_files[0]
    ppa_script = dir_path / 'ppa_analyzer.py'
    if not ppa_script.exists():
        raise FileNotFoundError(f"ppa_analyzer.py not found: {directory}")
    return netlist_file, ppa_script


def run_xyce(netlist_filename, work_dir):
    """Run Xyce simulation"""
    try:
        result = subprocess.run(
            ['Xyce', netlist_filename],
            cwd=work_dir,
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode != 0:
            print(f"Xyce simulation failed, return code: {result.returncode}")
            print(f"Error output: {result.stderr}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("Xyce simulation timeout")
        return False
    except Exception as e:
        print(f"Xyce execution error: {e}")
        return False


def run_ppa_analysis(ppa_script_name, netlist_stem, work_dir, verbose=False):
    """Run PPA analysis"""
    try:
        measure_file = f"{netlist_stem}.sp.mt0"
        netlist_file = f"{netlist_stem}.sp"
        output_file = f"{netlist_stem}_PPA_report.txt"
        
        result = subprocess.run(
            ['python3', ppa_script_name, 
             '--netlist', netlist_file, 
             '--m', measure_file,
             '--output', output_file],
            cwd=work_dir,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if verbose:
            if result.returncode != 0:
                print(f"   PPA analysis failed, return code: {result.returncode}")
                if result.stdout:
                    print(f"   Standard output:\n{result.stdout[:500]}")
                if result.stderr:
                    print(f"   Error output:\n{result.stderr[:500]}")
            else:
                print(f"   PPA analysis completed successfully")
        
        return result.returncode == 0
    except Exception as e:
        if verbose:
            print(f"  PPA analysis execution error: {e}")
        return False


def extract_ppa_metrics(ppa_report_file):
    """Extract delay, power, area values from PPA TXT report"""
    try:
        with open(ppa_report_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        
        # Enhanced matching patterns
        patterns = [
            # Format1: Performance (delay): 1.234e-09
            (r'Performance\s*\(?\s*delay\s*\)?\s*:?\s*([\d.eE+-]+)', 
             r'Power\s*\(?\s*average\s*\)?\s*:?\s*([\d.eE+-]+)', 
             r'Area\s*\(?\s*with\s+7[×x]\s+overhead\s*\)?\s*:?\s*([\d.eE+-]+)'),
            
            # Format2: Delay: 1.234e-09
            (r'Delay\s*:?\s*([\d.eE+-]+)',
             r'Power\s*:?\s*([\d.eE+-]+)',
             r'Area\s*:?\s*([\d.eE+-]+)'),
        ]
        
        for delay_pattern, power_pattern, area_pattern in patterns:
            try:
                delay_match = re.search(delay_pattern, content, re.IGNORECASE)
                power_match = re.search(power_pattern, content, re.IGNORECASE)
                area_match = re.search(area_pattern, content, re.IGNORECASE)
                
                if delay_match and power_match and area_match:
                    delay = float(delay_match.group(1).replace(' ', ''))
                    power = float(power_match.group(1).replace(' ', ''))
                    area = float(area_match.group(1).replace(' ', ''))
                    return np.array([delay, power, area])
            except (ValueError, IndexError) as e:
                continue
        
        print("No matching PPA metric format found")
        return None
    except Exception as e:
        print(f"PPA metric extraction error: {e}")
        return None


def analyze_cell_transistor_requirements(tracker, verbose=False):
    """Analyze transistor width modification quantities required for each cell"""
    cell_requirements = {}
    total_requirements = 0
    
    for cell_type in tracker.get_ordered_cell_types():
        transistor_types = tracker.get_cell_transistor_info(cell_type)
        cell_requirements[cell_type] = {
            'count': len(transistor_types),
            'types': transistor_types
        }
        total_requirements += len(transistor_types)
        
        if verbose:
            print(f"   {cell_type}: {len(transistor_types)} transistor types")
            for trans_type in transistor_types:
                print(f"     - {trans_type}")
    
    return cell_requirements, total_requirements


def vector_to_modifications(width_vector, cell_requirements, cell_types):
    """Convert width vector to modification dictionary - support multi-width transistors"""
    modifications = {}
    vector_index = 0
    
    for cell_type in cell_types:
        requirements = cell_requirements[cell_type]
        cell_modifications = {}
        
        for trans_type in requirements['types']:
            if vector_index >= len(width_vector):
                raise ValueError(f"Width vector length insufficient: needs {sum(req['count'] for req in cell_requirements.values())} values, but only has {len(width_vector)}")
            
            cell_modifications[trans_type] = f"{width_vector[vector_index]:.6f}"
            vector_index += 1
        
        modifications[cell_type] = cell_modifications
    
    if vector_index != len(width_vector):
        raise ValueError(f"Width vector length mismatch: used {vector_index} values, but vector has {len(width_vector)} values")
    
    return modifications



def run_ppa_vector(circuit_dir, width_vector, verbose=False):
    """
    Vectorized PPA analysis function - support multi-width transistors
    
    Args:
        circuit_dir: Circuit directory path
        width_vector: Width vector, dimension determined by actual transistor types
        verbose: Whether to print detailed information
        
    Returns:
        numpy array: [delay, power, area] or None (if failed)
    """
    try:
        if verbose:
            print(f"Step 1: Finding files...")
        
        # Find files
        try:
            netlist_file, ppa_script = find_files_in_directory(circuit_dir)
            if verbose:
                print(f"   Netlist file: {netlist_file}")
                print(f"   PPA script: {ppa_script}")
        except Exception as e:
            if verbose:
                print(f"   File search failed: {e}")
            return None
        
        if verbose:
            print(f"\nStep 2: Analyzing netlist structure...")
        
        # Analyze netlist structure
        try:
            modifier = TransistorModifier({})
            tracker = InstanceTracker()
            processor = NetlistProcessor(netlist_file, modifier, tracker)
            processor.read_netlist()
            processor.detect_includes()
            processor.analyze_flattened_instances(verbose=verbose)  # Pass verbose parameter
            cell_types = tracker.get_ordered_cell_types()
            
            # Analyze transistor requirements
            cell_requirements, total_requirements = analyze_cell_transistor_requirements(tracker, verbose=verbose)
            
            if verbose:
                print(f"   Detected {len(cell_types)} cell types")
                print(f"   Total transistor types: {total_requirements}")
                print(f"   Netlist lines: {len(processor.lines)}")
                
            # If no transistor types detected, try manual analysis
            if total_requirements == 0:
                if verbose:
                    print(f"   Warning: No transistor types detected, attempting manual analysis...")
                
        except Exception as e:
            if verbose:
                print(f"   Netlist analysis failed: {e}")
                import traceback
                traceback.print_exc()
            return None
        
        if verbose:
            print(f"\nStep 3: Verifying vector dimension...")
        
        # Verify vector dimension
        expected_length = total_requirements
        actual_length = len(width_vector)
        if verbose:
            print(f"  Expected length: {expected_length} (total transistor types)")
            print(f"  Actual length: {actual_length}")
        
        if actual_length != expected_length:
            if verbose:
                print(f"   Dimension mismatch!")
                print(f"     Need: {expected_length} width values")
                print(f"     Provided: {actual_length} width values")
            return None
        else:
            if verbose:
                print(f"   Dimension match")
        
        if verbose:
            print(f"\nStep 4: Converting vector to modification instructions...")
        
        # Convert vector to modification dictionary
        try:
            modifications = vector_to_modifications(width_vector, cell_requirements, cell_types)
            if verbose:
                print(f"   Modification instructions:")
                for cell_type, trans_dict in modifications.items():
                    print(f"    {cell_type}:")
                    for trans_type, width in trans_dict.items():
                        print(f"        {trans_type}: {width}u")
        except Exception as e:
            if verbose:
                print(f"   Vector conversion failed: {e}")
            return None
        
        if verbose:
            print(f"\nStep 5: Creating output directory...")
        
        # Create output directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        output_dir = Path('ppa_results') / f"{netlist_file.stem}_{timestamp}"
        output_dir.mkdir(parents=True, exist_ok=True)
        if verbose:
            print(f"   Output directory: {output_dir}")
        
        if verbose:
            print(f"\nStep 6: Modifying netlist...")
        
        # Re-process netlist
        try:
            modifier = TransistorModifier(modifications)
            tracker = InstanceTracker()
            processor = NetlistProcessor(netlist_file, modifier, tracker)
            processor.read_netlist()
            processor.detect_includes()
            processor.analyze_flattened_instances()
            processor.process_modifications()
            processor.remove_stdcells_includes()
            if verbose:
                print(f"   Netlist modification complete")
        except Exception as e:
            if verbose:
                print(f"   Netlist modification failed: {e}")
            return None
        
        if verbose:
            print(f"\nStep 7: Writing netlist...")
        
        # Write netlist
        output_netlist = output_dir / netlist_file.name
        if not processor.write_netlist(output_netlist):
            if verbose:
                print(f"   Netlist write failed")
            return None
        if verbose:
            print(f"   Netlist written: {output_netlist}")
        
        if verbose:
            print(f"\nStep 8: Copying PPA script...")
        
        # Copy PPA script
        output_ppa_script = output_dir / ppa_script.name
        shutil.copy2(ppa_script, output_ppa_script)
        if verbose:
            print(f"   PPA script copied")
        
        if verbose:
            print(f"\nStep 9: Running Xyce simulation...")
        
        # Run Xyce
        if not run_xyce(netlist_file.name, output_dir):
            if verbose:
                print(f"   Xyce simulation failed")
            return None
        if verbose:
            print(f"   Xyce simulation complete")
        
        if verbose:
            print(f"\nStep 10: Running PPA analysis...")
        
        # Run PPA analysis
        if not run_ppa_analysis(ppa_script.name, netlist_file.stem, output_dir, verbose):
            if verbose:
                print(f"   PPA analysis failed")
            return None
        if verbose:
            print(f"   PPA analysis complete")
        
        if verbose:
            print(f"\nStep 11: Extracting PPA metrics...")
        
        # Extract PPA metrics
        ppa_report_file = output_dir / f"{netlist_file.stem}_PPA_report.txt"
        
        if not ppa_report_file.exists():
            if verbose:
                print(f"   PPA report file does not exist: {ppa_report_file}")
            return None
            
        result = extract_ppa_metrics(ppa_report_file)
        
        if result is None:
            if verbose:
                print(f"   PPA metric extraction failed")
        else:
            if verbose:
                print(f"   PPA metrics:")
                print(f"    Delay: {result[0]:.6e} ps")
                print(f"    Power: {result[1]:.6e} μW")
                print(f"    Area:  {result[2]:.6e} μm²")

        if verbose:
            print(f"\nStep 12: Cleaning temporary files...")
        
        # Clean temporary directory
        try:
            shutil.rmtree(output_dir)
            if verbose:
                print(f"   Temporary files cleaned")
        except:
            if verbose:
                print(f"   Cleanup failed, directory preserved at: {output_dir}")
        
        return result
        
    except Exception as e:
        if verbose:
            print(f"\nException: {e}")
            import traceback
            traceback.print_exc()
        return None


def main():
    """Main function"""
    # Configuration parameters
    circuit_dir = 'sabetz'
    
    widths = [0.370, 0.190, 0.145, 0.145]
    
    # Run PPA analysis (can enable verbose output for debugging)
    output = run_ppa_vector(circuit_dir, widths, verbose=True)
    
    # Only output result
    if output is not None:
        print(' '.join([f'{x:.6e}' for x in output]))
    else:
        print("nan nan nan")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nnan nan nan", flush=True)
    except Exception as e:
        print(f"nan nan nan (error: {e})", flush=True)