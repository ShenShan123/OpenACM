#!/usr/bin/env python3
"""
PPA Analysis Tool for AKbar1 4-2 Compressor
Version 1.0
usage: Xyce AKbar1.sp => python3 ppa_analyzer.py -m AKbar1.sp.mt0 -n AKbar1.sp
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


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


@dataclass
class PowerMetrics:
    """Power metrics"""
    avg_power: float  # W
    peak_power: float  # W
    static_power: float  # W
    dynamic_power: float  # W
    total_energy: float  # J


@dataclass
class PerformanceMetrics:
    """Performance metrics"""
    avg_delay_s: float  # ns
    avg_delay_cout: float  # ns
    avg_delay_s_rise: float  # ns
    avg_delay_s_fall: float  # ns
    rise_time_s: float  # ns
    rise_time_cout: float  # ns
    fall_time_s: float = 0.0  # ns 
    fall_time_cout: float = 0.0  # ns 


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
    
    def calculate_area_from_netlist(self) -> AreaMetrics:
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


class PPAAnalyzer:
    """PPA Analyzer"""
    
    # Default area values (used when extraction from netlist fails)
    DEFAULT_AREA_METRICS = {
        'akbar1': AreaMetrics(
            total_area=0.850,  # um^2 (assumed value)
            nmos_area=0.400,
            pmos_area=0.450,
            transistor_count=24,
            nmos_count=12,
            pmos_count=12,
            calculation_method="default"
        ),
    }
    
    def __init__(self, design_name: str = "akbar1"):
        self.design_name = design_name
        self.area_metrics: Optional[AreaMetrics] = None
        self.power_metrics: Optional[PowerMetrics] = None
        self.performance_metrics: Optional[PerformanceMetrics] = None
    
    def analyze_area_from_netlist(self, netlist_file: str) -> AreaMetrics:
        """Analyze area from netlist file"""
        print(f"\nExtracting transistor information from netlist: {netlist_file}")
        
        parser = NetlistParser(netlist_file)
        transistors = parser.parse()
        
        if not transistors:
            print("Warning: Unable to extract transistor information from netlist, using default area values")
            return self.get_default_area()
        
        print(f"Successfully extracted {len(transistors)} transistors")
        
        # Display detailed information
        print("\nTransistor Details:")
        print(f"{'Name':<20} {'Type':<10} {'Width(um)':<12} {'Length(um)':<12} {'Area(um²)':<12}")
        print("-" * 70)
        
        for trans in transistors:
            print(f"{trans.name:<20} {trans.type:<10} {trans.width:<12.3f} "
                  f"{trans.length:<12.3f} {trans.area:<12.6f}")
        
        area_metrics = parser.calculate_area_from_netlist()
        self.area_metrics = area_metrics
        
        return area_metrics
    
    def get_default_area(self) -> AreaMetrics:
        """Get default area values"""
        if self.design_name in self.DEFAULT_AREA_METRICS:
            area = self.DEFAULT_AREA_METRICS[self.design_name]
            self.area_metrics = area
            return area
        else:
            # If no default value exists for this design, return a generic default
            print(f"Warning: Design '{self.design_name}' has no default area values")
            area = AreaMetrics(
                total_area=1.0,
                nmos_area=0.5,
                pmos_area=0.5,
                transistor_count=20,
                nmos_count=10,
                pmos_count=10,
                calculation_method="default"
            )
            self.area_metrics = area
            return area
    
    def parse_measurement_file(self, meas_file: str) -> Tuple[Optional[PowerMetrics], Optional[PerformanceMetrics]]:
        """Parse SPICE simulation output .mt0 file"""
        try:
            with open(meas_file, 'r') as f:
                content = f.read()
            
            # Helper function to extract measurement values
            def extract_value(pattern: str) -> Optional[float]:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    value_str = match.group(1).strip()
                    # Handle scientific notation
                    try:
                        return float(value_str)
                    except ValueError:
                        return None
                return None
            
            # Extract power data
            p_avg = extract_value(r'P_AVG\s*=\s*([0-9.eE+-]+)')
            p_peak = extract_value(r'P_PEAK\s*=\s*([0-9.eE+-]+)')
            p_static = extract_value(r'P_STATIC\s*=\s*([0-9.eE+-]+)')
            p_dynamic = extract_value(r'P_DYNAMIC_AVG\s*=\s*([0-9.eE+-]+)')
            e_total = extract_value(r'E_TOTAL\s*=\s*([0-9.eE+-]+)')
            
            power_metrics = None
            if p_avg is not None:
                power_metrics = PowerMetrics(
                    avg_power=p_avg,
                    peak_power=p_peak or 0.0,
                    static_power=p_static or 0.0,
                    dynamic_power=p_dynamic or 0.0,
                    total_energy=e_total or 0.0
                )
            
            # Extract performance data
            avg_delay_s = extract_value(r'AVG_DELAY_S\s*=\s*([0-9.eE+-]+)')
            avg_delay_cout = extract_value(r'AVG_DELAY_COUT\s*=\s*([0-9.eE+-]+)')
            avg_delay_s_rise = extract_value(r'AVG_DELAY_S_RISE\s*=\s*([0-9.eE+-]+)')
            avg_delay_s_fall = extract_value(r'AVG_DELAY_S_FALL\s*=\s*([0-9.eE+-]+)')
            rise_time_s = extract_value(r'RISE_TIME_S\s*=\s*([0-9.eE+-]+)')
            rise_time_cout = extract_value(r'RISE_TIME_COUT\s*=\s*([0-9.eE+-]+)')
            fall_time_s = extract_value(r'FALL_TIME_S\s*=\s*([0-9.eE+-]+)')
            fall_time_cout = extract_value(r'FALL_TIME_COUT\s*=\s*([0-9.eE+-]+)')
            
            performance_metrics = None
            if avg_delay_s is not None:
                performance_metrics = PerformanceMetrics(
                    avg_delay_s=avg_delay_s * 1e9,  # Convert to ns
                    avg_delay_cout=avg_delay_cout * 1e9 if avg_delay_cout else 0.0,
                    avg_delay_s_rise=avg_delay_s_rise * 1e9 if avg_delay_s_rise else 0.0,
                    avg_delay_s_fall=avg_delay_s_fall * 1e9 if avg_delay_s_fall else 0.0,
                    rise_time_s=rise_time_s * 1e9 if rise_time_s else 0.0,
                    rise_time_cout=rise_time_cout * 1e9 if rise_time_cout else 0.0,
                    fall_time_s=fall_time_s * 1e9 if fall_time_s else 0.0,
                    fall_time_cout=fall_time_cout * 1e9 if fall_time_cout else 0.0
                )
            
            self.power_metrics = power_metrics
            self.performance_metrics = performance_metrics
            
            return power_metrics, performance_metrics
            
        except FileNotFoundError:
            print(f"Warning: Measurement file '{meas_file}' not found")
            return None, None
        except Exception as e:
            print(f"Error parsing measurement file: {e}")
            return None, None
    
    def generate_report(self, output_file: str = None):
        """Generate PPA analysis report"""
        report_lines = []
        
        # Title
        report_lines.append("=" * 80)
        report_lines.append(f"{self.design_name.upper()}  - PPA ANALYSIS REPORT")
        report_lines.append("=" * 80)
        report_lines.append("")
        report_lines.append(f"Circuit:           {self.design_name.upper()}")
        report_lines.append("Technology:        45nm CMOS")
        report_lines.append("Supply Voltage:    1.2V")
        report_lines.append("Temperature:       27°C")
        report_lines.append(f"Netlist:           {self.design_name}.sp")
        report_lines.append(f"Measurements:      {self.design_name}.sp.mt0")
        report_lines.append("")
        
        # ========== 1. PERFORMANCE ANALYSIS ==========
        report_lines.append("=" * 80)
        report_lines.append("1. PERFORMANCE ANALYSIS")
        report_lines.append("=" * 80)
        report_lines.append("")
        
        # 1.1 Output Propagation Delays
        report_lines.append("1.1 Output Propagation Delays")
        report_lines.append("-" * 80)
        if self.performance_metrics:
            perf = self.performance_metrics
            # Convert to ps
            avg_delay_s_ps = perf.avg_delay_s * 1000
            avg_delay_cout_ps = perf.avg_delay_cout * 1000
            avg_delay_s_rise_ps = perf.avg_delay_s_rise * 1000
            avg_delay_s_fall_ps = perf.avg_delay_s_fall * 1000
            
            report_lines.append("  Sum Output (S):")
            report_lines.append(f"    Average delay:         {avg_delay_s_ps:.2f} ps")
            if avg_delay_s_rise_ps > 0:
                report_lines.append(f"    Rise delay avg:        {avg_delay_s_rise_ps:.2f} ps")
            if avg_delay_s_fall_ps > 0:
                report_lines.append(f"    Fall delay avg:        {avg_delay_s_fall_ps:.2f} ps")
            report_lines.append("")
            if avg_delay_cout_ps > 0:
                report_lines.append("  Carry Output (Cout):")
                report_lines.append(f"    Average delay:         {avg_delay_cout_ps:.2f} ps")
        report_lines.append("")
        
        # 1.2 Critical Path Analysis
        report_lines.append("1.2 Critical Path Analysis")
        report_lines.append("-" * 80)
        if self.performance_metrics:
            perf = self.performance_metrics
            avg_delay_s_ps = perf.avg_delay_s * 1000
            avg_delay_cout_ps = perf.avg_delay_cout * 1000
            
            # Determine critical path (considering rise and fall)
            critical_delay_ps = avg_delay_s_ps
            critical_path = "S output"
            
            if perf.avg_delay_s_rise > 0 and perf.avg_delay_s_fall > 0:
                max_s_delay = max(perf.avg_delay_s_rise, perf.avg_delay_s_fall) * 1000
                critical_delay_ps = max_s_delay
            
            if avg_delay_cout_ps > critical_delay_ps:
                critical_delay_ps = avg_delay_cout_ps
                critical_path = "Cout output"
            
            report_lines.append(f"  Critical path:           {critical_path}")
            report_lines.append(f"  Critical delay:          {critical_delay_ps:.2f} ps")
        report_lines.append("")
        
        # 1.3 Transition Times
        report_lines.append("1.3 Transition Times")
        report_lines.append("-" * 80)
        if self.performance_metrics:
            perf = self.performance_metrics
            if perf.rise_time_s > 0:
                rise_s_ps = perf.rise_time_s * 1000
                report_lines.append(f"  Sum (S) rise time:       {rise_s_ps:.2f} ps")
            if perf.fall_time_s > 0:
                fall_s_ps = perf.fall_time_s * 1000
                report_lines.append(f"  Sum (S) fall time:       {fall_s_ps:.2f} ps")
            if perf.rise_time_cout > 0:
                rise_cout_ps = perf.rise_time_cout * 1000
                report_lines.append(f"  Carry (Cout) rise time:  {rise_cout_ps:.2f} ps")
            if perf.fall_time_cout > 0:
                fall_cout_ps = perf.fall_time_cout * 1000
                report_lines.append(f"  Carry (Cout) fall time:  {fall_cout_ps:.2f} ps")
        report_lines.append("")
        
        # ========== 2. POWER ANALYSIS ==========
        report_lines.append("=" * 80)
        report_lines.append("2. POWER ANALYSIS")
        report_lines.append("=" * 80)
        report_lines.append("")
        
        # 2.1 Dynamic Power
        report_lines.append("2.1 Dynamic Power")
        report_lines.append("-" * 80)
        if self.power_metrics:
            power = self.power_metrics
            report_lines.append(f"  Average dynamic power:   {power.dynamic_power*1e6:.3f} μW")
        report_lines.append("")
        
        # 2.2 Static Power / Leakage
        report_lines.append("2.2 Static Power / Leakage")
        report_lines.append("-" * 80)
        if self.power_metrics:
            power = self.power_metrics
            report_lines.append(f"  Average static power:    {power.static_power*1e9:.3f} nW")
        report_lines.append("")
        
        # 2.3 Total Power and Energy
        report_lines.append("2.3 Total Power and Energy")
        report_lines.append("-" * 80)
        if self.power_metrics:
            power = self.power_metrics
            energy_per_op = power.total_energy / 6 if power.total_energy > 0 else 0  # Assume 6 operations
            report_lines.append(f"  Total average power:     {power.avg_power*1e6:.3f} μW")
            if power.peak_power > 0:
                report_lines.append(f"  Peak power:              {power.peak_power*1e3:.3f} mW")
            report_lines.append(f"  Total energy:            {power.total_energy*1e15:.3f} fJ")
            report_lines.append(f"  Energy per operation:    {energy_per_op*1e15:.3f} fJ")
        report_lines.append("")
        
        # 2.4 Power Breakdown
        report_lines.append("2.4 Power Breakdown")
        report_lines.append("-" * 80)
        if self.power_metrics:
            power = self.power_metrics
            # Calculate actual dynamic power percentage (based on total power)
            actual_dynamic = power.avg_power - power.static_power
            if power.avg_power > 0:
                dynamic_pct = (actual_dynamic / power.avg_power) * 100
                static_pct = (power.static_power / power.avg_power) * 100
                report_lines.append(f"  Dynamic power:           {dynamic_pct:.2f}%")
                report_lines.append(f"  Static power:            {static_pct:.2f}%")
                # Add additional information note
                if power.dynamic_power > power.avg_power * 1.5:
                    report_lines.append(f"  Note: P_DYNAMIC_AVG ({power.dynamic_power*1e6:.3f} μW) > P_AVG")
                    report_lines.append(f"        (measured during active transitions)")
        report_lines.append("")
        
        # ========== 3. AREA ANALYSIS ==========
        report_lines.append("=" * 80)
        report_lines.append("3. AREA ANALYSIS")
        report_lines.append("=" * 80)
        report_lines.append("")
        
        # 3.1 Transistor Count
        report_lines.append("3.1 Transistor Count")
        report_lines.append("-" * 80)
        if self.area_metrics:
            area = self.area_metrics
            report_lines.append(f"  Total Transistors:       {area.transistor_count}")
            report_lines.append(f"  NMOS:                    {area.nmos_count}")
            report_lines.append(f"  PMOS:                    {area.pmos_count}")
        report_lines.append("")
        
        # 3.2 Transistor Widths (from netlist)
        if self.area_metrics and self.area_metrics.calculation_method == "netlist":
            report_lines.append("3.2 Transistor Widths (from netlist)")
            report_lines.append("-" * 80)
            area = self.area_metrics
            # Calculate total width (assuming length is 50nm)
            nmos_width = area.nmos_area / 0.05
            pmos_width = area.pmos_area / 0.05
            report_lines.append(f"  NMOS total width:        {nmos_width:.3f} μm")
            report_lines.append(f"  PMOS total width:        {pmos_width:.3f} μm")
            report_lines.append(f"  Gate Length:             0.050 μm (50nm)")
            report_lines.append("")
        
        # 3.3 Area Estimation
        report_lines.append("3.3 Area Estimation")
        report_lines.append("-" * 80)
        if self.area_metrics:
            area = self.area_metrics
            report_lines.append(f"  Raw transistor area:     {area.total_area:.4f} μm²")
            report_lines.append(f"    NMOS area:             {area.nmos_area:.4f} μm²")
            report_lines.append(f"    PMOS area:             {area.pmos_area:.4f} μm²")
            report_lines.append("")
            report_lines.append("  With layout overhead:")
            report_lines.append(f"     5× overhead:          {area.total_area*5:.4f} μm²")
            report_lines.append(f"     7× overhead:          {area.total_area*7:.4f} μm² (typical)")
            report_lines.append(f"    10× overhead:          {area.total_area*10:.4f} μm²")
        report_lines.append("")
        
        # ========== 4. PPA SUMMARY ==========
        report_lines.append("=" * 80)
        report_lines.append("4. PPA SUMMARY")
        report_lines.append("=" * 80)
        report_lines.append("")
        
        # 4.1 Key Metrics
        report_lines.append("4.1 Key Metrics")
        report_lines.append("-" * 80)
        
        if self.performance_metrics:
            perf = self.performance_metrics
            # Use critical path delay
            critical_delay_ns = perf.avg_delay_s
            if perf.avg_delay_s_rise > 0 and perf.avg_delay_s_fall > 0:
                critical_delay_ns = max(perf.avg_delay_s_rise, perf.avg_delay_s_fall)
            if perf.avg_delay_cout > critical_delay_ns:
                critical_delay_ns = perf.avg_delay_cout
            
            perf_val = f"{critical_delay_ns * 1000:.2f} ps (critical path)"
            report_lines.append(f"  Performance (delay):     {perf_val}")
        
        if self.power_metrics:
            power = self.power_metrics
            power_val = f"{power.avg_power*1e6:.3f} μW"
            energy_val = f"{(power.total_energy/6)*1e15:.3f} fJ"
            report_lines.append(f"  Power (average):         {power_val}")
        
        if self.area_metrics:
            area = self.area_metrics
            area_val = f"{area.total_area*7:.4f} μm²"
            report_lines.append(f"  Area (with 7× overhead): {area_val}")
        
        if self.power_metrics:
            report_lines.append(f"  Energy per operation:    {energy_val}")
        
        report_lines.append("")
        
        # 4.2 Figure of Merit
        report_lines.append("4.2 Figure of Merit")
        report_lines.append("-" * 80)
        if self.area_metrics and self.power_metrics and self.performance_metrics:
            area = self.area_metrics
            power = self.power_metrics
            perf = self.performance_metrics
            
            # Use critical path delay
            critical_delay_ns = perf.avg_delay_s
            if perf.avg_delay_s_rise > 0 and perf.avg_delay_s_fall > 0:
                critical_delay_ns = max(perf.avg_delay_s_rise, perf.avg_delay_s_fall)
            if perf.avg_delay_cout > critical_delay_ns:
                critical_delay_ns = perf.avg_delay_cout
            
            # PDP (Power-Delay Product) - unit: fJ
            # Power(W) × Delay(ns) = W·ns = J·1e-9 = fJ·1e6
            pdp = power.avg_power * critical_delay_ns * 1e6  # W × ns → fJ
            
            # EDP (Energy-Delay Product) - unit: fJ·ps
            # Energy_per_op(J) × Delay(ns) = J·ns = J·1e-9·s = fJ·1e6·ps·1e-3 = fJ·ps·1e3
            energy_per_op = power.total_energy / 6  # J
            edp = energy_per_op * critical_delay_ns * 1e18  # J × ns → fJ·ps
            
            # ADP (Area-Delay Product) - unit: μm²·ps
            area_7x = area.total_area * 7  # μm²
            adp = area_7x * (critical_delay_ns * 1e3)  # μm² × ps
            
            report_lines.append(f"  PDP (Power×Delay):       {pdp:.3f} fJ")
            report_lines.append(f"  EDP (Energy×Delay):      {edp:.3f} fJ·ps")
            report_lines.append(f"  ADP (Area×Delay):        {adp:.2f} μm²·ps")
        report_lines.append("")
        
        # 4.3 Design Characteristics
        report_lines.append("4.3 Design Characteristics")
        report_lines.append("-" * 80)
        if self.power_metrics and self.power_metrics.avg_power > 0:
            power = self.power_metrics
            # Use actual dynamic power (P_AVG - P_STATIC)
            actual_dynamic = power.avg_power - power.static_power
            dynamic_pct = (actual_dynamic / power.avg_power) * 100
            static_pct = (power.static_power / power.avg_power) * 100
            report_lines.append(f"  Power efficiency:        {dynamic_pct:.1f}% dynamic, {static_pct:.1f}% static")
        
        if self.performance_metrics:
            perf = self.performance_metrics
            critical_delay_ns = perf.avg_delay_s
            if perf.avg_delay_s_rise > 0 and perf.avg_delay_s_fall > 0:
                critical_delay_ns = max(perf.avg_delay_s_rise, perf.avg_delay_s_fall)
            if perf.avg_delay_cout > critical_delay_ns:
                critical_delay_ns = perf.avg_delay_cout
            
            delay_ps = critical_delay_ns * 1000
            if delay_ps < 1000:
                speed_grade = "Fast (sub-nanosecond)"
            elif delay_ps < 2000:
                speed_grade = "Medium (1-2 ns)"
            else:
                speed_grade = "Slow (>2 ns)"
            report_lines.append(f"  Speed grade:             {speed_grade}")
        
        if self.area_metrics:
            report_lines.append(f"  Area efficiency:         Compact ({self.area_metrics.transistor_count} transistors)")
        report_lines.append("")
        
        # End
        report_lines.append("=" * 80)
        report_lines.append("END OF REPORT")
        report_lines.append("=" * 80)
        
        # Output report
        report_text = "\n".join(report_lines)
        print(report_text)
        
        # Save to file
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report_text)
                print(f"\nReport saved to: {output_file}")
            except Exception as e:
                print(f"Error saving report: {e}")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='PPA Analysis Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Usage Examples:
  # Use default area values
  python ppa_analyzer.py --design akbar1 --meas akbar1.mt0
  
  # Extract actual area from netlist
  python ppa_analyzer.py --design akbar1 --netlist akbar1.sp --meas akbar1.mt0
  
  # Analyze area only (from netlist)
  python ppa_analyzer.py --design akbar1 --netlist akbar1.sp --area-only
  
  # Save report to file
  python ppa_analyzer.py --design akbar1 --netlist akbar1.sp --meas akbar1.mt0 --output akbar1_PPA_report.txt
        '''
    )
    
    parser.add_argument('--design', default='akbar1', 
                        help='Design name (default: akbar1)')
    parser.add_argument('--netlist', '-n', 
                        help='SPICE netlist file path (.sp file)')
    parser.add_argument('--meas', '-m', 
                        help='SPICE measurement result file path (.mt0 file)')
    parser.add_argument('--output', '-o', 
                        help='Output report file path')
    parser.add_argument('--area-only', action='store_true',
                        help='Analyze area only (no simulation results needed)')
    
    args = parser.parse_args()
    
    # Create analyzer
    analyzer = PPAAnalyzer(design_name=args.design)
    
    # Area analysis
    if args.netlist:
        # Extract from netlist
        analyzer.analyze_area_from_netlist(args.netlist)
    else:
        # Use default values
        print(f"\nNetlist file not specified, using default area values")
        analyzer.get_default_area()
    
    # Power and performance analysis
    if not args.area_only:
        if args.meas:
            analyzer.parse_measurement_file(args.meas)
        else:
            print("\nWarning: Measurement file not specified, unable to analyze power and performance")
    
    # Generate report
    analyzer.generate_report(output_file=args.output)


if __name__ == '__main__':
    main()