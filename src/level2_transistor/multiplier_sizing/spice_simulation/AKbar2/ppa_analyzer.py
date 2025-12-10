#!/usr/bin/env python3
"""
PPA Analysis Tool for akbar2 4-2 Compressor
Version 1.0
usage: Xyce AKbar2.sp => python3 ppa_analyzer.py -m AKbar2.sp.mt0 -n AKbar2.sp
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TransistorInfo:
    """Transistor information"""
    name: str
    width: float  # in um
    length: float  # in um
    type: str  # NMOS or PMOS
    
    @property
    def area(self) -> float:
        """Calculate the area (um^2) of a single transistor"""
        return self.width * self.length


@dataclass
class AreaMetrics:
    """Area metrics"""
    total_area: float  # um^2
    nmos_area: float  # um^2
    pmos_area: float  # um^2
    transistor_count: int
    nmos_count: int
    pmos_count: int
    calculation_method: str  # "netlist" or "default"


class NetlistParser:
    """SPICE netlist parser"""
    
    def __init__(self, netlist_file: str):
        self.netlist_file = netlist_file
        self.transistors: List[TransistorInfo] = []
        
    def parse(self) -> List[TransistorInfo]:
        """Parse netlist and extract all transistor information"""
        try:
            with open(self.netlist_file, 'r') as f:
                content = f.read()
            
            # Match MOSFET definition lines
            # Format: M<n> <drain> <gate> <source> <bulk> <model> W=<width> L=<length>
            mosfet_pattern = r'M\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(NMOS_VTL|PMOS_VTL)\s+W=([0-9.]+)u\s+L=([0-9.]+)u'
            
            matches = re.finditer(mosfet_pattern, content, re.MULTILINE | re.IGNORECASE)
            
            for match in matches:
                # Get complete transistor definition line
                line_start = content.rfind('\n', 0, match.start()) + 1
                line_end = content.find('\n', match.end())
                full_line = content[line_start:line_end]
                
                # Extract transistor name
                name_match = re.match(r'(M\S+)\s+', full_line)
                if name_match:
                    name = name_match.group(1)
                else:
                    name = "Unknown"
                
                model_type = match.group(1)
                width = float(match.group(2))
                length = float(match.group(3))
                
                trans_type = "NMOS" if "NMOS" in model_type else "PMOS"
                
                transistor = TransistorInfo(
                    name=name,
                    width=width,
                    length=length,
                    type=trans_type
                )
                self.transistors.append(transistor)
            
            return self.transistors
            
        except FileNotFoundError:
            print(f"Error: Netlist file '{self.netlist_file}' not found")
            return []
        except Exception as e:
            print(f"Error parsing netlist: {e}")
            return []
    
    def calculate_area_from_netlist(self) -> Optional[AreaMetrics]:
        """Calculate area from parsed transistor list"""
        if not self.transistors:
            return None
        
        total_area = 0.0
        nmos_area = 0.0
        pmos_area = 0.0
        nmos_count = 0
        pmos_count = 0
        
        for trans in self.transistors:
            area = trans.area
            total_area += area
            
            if trans.type == "NMOS":
                nmos_area += area
                nmos_count += 1
            else:
                pmos_area += area
                pmos_count += 1
        
        return AreaMetrics(
            total_area=total_area,
            nmos_area=nmos_area,
            pmos_area=pmos_area,
            transistor_count=len(self.transistors),
            nmos_count=nmos_count,
            pmos_count=pmos_count,
            calculation_method="netlist"
        )


class PPAAnalyzerAkbar2:
    """Analyzes PPA metrics from Xyce simulation outputs for akbar2"""
    
    # Default area values (used when extraction from netlist fails)
    DEFAULT_AREA_METRICS = AreaMetrics(
        total_area=0.7015,  # um^2 (based on typical akbar2 design)
        nmos_area=0.2795,  # um^2
        pmos_area=0.4220,  # um^2
        transistor_count=34,
        nmos_count=17,
        pmos_count=17,
        calculation_method="default"
    )
    
    def __init__(self, measure_file: str = "AKbar2.sp.mt0", netlist_file: str = None):
        measure_path = Path(measure_file)
        if netlist_file:
            netlist_path = Path(netlist_file)
            
            # If measure_file looks like netlist and netlist_file looks like measurement, swap them
            if (measure_path.suffix == '.sp' or '.sp' in str(measure_path)) and \
               (netlist_path.suffix == '.mt0' or '.mt0' in str(netlist_path)):
                print(f"Warning: Parameters may be swapped")
                print(f"  -m parameter: {measure_file} (looks like netlist)")
                print(f"  -n parameter: {netlist_file} (looks like measurement)")
                print(f"  Auto-swapping parameters...")
                measure_file, netlist_file = netlist_file, measure_file
                measure_path = Path(measure_file)
        
        self.measure_file = measure_path
        self.netlist_file = netlist_file
        self.measurements = {}
        self.area_metrics: Optional[AreaMetrics] = None
        self.ppa_report = {
            'performance': {},
            'power': {},
            'area': {},
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'measure_file': str(measure_file),
                'netlist_file': str(netlist_file) if netlist_file else None,
                'design': 'akbar2',
                'architecture': '2×XNOR2 + 1×NAND2 + 1×AOI22 + 1×INV',
            }
        }
        self.report_lines = []
        
    def add_report_line(self, line: str = ""):
        """Add a line to text report"""
        self.report_lines.append(line)
        print(line)
        
    def parse_measurements(self) -> bool:
        """Parse Xyce .mt0 measurement file"""
        if not self.measure_file.exists():
            self.add_report_line(f"Error: Measurement file not found: {self.measure_file}")
            return False
            
        self.add_report_line(f"✓ Reading measurements from: {self.measure_file}")
        
        try:
            with open(self.measure_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('*') or line.startswith('#'):
                        continue
                    
                    match = re.match(r'(\w+)\s*=\s*([-+]?[\d.]+(?:[eE][-+]?\d+)?)', line)
                    if match:
                        name = match.group(1)
                        value = float(match.group(2))
                        self.measurements[name] = value
                        
            if len(self.measurements) == 0:
                self.add_report_line(f"Warning: No measurement data found!")
                self.add_report_line(f"  Please confirm that {self.measure_file} is a valid .mt0 measurement file")
                self.add_report_line(f"  Correct usage: -m <measurement.mt0> -n <netlist.sp>")
                return False
            
            self.add_report_line(f"✓ Parsed {len(self.measurements)} measurements")
            return True
            
        except Exception as e:
            self.add_report_line(f"Error parsing measurement file: {e}")
            return False
    
    def analyze_performance(self):
        """Extract and analyze performance metrics for akbar2"""
        self.add_report_line("\n" + "="*80)
        self.add_report_line("1. PERFORMANCE ANALYSIS")
        self.add_report_line("="*80)
        
        perf = self.ppa_report['performance']
        
        self.add_report_line("\n1.1 Output Propagation Delays")
        self.add_report_line("-" * 80)
        
        delays_s = []
        delays_cout = []
        
        # S output delay patterns
        delay_patterns_s = [
            ('TPLH_D_S_P1', 'D→S (P1)', 'Rise'),
            ('TPHL_C_S_P2', 'C→S (P2)', 'Fall'),
            ('TPLH_B_S_P3', 'B→S (P3)', 'Rise'),
            ('TPHL_A_S_P4', 'A→S (P4)', 'Fall'),
            ('TPLH_D_S_P5', 'D→S (P5)', 'Rise'),
        ]
        
        self.add_report_line("  Sum Output (S):")
        for key, label, edge in delay_patterns_s:
            if key in self.measurements:
                val = self.measurements[key] * 1e12
                # Filter out failed measurements (extremely large or zero values)
                if 0 < val < 1e9:  # Valid range: 0 to 1ms
                    delays_s.append(val)
                    self.add_report_line(f"    {label:12s} {edge:4s}: {val:7.2f} ps")
        
        # cout output delays
        self.add_report_line("\n  Carry Output (Cout):")
        
        delay_patterns_cout = [
            ('TPLH_C_cout_P2', 'C→cout (P2)', 'Rise'),
        ]
        
        for key, label, edge in delay_patterns_cout:
            if key in self.measurements:
                val = self.measurements[key] * 1e12
                if 0 < val < 1e9:
                    delays_cout.append(val)
                    self.add_report_line(f"    {label:12s} {edge:4s}: {val:7.2f} ps")
        
        # Average delays
        self.add_report_line("")
        
        if 'AVG_DELAY_S' in self.measurements:
            avg_s = self.measurements['AVG_DELAY_S'] * 1e12
            if 0 < avg_s < 1e9:
                perf['avg_delay_sum'] = avg_s
                self.add_report_line(f"  Average Sum (S) delay:      {avg_s:7.2f} ps")
        elif delays_s:
            avg_s = sum(delays_s) / len(delays_s)
            perf['avg_delay_sum'] = avg_s
            self.add_report_line(f"  Average Sum (S) delay:      {avg_s:7.2f} ps")
            
        if 'AVG_DELAY_cout' in self.measurements:
            avg_cout = self.measurements['AVG_DELAY_cout'] * 1e12
            if 0 < avg_cout < 1e9:
                perf['avg_delay_carry'] = avg_cout
                self.add_report_line(f"  Average Carry (cout) delay: {avg_cout:7.2f} ps")
        elif delays_cout:
            avg_cout = sum(delays_cout) / len(delays_cout)
            perf['avg_delay_carry'] = avg_cout
            self.add_report_line(f"  Average Carry (cout) delay: {avg_cout:7.2f} ps")
        
        # Critical path analysis
        self.add_report_line("\n1.2 Critical Path Analysis")
        self.add_report_line("-" * 80)
        
        if delays_s or delays_cout:
            all_delays = delays_s + delays_cout
            critical = max(all_delays)
            perf['critical_path_delay'] = critical
            
            # Determine which is the critical path
            if critical in delays_s:
                critical_output = "S output"
            else:
                critical_output = "Cout output"
            
            self.add_report_line(f"  Critical path:           {critical_output}")
            self.add_report_line(f"  Critical delay:          {critical:7.2f} ps")
        
        # Rise/Fall times
        self.add_report_line("\n1.3 Transition Times")
        self.add_report_line("-" * 80)
        
        if 'RISE_TIME_S' in self.measurements:
            rise_s = self.measurements['RISE_TIME_S'] * 1e12
            if 0 < rise_s < 1e6:
                perf['rise_time_sum'] = rise_s
                self.add_report_line(f"  Sum (S) rise time:       {rise_s:7.2f} ps")
        
        if 'FALL_TIME_S' in self.measurements:
            fall_s = self.measurements['FALL_TIME_S'] * 1e12
            if 0 < fall_s < 1e6:
                perf['fall_time_sum'] = fall_s
                self.add_report_line(f"  Sum (S) fall time:       {fall_s:7.2f} ps")
            
        if 'RISE_TIME_cout' in self.measurements:
            rise_cout = self.measurements['RISE_TIME_cout'] * 1e12
            if 0 < rise_cout < 1e6:
                perf['rise_time_carry'] = rise_cout
                self.add_report_line(f"  Carry (cout) rise time:  {rise_cout:7.2f} ps")
        
        self.add_report_line("")
    
    def analyze_power(self):
        """Extract and analyze power metrics"""
        self.add_report_line("="*80)
        self.add_report_line("2. POWER ANALYSIS")
        self.add_report_line("="*80)
        
        power = self.ppa_report['power']
        
        # Dynamic power
        self.add_report_line("\n2.1 Dynamic Power")
        self.add_report_line("-" * 80)
        
        dyn_powers = []
        for pattern in [1, 2, 3, 4, 5]:
            key = f'P_DYN{pattern}'
            if key in self.measurements:
                val = self.measurements[key]
                # Filter out failed measurements (negative or near-zero anomalous values)
                if val > 1e-15:  # At least greater than 1fW
                    val_uw = val * 1e6
                    dyn_powers.append(val_uw)
                    self.add_report_line(f"  Pattern {pattern}: {val_uw:8.4f} µW")
        
        # Use P_DYNAMIC_AVG as average dynamic power
        p_dyn_avg = 0
        if 'P_DYNAMIC_AVG' in self.measurements and self.measurements['P_DYNAMIC_AVG'] > 0:
            p_dyn_avg = self.measurements['P_DYNAMIC_AVG'] * 1e6
            power['dynamic_power_avg'] = p_dyn_avg
            self.add_report_line(f"\n  Average dynamic power:   {p_dyn_avg:8.4f} µW")
        elif dyn_powers:
            p_dyn_avg = sum(dyn_powers) / len(dyn_powers)
            power['dynamic_power_avg'] = p_dyn_avg
            self.add_report_line(f"\n  Average dynamic power:   {p_dyn_avg:8.4f} µW")
        
        # Static/Leakage power
        self.add_report_line("\n2.2 Static Power / Leakage")
        self.add_report_line("-" * 80)
        
        leak_powers = []
        for period in [1, 2, 3]:
            key = f'P_LEAK{period}'
            if key in self.measurements:
                val = self.measurements[key]
                # Filter out failed measurements
                if val > 0:
                    val_nw = val * 1e9
                    leak_powers.append(val_nw)
                    self.add_report_line(f"  Period {period}: {val_nw:8.4f} nW")
        
        # Calculate average static power
        p_static_avg = 0
        if 'P_STATIC_AVG' in self.measurements and self.measurements['P_STATIC_AVG'] > 0:
            p_static_avg = self.measurements['P_STATIC_AVG'] * 1e9
            power['static_power_avg'] = p_static_avg
            self.add_report_line(f"\n  Average static power:    {p_static_avg:8.4f} nW")
        elif leak_powers:
            p_static_avg = sum(leak_powers) / len(leak_powers)
            power['static_power_avg'] = p_static_avg
            self.add_report_line(f"\n  Average static power:    {p_static_avg:8.4f} nW")
        
        # Total power
        self.add_report_line("\n2.3 Total Power and Energy")
        self.add_report_line("-" * 80)
        
        if 'P_AVG' in self.measurements:
            p_total = self.measurements['P_AVG'] * 1e6
            power['total_power_avg'] = p_total
            self.add_report_line(f"  Total average power:     {p_total:8.4f} µW")
        
        if 'P_PEAK' in self.measurements:
            p_peak = self.measurements['P_PEAK'] * 1e6
            power['peak_power'] = p_peak
            self.add_report_line(f"  Peak power:              {p_peak:8.4f} µW")
        
        # Energy metrics
        if 'E_TOTAL' in self.measurements:
            e_total = self.measurements['E_TOTAL'] * 1e15
            power['total_energy'] = e_total
            self.add_report_line(f"  Total energy:            {e_total:8.2f} fJ")
            
            # Calculate energy per operation (5 major transitions)
            e_per_op = e_total / 5.0
            power['energy_per_op'] = e_per_op
            self.add_report_line(f"  Energy per operation:    {e_per_op:8.2f} fJ")
        
        # Power breakdown
        self.add_report_line("\n2.4 Power Breakdown")
        self.add_report_line("-" * 80)
        
        if p_dyn_avg > 0 and p_static_avg > 0:
            p_static_uw = p_static_avg / 1000.0
            total_components = p_dyn_avg + p_static_uw
            if total_components > 0:
                dyn_percent = (p_dyn_avg / total_components) * 100
                static_percent = (p_static_uw / total_components) * 100
                
                self.add_report_line(f"  Dynamic power:           {dyn_percent:5.2f}%")
                self.add_report_line(f"  Static power:            {static_percent:5.2f}%")
                
                # If P_AVG differs significantly from component sum, add note
                if 'P_AVG' in self.measurements:
                    p_total = self.measurements['P_AVG'] * 1e6
                    diff_percent = abs(p_total - total_components) / p_total * 100 if p_total > 0 else 0
                    if diff_percent > 5.0:
                        self.add_report_line(f"  Note: P_DYNAMIC_AVG ({p_dyn_avg:.4f} µW) measured during active transitions")
                        self.add_report_line(f"        Components differ from P_AVG by {diff_percent:.1f}%")
        
        self.add_report_line("")
    
    def analyze_area_from_netlist(self, netlist_file: str) -> Optional[AreaMetrics]:
        """Analyze area from netlist file"""
        self.add_report_line(f"\nExtracting transistor information from netlist: {netlist_file}")
        
        # Check if file exists
        if not Path(netlist_file).exists():
            self.add_report_line(f"Error: Netlist file not found: {netlist_file}")
            self.add_report_line("  Using default area values")
            return None
        
        parser = NetlistParser(netlist_file)
        transistors = parser.parse()
        
        if not transistors:
            self.add_report_line("Warning: Unable to extract transistor information from netlist")
            self.add_report_line(f"  Please confirm that {netlist_file} is a valid .sp SPICE netlist file")
            self.add_report_line("  Correct usage: -m <measurement.mt0> -n <netlist.sp>")
            return None
        
        self.add_report_line(f"Successfully extracted {len(transistors)} transistors")
        
        # Display detailed information
        self.add_report_line("\nTransistor Details:")
        self.add_report_line(f"{'Name':<20} {'Type':<10} {'Width(um)':<12} {'Length(um)':<12} {'Area(um²)':<12}")
        self.add_report_line("-" * 70)
        
        for trans in transistors:
            self.add_report_line(f"{trans.name:<20} {trans.type:<10} {trans.width:<12.3f} "
                  f"{trans.length:<12.3f} {trans.area:<12.6f}")
        
        area_metrics = parser.calculate_area_from_netlist()
        return area_metrics
    
    def get_default_area(self) -> AreaMetrics:
        """Get default area values"""
        self.add_report_line("\nUsing default area values")
        return self.DEFAULT_AREA_METRICS
    
    def analyze_area(self):
        """Calculate area metrics from transistor sizes for akbar2"""
        self.add_report_line("\n" + "="*80)
        self.add_report_line("3. AREA ANALYSIS")
        self.add_report_line("="*80)
        
        area_dict = self.ppa_report['area']
        
        # Try to extract from netlist or use default values
        if self.netlist_file:
            area_metrics = self.analyze_area_from_netlist(self.netlist_file)
            if area_metrics is None:
                area_metrics = self.get_default_area()
        else:
            area_metrics = self.get_default_area()
        
        self.area_metrics = area_metrics
        
        # 3.1 Transistor Count
        self.add_report_line("\n3.1 Transistor Count")
        self.add_report_line("-" * 80)
        self.add_report_line(f"  Total Transistors:       {area_metrics.transistor_count}")
        if area_metrics.calculation_method == "default":
            self.add_report_line(f"    2×XNOR2_X1: 20 (10 each)")
            self.add_report_line(f"    1×NAND2_X1: 4")
            self.add_report_line(f"    1×AOI22_X1: 8")
            self.add_report_line(f"    1×INV_X1:   2")
        self.add_report_line(f"  NMOS:                    {area_metrics.nmos_count}")
        self.add_report_line(f"  PMOS:                    {area_metrics.pmos_count}")
        
        # 3.2 Transistor Widths (from netlist) - only show when extracted from netlist
        if area_metrics.calculation_method == "netlist":
            self.add_report_line("\n3.2 Transistor Widths (from netlist)")
            self.add_report_line("-" * 80)
            
            # Calculate total width (assuming length is 50nm)
            gate_length = 0.050  # um
            nmos_width = area_metrics.nmos_area / gate_length
            pmos_width = area_metrics.pmos_area / gate_length
            
            self.add_report_line(f"  NMOS total width:        {nmos_width:.3f} µm")
            self.add_report_line(f"  PMOS total width:        {pmos_width:.3f} µm")
            self.add_report_line(f"  Total Width:             {nmos_width + pmos_width:.3f} µm")
            self.add_report_line(f"  Gate Length:             {gate_length:.3f} µm (50nm)")
        
        # 3.3 Area Estimation
        self.add_report_line("\n3.3 Area Estimation")
        self.add_report_line("-" * 80)
        self.add_report_line(f"  Raw transistor area:     {area_metrics.total_area:.4f} µm²")
        self.add_report_line(f"    NMOS area:             {area_metrics.nmos_area:.4f} µm²")
        self.add_report_line(f"    PMOS area:             {area_metrics.pmos_area:.4f} µm²")
        
        self.add_report_line(f"\n  With layout overhead:")
        
        layout_factors = [5, 7, 10]
        for factor in layout_factors:
            estimated = area_metrics.total_area * factor
            marker = " (typical)" if factor == 7 else ""
            self.add_report_line(f"    {factor:2d}× overhead:          {estimated:7.4f} µm²{marker}")
        
        # Save to dictionary
        area_dict['transistor_count'] = area_metrics.transistor_count
        area_dict['nmos_count'] = area_metrics.nmos_count
        area_dict['pmos_count'] = area_metrics.pmos_count
        area_dict['total_width_um'] = (area_metrics.nmos_area + area_metrics.pmos_area) / 0.050
        area_dict['raw_area_um2'] = area_metrics.total_area
        area_dict['estimated_area_um2'] = area_metrics.total_area * 7
        area_dict['calculation_method'] = area_metrics.calculation_method
        
        self.add_report_line("")
    
    def generate_summary(self):
        """Generate summary metrics and PPA scores"""
        self.add_report_line("="*80)
        self.add_report_line("4. PPA SUMMARY")
        self.add_report_line("="*80)
        
        perf = self.ppa_report['performance']
        power = self.ppa_report['power']
        area = self.ppa_report['area']
        
        self.add_report_line("\n4.1 Key Metrics")
        self.add_report_line("-" * 80)
        
        if 'critical_path_delay' in perf:
            self.add_report_line(f"  Performance (delay):     {perf['critical_path_delay']:8.2f} ps (critical path)")
        if 'total_power_avg' in power:
            self.add_report_line(f"  Power (average):         {power['total_power_avg']:8.4f} µW")
        if 'estimated_area_um2' in area:
            self.add_report_line(f"  Area (with 7× overhead): {area['estimated_area_um2']:8.4f} µm²")
        if 'energy_per_op' in power:
            self.add_report_line(f"  Energy per operation:    {power['energy_per_op']:8.2f} fJ")
        
        self.add_report_line("\n4.2 Figure of Merit")
        self.add_report_line("-" * 80)
        
        has_fom = False
        
        # PDP (Power-Delay Product) - unit: fJ
        # Power(µW) × Delay(ps) = 1e-6 W × 1e-12 s = 1e-18 J = fJ
        if 'critical_path_delay' in perf and 'total_power_avg' in power:
            delay_ps = perf['critical_path_delay']
            power_uw = power['total_power_avg']
            pdp = power_uw * delay_ps / 1e3  # µW × ps / 1000 = fJ
            self.ppa_report['pdp'] = pdp
            self.add_report_line(f"  PDP (Power×Delay):       {pdp:8.4f} fJ")
            has_fom = True
        
        # EDP (Energy-Delay Product) - unit: fJ·ps
        # Energy(fJ) × Delay(ps) = fJ·ps
        if 'critical_path_delay' in perf and 'energy_per_op' in power:
            delay_ps = perf['critical_path_delay']
            energy_fj = power['energy_per_op']
            edp = energy_fj * delay_ps  # fJ × ps = fJ·ps
            self.ppa_report['edp'] = edp
            self.add_report_line(f"  EDP (Energy×Delay):      {edp:8.2f} fJ·ps")
            has_fom = True
        
        # ADP (Area-Delay Product) - unit: µm²·ps
        # Area(µm²) × Delay(ps) = µm²·ps
        if 'estimated_area_um2' in area and 'critical_path_delay' in perf:
            area_um2 = area['estimated_area_um2']
            delay_ps = perf['critical_path_delay']
            adp = area_um2 * delay_ps
            self.ppa_report['adp'] = adp
            self.add_report_line(f"  ADP (Area×Delay):        {adp:8.2f} µm²·ps")
            has_fom = True
        
        # Design characteristics
        self.add_report_line("\n4.3 Design Characteristics")
        self.add_report_line("-" * 80)
        
        if 'dynamic_power_avg' in power and 'static_power_avg' in power:
            p_dyn = power['dynamic_power_avg']
            p_static_uw = power['static_power_avg'] / 1000.0
            total = p_dyn + p_static_uw
            if total > 0:
                dyn_pct = (p_dyn / total) * 100
                static_pct = (p_static_uw / total) * 100
                self.add_report_line(f"  Power efficiency:        {dyn_pct:.1f}% dynamic, {static_pct:.1f}% static")
        
        if 'critical_path_delay' in perf:
            delay_ps = perf['critical_path_delay']
            if delay_ps < 1000:
                speed_grade = "Fast (sub-nanosecond)"
            elif delay_ps < 2000:
                speed_grade = "Medium (1-2 ns)"
            else:
                speed_grade = "Slow (>2 ns)"
            self.add_report_line(f"  Speed grade:             {speed_grade}")
        
        if 'transistor_count' in area:
            self.add_report_line(f"  Area efficiency:         Compact ({area['transistor_count']} transistors)")
        
        self.add_report_line("")
    
    def save_report_txt(self, output_file: str = "AKbar2_PPA_report.txt"):
        """Save PPA report to TXT file"""
        output_path = Path(output_file)
        
        # Add end marker
        end_lines = [
            "="*80,
            "END OF REPORT",
            "="*80
        ]
        self.report_lines.extend(end_lines)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.report_lines))
            print(f"\nReport saved to: {output_path}")
            return True
        except Exception as e:
            print(f"\nError saving report: {e}")
            return False
    
    def save_report_json(self, output_file: str = "akbar2_PPA_report.json"):
        """Save PPA report to JSON file"""
        output_path = Path(output_file)
        
        self.ppa_report['raw_measurements'] = self.measurements
        
        try:
            with open(output_path, 'w') as f:
                json.dump(self.ppa_report, f, indent=2)
            print(f"JSON report saved to: {output_path}")
            return True
        except Exception as e:
            print(f"Error saving JSON report: {e}")
            return False
    
    def run_analysis(self):
        """Run complete PPA analysis"""
        self.add_report_line("="*80)
        self.add_report_line(f"AKBAR2 - PPA ANALYSIS REPORT")
        self.add_report_line("="*80)
        self.add_report_line("")
        self.add_report_line(f"Circuit:           AKBAR2")
        self.add_report_line("Technology:        45nm CMOS")
        self.add_report_line("Supply Voltage:    1.2V")
        self.add_report_line("Temperature:       27°C")
        self.add_report_line(f"Architecture:      2×XNOR2 + 1×NAND2 + 1×AOI22 + 1×INV")
        self.add_report_line(f"Netlist:           {self.netlist_file if self.netlist_file else 'akbar2.sp'}")
        self.add_report_line(f"Measurements:      {self.measure_file.name}")
        
        if not self.parse_measurements():
            return False
        
        self.analyze_performance()
        self.analyze_power()
        self.analyze_area()
        self.generate_summary()
        
        self.save_report_txt()
        self.save_report_json()
        
        return True


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='PPA Analysis Tool - AKbar2 4-2 Compressor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Usage Examples:
  # Use default area values (measurement file only)
  python ppa_analyzer_akbar2.py -m AKbar2.sp.mt0
  
  # Extract actual area from netlist (recommended)
  python ppa_analyzer_akbar2.py -m AKbar2.sp.mt0 -n AKbar2.sp
  
  # Specify output filename
  python ppa_analyzer_akbar2.py -m AKbar2.sp.mt0 -n AKbar2.sp -o my_report
  
Important Notes:
  -m parameter: Specify measurement file (.mt0 file)
  -n parameter: Specify netlist file (.sp file)
  
  View reports:
    cat AKbar2_PPA_report.txt
    cat AKbar2_PPA_report.json | python -m json.tool
        '''
    )
    parser.add_argument(
        '-m', '--measure-file',
        default='AKbar2.sp.mt0',
        help='Xyce measurement output file (.mt0 file, default: AKbar2.sp.mt0)'
    )
    parser.add_argument(
        '-n', '--netlist',
        help='SPICE netlist file for area extraction (.sp file)'
    )
    parser.add_argument(
        '-o', '--output',
        default='AKbar2_PPA_report',
        help='Output report base filename (default: AKbar2_PPA_report)'
    )
    

    args = parser.parse_args()
    
    # Friendly prompt
    print("="*80)
    print("AKbar2 PPA Analysis Tool")
    print("="*80)
    print(f"Measurement file: {args.measure_file}")
    if args.netlist:
        print(f"Netlist file: {args.netlist}")
    else:
        print("Netlist file: Not specified (will use default area values)")
    print("="*80)
    print()
    
    analyzer = PPAAnalyzerAkbar2(args.measure_file, args.netlist)
    success = analyzer.run_analysis()
    
    if not success:
        print("\nAnalysis failed!")
        print("Please check:")
        print("  1. File paths are correct")
        print("  2. -m parameter specifies a .mt0 file")
        print("  3. -n parameter specifies a .sp file")
        sys.exit(1)
    
    print("\nAnalysis completed successfully!")
    sys.exit(0)


if __name__ == '__main__':
    main()