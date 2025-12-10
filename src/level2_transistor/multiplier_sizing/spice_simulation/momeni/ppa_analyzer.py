#!/usr/bin/env python3
"""
PPA Analysis Tool for momeni 4-2 Compressor
Version 1.0
usage: Xyce momeni.sp => python3 ppa_analyzer.py -m momeni.sp.mt0 -n momeni.sp
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
        """Calculate single transistor area (um^2)"""
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
            mosfet_pattern = r'M\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(NMOS_VTL|PMOS_VTL)\s+W=([0-9.]+)[uU]\s+L=([0-9.]+)[uU]'
            
            matches = re.finditer(mosfet_pattern, content, re.MULTILINE | re.IGNORECASE)
            
            for match in matches:
                line_start = content.rfind('\n', 0, match.start()) + 1
                line_end = content.find('\n', match.end())
                full_line = content[line_start:line_end]
                
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


class MomeniPPAAnalyzer:
    """Analyzes PPA metrics from momeni Xyce simulation outputs"""
    
    # Default area values (used when unable to extract from netlist)
    DEFAULT_AREA_METRICS = AreaMetrics(
        total_area=0.6200,  # um^2 (based on typical momeni design)
        nmos_area=0.2478,  # um^2
        pmos_area=0.3723,  # um^2
        transistor_count=30,
        nmos_count=15,
        pmos_count=15,
        calculation_method="default"
    )
    
    def __init__(self, measure_file: str = "momeni.sp.mt0", netlist_file: str = None):
        # Smart detection: if file extensions are wrong, automatically swap
        measure_path = Path(measure_file)
        if netlist_file:
            netlist_path = Path(netlist_file)
            
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
                'design': 'momeni',
                'architecture': '1×OAI22 + 1×INV + 2×AND2 + 1×OR3',
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
            
        self.add_report_line(f" Reading measurements from: {self.measure_file}")
        
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
                        # Filter out -1.0 values (Xyce measurement failures)
                        if value != -1.0:
                            self.measurements[name] = value
            
            if len(self.measurements) == 0:
                self.add_report_line(f"Warning: No measurement data found!")
                self.add_report_line(f"  Please confirm that {self.measure_file} is a valid .mt0 measurement file")
                self.add_report_line(f"  Correct usage: -m <measurement.mt0> -n <netlist.sp>")
                return False
                        
            self.add_report_line(f" Parsed {len(self.measurements)} measurements")
            return True
            
        except Exception as e:
            self.add_report_line(f"Error parsing measurement file: {e}")
            return False
    
    def is_valid(self, key: str) -> bool:
        """Check if measurement exists and is valid"""
        return key in self.measurements and self.measurements[key] > 0
    
    def analyze_performance(self):
        """Extract and analyze performance metrics"""
        self.add_report_line("\n" + "="*80)
        self.add_report_line("1. PERFORMANCE ANALYSIS")
        self.add_report_line("="*80)
        
        perf = self.ppa_report['performance']
        
        self.add_report_line("\n1.1 Output Propagation Delays")
        self.add_report_line("-" * 80)
        
        # S output delays (if any)
        self.add_report_line("  Sum Output (S):")
        s_delays = []
        
        # Check for S output delays
        s_delay_keys = [
            ('TPLH_S', 'S Rise'),
            ('TPHL_S', 'S Fall'),
        ]
        
        for key, label in s_delay_keys:
            if self.is_valid(key):
                val = self.measurements[key] * 1e12  # to ps
                if 0 < val < 1e9:
                    s_delays.append(val)
                    perf[key.lower()] = val
                    self.add_report_line(f"    {label:20s} {val:7.2f} ps")
        
        if not s_delays:
            self.add_report_line("    No S output delays measured")
        
        # COUT delays
        self.add_report_line("\n  Carry Output (COUT):")
        cout_delays = []
        
        # COUT delays relative to B (actual behavior per netlist comments)
        cout_delay_patterns = [
            ('TPLH_B_COUT', 'B→COUT Rise'),
            ('TPHL_B_COUT', 'B→COUT Fall'),
            ('TPLH_C_COUT', 'C→COUT Rise'),
            ('TPHL_C_COUT', 'C→COUT Fall'),
        ]
        
        for key, label in cout_delay_patterns:
            if self.is_valid(key):
                val = self.measurements[key] * 1e12
                if 0 < val < 1e9:
                    cout_delays.append(val)
                    perf[key.lower()] = val
                    self.add_report_line(f"    {label:20s} {val:7.2f} ps")
        
        # Average delays
        self.add_report_line("")
        
        if s_delays:
            avg_s = sum(s_delays) / len(s_delays)
            perf['avg_delay_sum'] = avg_s
            self.add_report_line(f"  Average Sum (S) delay:      {avg_s:7.2f} ps")
            
        if cout_delays:
            avg_cout = sum(cout_delays) / len(cout_delays)
            perf['avg_delay_cout'] = avg_cout
            self.add_report_line(f"  Average Carry (COUT) delay: {avg_cout:7.2f} ps")
        
        # Average propagation delay from measurement
        if self.is_valid('AVG_TP_COUT'):
            avg_tp = self.measurements['AVG_TP_COUT'] * 1e12
            perf['avg_tp_cout'] = avg_tp
            self.add_report_line(f"  Average TP (COUT):          {avg_tp:7.2f} ps")
        
        # Critical path analysis
        self.add_report_line("\n1.2 Critical Path Analysis")
        self.add_report_line("-" * 80)
        
        critical = 0
        critical_output = "Unknown"
        
        if self.is_valid('CRITICAL_PATH'):
            critical = self.measurements['CRITICAL_PATH'] * 1e12
            perf['critical_path_delay'] = critical
            critical_output = "COUT output"
        elif cout_delays:
            critical = max(cout_delays)
            perf['critical_path_delay'] = critical
            critical_output = "COUT output"
        elif s_delays:
            critical = max(s_delays)
            perf['critical_path_delay'] = critical
            critical_output = "S output"
        
        if critical > 0:
            self.add_report_line(f"  Critical path:           {critical_output}")
            self.add_report_line(f"  Critical delay:          {critical:7.2f} ps")
        
        # Rise/Fall times
        self.add_report_line("\n1.3 Transition Times")
        self.add_report_line("-" * 80)
        
        transition_map = [
            ('RISE_TIME_COUT', 'Carry (COUT) rise time'),
            ('FALL_TIME_COUT', 'Carry (COUT) fall time'),
        ]
        
        for key, label in transition_map:
            if self.is_valid(key):
                val = self.measurements[key] * 1e12
                if 0 < val < 1e6:
                    perf[key.lower()] = val
                    self.add_report_line(f"  {label:25s} {val:6.2f} ps")
        
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
        for i in range(1, 8):  # P_DYN_1 to P_DYN_7
            key = f'P_DYN_{i}'
            if self.is_valid(key):
                val = self.measurements[key] * 1e6  # to µW
                if val > 1e-15:
                    dyn_powers.append(val)
                    self.add_report_line(f"  Transition {i}: {val:7.4f} µW")
        
        # Average dynamic power
        p_dyn_avg = 0
        if self.is_valid('P_DYNAMIC_AVG'):
            p_dyn_avg = self.measurements['P_DYNAMIC_AVG'] * 1e6
            power['dynamic_power_avg'] = p_dyn_avg
            self.add_report_line(f"\n  Average dynamic power:   {p_dyn_avg:7.4f} µW")
        elif dyn_powers:
            p_dyn_avg = sum(dyn_powers) / len(dyn_powers)
            power['dynamic_power_avg'] = p_dyn_avg
            self.add_report_line(f"\n  Average dynamic power:   {p_dyn_avg:7.4f} µW")
        
        # Static/Leakage power
        self.add_report_line("\n2.2 Static Power / Leakage")
        self.add_report_line("-" * 80)
        
        leak_powers = []
        for i in range(1, 5):  # P_LEAK_1 to P_LEAK_4
            key = f'P_LEAK_{i}'
            if self.is_valid(key):
                val = self.measurements[key] * 1e9  # to nW
                if val > 0:
                    leak_powers.append(val)
                    self.add_report_line(f"  Period {i}: {val:9.4f} nW")
        
        # Average static power
        p_static_avg = 0
        if self.is_valid('P_STATIC_AVG'):
            p_static_avg = self.measurements['P_STATIC_AVG'] * 1e9
            power['static_power_avg'] = p_static_avg
            self.add_report_line(f"\n  Average static power:    {p_static_avg:9.4f} nW")
        elif leak_powers:
            p_static_avg = sum(leak_powers) / len(leak_powers)
            power['static_power_avg'] = p_static_avg
            self.add_report_line(f"\n  Average static power:    {p_static_avg:9.4f} nW")
        
        # Total power
        self.add_report_line("\n2.3 Total Power and Energy")
        self.add_report_line("-" * 80)
        
        if self.is_valid('P_TOTAL_AVG'):
            p_total = self.measurements['P_TOTAL_AVG'] * 1e6
            power['total_power_avg'] = p_total
            self.add_report_line(f"  Total average power:     {p_total:7.4f} µW")
        elif self.is_valid('P_TOTAL_CALC'):
            p_total = self.measurements['P_TOTAL_CALC'] * 1e6
            power['total_power_avg'] = p_total
            self.add_report_line(f"  Total average power:     {p_total:7.4f} µW")
        
        if self.is_valid('P_PEAK'):
            p_peak = self.measurements['P_PEAK'] * 1e6
            power['peak_power'] = p_peak
            self.add_report_line(f"  Peak power:              {p_peak:9.4f} µW")
        
        # Energy metrics
        if self.is_valid('E_TOTAL'):
            e_total = self.measurements['E_TOTAL'] * 1e15  # to fJ
            power['total_energy'] = e_total
            self.add_report_line(f"  Total energy:            {e_total:8.2f} fJ")
        
        if self.is_valid('E_PER_TRANSITION'):
            e_per_trans = self.measurements['E_PER_TRANSITION'] * 1e15
            power['energy_per_transition'] = e_per_trans
            self.add_report_line(f"  Energy per transition:   {e_per_trans:8.2f} fJ")
        elif self.is_valid('E_TOTAL'):
            # momeni has 7 transitions
            e_per_trans = e_total / 7.0
            power['energy_per_transition'] = e_per_trans
            self.add_report_line(f"  Energy per transition:   {e_per_trans:8.2f} fJ")
        
        # Power breakdown
        self.add_report_line("\n2.4 Power Breakdown")
        self.add_report_line("-" * 80)
        
        if p_dyn_avg > 0 and p_static_avg > 0:
            p_static_uw = p_static_avg / 1000.0
            total = p_dyn_avg + p_static_uw
            if total > 0:
                dyn_percent = (p_dyn_avg / total) * 100
                static_percent = (p_static_uw / total) * 100
                
                self.add_report_line(f"  Dynamic power:           {dyn_percent:5.2f}%")
                self.add_report_line(f"  Static power:            {static_percent:5.2f}%")
        
        self.add_report_line("")
    
    def analyze_area_from_netlist(self, netlist_file: str) -> Optional[AreaMetrics]:
        """Analyze area from netlist file"""
        self.add_report_line(f"\nExtracting transistor information from netlist: {netlist_file}")
        
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
        """Calculate area metrics from transistor sizes"""
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
            self.add_report_line(f"    Instance _3_ (OAI22_X1):  8")
            self.add_report_line(f"    Instance _4_ (INV_X1):    2")
            self.add_report_line(f"    Instance _5_ (AND2_X1):   6")
            self.add_report_line(f"    Instance _6_ (AND2_X1):   6")
            self.add_report_line(f"    Instance _7_ (OR3_X1):    8")
        self.add_report_line(f"  NMOS:                    {area_metrics.nmos_count}")
        self.add_report_line(f"  PMOS:                    {area_metrics.pmos_count}")
        
        # 3.2 Transistor Widths (from netlist)
        if area_metrics.calculation_method == "netlist":
            self.add_report_line("\n3.2 Transistor Widths (from netlist)")
            self.add_report_line("-" * 80)
            
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
        if 'energy_per_transition' in power:
            self.add_report_line(f"  Energy per transition:   {power['energy_per_transition']:8.2f} fJ")
        
        self.add_report_line("\n4.2 Figure of Merit")
        self.add_report_line("-" * 80)
        
        has_fom = False
        
        # PDP (Power-Delay Product) - unit: fJ
        if 'critical_path_delay' in perf and 'total_power_avg' in power:
            delay_ps = perf['critical_path_delay']
            power_uw = power['total_power_avg']
            pdp = power_uw * delay_ps / 1e3  # µW × ps / 1000 = fJ
            self.ppa_report['pdp'] = pdp
            self.add_report_line(f"  PDP (Power×Delay):       {pdp:8.4f} fJ")
            has_fom = True
        
        # EDP (Energy-Delay Product) - unit: fJ·ps
        if 'critical_path_delay' in perf and 'energy_per_transition' in power:
            delay_ps = perf['critical_path_delay']
            energy_fj = power['energy_per_transition']
            edp = energy_fj * delay_ps  # fJ × ps = fJ·ps
            self.ppa_report['edp'] = edp
            self.add_report_line(f"  EDP (Energy×Delay):      {edp:8.2f} fJ·ps")
            has_fom = True
        
        # ADP (Area-Delay Product) - unit: µm²·ps
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
    
    def save_report_txt(self, output_file: str = "momeni_PPA_report.txt"):
        """Save text report"""
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
    
    def save_report_json(self, output_file: str = "momeni_PPA_report.json"):
        """Save JSON report"""
        output_path = Path(output_file)
        
        self.ppa_report['raw_measurements'] = self.measurements
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.ppa_report, f, indent=2)
            print(f"JSON report saved to: {output_path}")
            return True
        except Exception as e:
            print(f"Error saving JSON report: {e}")
            return False
    
    def run_analysis(self):
        """Run complete PPA analysis"""
        self.add_report_line("="*80)
        self.add_report_line(f"MOMENI - PPA ANALYSIS REPORT")
        self.add_report_line("="*80)
        self.add_report_line("")
        self.add_report_line(f"Circuit:           MOMENI")
        self.add_report_line("Technology:        45nm CMOS")
        self.add_report_line("Supply Voltage:    1.2V")
        self.add_report_line("Temperature:       27°C")
        self.add_report_line(f"Architecture:      1×OAI22 + 1×INV + 2×AND2 + 1×OR3")
        self.add_report_line(f"Design:            Approximate 4-2 Compressor")
        self.add_report_line(f"Netlist:           {self.netlist_file if self.netlist_file else 'momeni.sp'}")
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
        description='PPA Analysis Tool - Momeni Approximate 4-2 Compressor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Usage Examples:
  # Use default area values (measurement file only)
  python3 ppa_analyzer_momeni.py -m momeni.sp.mt0
  
  # Extract actual area from netlist (recommended)
  python3 ppa_analyzer_momeni.py -m momeni.sp.mt0 -n momeni.sp
  
  # Specify output filename
  python3 ppa_analyzer_momeni.py -m momeni.sp.mt0 -n momeni.sp -o my_report

Important Notes:
  -m parameter: Specify measurement file (.mt0 file)
  -n parameter: Specify netlist file (.sp file)
  Do not swap -m and -n parameters!
  
  View reports:
    cat momeni_PPA_report.txt
    cat momeni_PPA_report.json | python -m json.tool

Special Notes:
  Momeni design is an approximate 4-2 compressor with simplified logic.
  COUT output actually follows B input instead of C input (see netlist comments).
        '''
    )
    parser.add_argument(
        '-m', '--measure-file',
        default='momeni.sp.mt0',
        help='Xyce measurement output file (.mt0 file, default: momeni.sp.mt0)'
    )
    parser.add_argument(
        '-n', '--netlist',
        help='SPICE netlist file for area extraction (.sp file)'
    )
    parser.add_argument(
        '-o', '--output',
        default='momeni_PPA_report',
        help='Output report base filename (default: momeni_PPA_report)'
    )
    
    args = parser.parse_args()
    
    # Friendly prompt
    print("="*80)
    print("Momeni PPA Analysis Tool")
    print("="*80)
    print(f"Measurement file: {args.measure_file}")
    if args.netlist:
        print(f"Netlist file: {args.netlist}")
    else:
        print("Netlist file: Not specified (will use default area values)")
    print("="*80)
    print()
    
    analyzer = MomeniPPAAnalyzer(args.measure_file, args.netlist)
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