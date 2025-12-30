from PySpice.Spice.Netlist import SubCircuitFactory, Circuit
from PySpice.Unit import u_Ohm, u_pF, u_V, u_ns
from .base_subcircuit import BaseSubcircuit


class ColumnMux(BaseSubcircuit):
    """Column multiplexer for SRAM array using NMOS pass gates."""
    
    def __init__(self, nmos_model_name, pmos_model_name, 
                 num_in, # Number of columns to multiplex
                 base_nmos_width=0.135e-6, base_pmos_width=0.135e-6, 
                 length=50e-9,
                 w_rc=False, pi_res=100 @ u_Ohm, pi_cap=0.001 @ u_pF, sweep_columnmux = False,
                 pmos_modle_choices='PMOS_VTG',nmos_modle_choices='NMOS_VTG'
                 ):
        """
        Args:
            nmos_model_name (str): NMOS model name.
            pmos_model_name (str): PMOS model name.
            num_in (int): Number of columns multiplexed into one output.
            base_nmos_width (float): Width of the NMOS pass gates.
            base_pmos_width (float): Width of the PMOS pass gates.
            length (float): Length of the NMOS pass gates.
            w_rc (bool): Whether use estimated parasitic RCs.
            pi_res (float): Value of parasitic Rs.
            pi_cap (float): Value of parasitic Cs.
        """
        self.NAME = f'COLUMNMUX{num_in}' # Multi-input multiplexer
        # Power Nodes: VDD, VSS,
        # Output: SA_IN (Sense Amplifier INput), SA_INB (sense amplifier bitline bar),
        # Input: SEL (SELect signals), BL/BLB (bitlines).
        nodes = ['VDD', 'VSS', 'SA_IN', 'SA_INB']
        nodes += [f'SEL{i}' for i in range(num_in)]  # input: Select signals (per input)
        nodes += [f'BL{i}' for i in range(num_in)]   # input: Bitlines
        nodes += [f'BLB{i}' for i in range(num_in)]  # input: Bitline bars
        self.NODES = tuple(nodes)

        super().__init__(
            nmos_model_name, pmos_model_name,
            base_nmos_width, base_pmos_width, length,
            w_rc, pi_res, pi_cap,
        )

        self.pmos_modle_choices=pmos_modle_choices
        self.nmos_modle_choices=nmos_modle_choices
        self.num_in = num_in
        self. sweep_columnmux =  sweep_columnmux

        self.REQUIRED_COLUMNS = ['pmos_model_columnmux', 'nmos_model_columnmux']
        # Read model names from parameter file
        self.mos_model_index = self.read_mos_model_from_param_file(self.REQUIRED_COLUMNS)
        self.add_switch_transistor() # Add multiplexer transistors
    
    
    def add_switch_transistor(self):
        # Add NMOS pass transistors for each column in the mux
        for i in range(self.num_in):    # Generate identical structure per input
            # We do not need to add RCs to node BL/BLB and SA_IN/SA_INB,
            # as these nodes will get their own RCs 
            # during the instantiations of SRAM core and SAs.
            if self.w_rc:                                    # Consider RC networks on SEL/SELB lines
                sel_node = self.add_rc_networks_to_node(f'SEL{i}', num_segs=1)
                selb_node = self.add_rc_networks_to_node(f'SELB{i}', num_segs=1)
            else:
                sel_node = f'SEL{i}'
                selb_node = f'SELB{i}'
            if not self.sweep_columnmux:
                # Inverters for select signal
                self.M(f'Invp_{i}', selb_node, sel_node, 'VDD', 'VDD',
                    model=self.pmos_pdk_model,
                    w=self.base_pmos_width, l=self.length)
                self.M(f'Invn_{i}', selb_node, sel_node, 'VSS', 'VSS',
                    model=self.nmos_pdk_model,
                    w=self.base_nmos_width, l=self.length)
                
                # Bitline pass gate
                self.M(f'Muxn_BL_{i}', f'BL{i}', sel_node, 'SA_IN', 'VSS', 
                    model=self.nmos_pdk_model, w=self.base_nmos_width, 
                    l=self.length)
                self.M(f'Muxp_BL_{i}', f'BL{i}', selb_node, 'SA_IN', 'VDD', 
                    model=self.pmos_pdk_model, w=self.base_pmos_width, 
                    l=self.length)
                # Bitline bar pass gate
                self.M(f'Muxn_BLB_{i}', f'BLB{i}', sel_node, 'SA_INB', 'VSS',
                    model=self.nmos_pdk_model, w=self.base_nmos_width, 
                    l=self.length)
                self.M(f'Muxp_BLB_{i}', f'BLB{i}', selb_node, 'SA_INB', 'VDD',
                    model=self.pmos_pdk_model, w=self.base_pmos_width, 
                    l=self.length)
            else:
                # Inverters for select signal
                self.M(f'Invp_{i}', selb_node, sel_node, 'VDD', 'VDD',
                    model=self.pmos_modle_choices[int(self.mos_model_index['pmos'])],
                    w='pmos_width_mux', l='length_mux')
                self.M(f'Invn_{i}', selb_node, sel_node, 'VSS', 'VSS',
                    model=self.nmos_modle_choices[int(self.mos_model_index['nmos'])],
                    w= 'nmos_width_mux', l='length_mux')
                
                # Bitline pass gate
                self.M(f'Muxn_BL_{i}', f'BL{i}', sel_node, 'SA_IN', 'VSS', 
                    model=self.nmos_modle_choices[int(self.mos_model_index['nmos'])],
                    w= 'nmos_width_mux', l='length_mux')
                self.M(f'Muxp_BL_{i}', f'BL{i}', selb_node, 'SA_IN', 'VDD', 
                    model=self.pmos_modle_choices[int(self.mos_model_index['pmos'])],
                    w='pmos_width_mux', l='length_mux')
                # Bitline bar pass gate
                self.M(f'Muxn_BLB_{i}', f'BLB{i}', sel_node, 'SA_INB', 'VSS',
                    model=self.nmos_modle_choices[int(self.mos_model_index['nmos'])],
                    w= 'nmos_width_mux', l='length_mux')
                self.M(f'Muxp_BLB_{i}', f'BLB{i}', selb_node, 'SA_INB', 'VDD',
                    model=self.pmos_modle_choices[int(self.mos_model_index['pmos'])], 
                    w='pmos_width_mux', l='length_mux')


class ColumnMux_simple(BaseSubcircuit):
    """Column multiplexer for SRAM array using NMOS pass gates."""
    
    def __init__(self, nmos_model_name, pmos_model_name, 
                 num_in, # Number of columns to multiplex
                 base_nmos_width=0.135e-6, base_pmos_width=0.135e-6, 
                 length=50e-9,
                 w_rc=False, pi_res=100 @ u_Ohm, pi_cap=0.001 @ u_pF, sweep_columnmux = False,
                 pmos_modle_choices='PMOS_VTG',nmos_modle_choices='NMOS_VTG'
                 ):
        """
        Args:
            nmos_model_name (str): NMOS model name.
            pmos_model_name (str): PMOS model name.
            num_in (int): Number of columns multiplexed into one output.
            base_nmos_width (float): Width of the NMOS pass gates.
            base_pmos_width (float): Width of the PMOS pass gates.
            length (float): Length of the NMOS pass gates.
            w_rc (bool): Whether use estimated parasitic RCs.
            pi_res (float): Value of parasitic Rs.
            pi_cap (float): Value of parasitic Cs.
        """
        self.NAME = f'COLUMNMUX{num_in}' # Multi-input multiplexer
        # Power Nodes: VDD, VSS,
        # Output: SA_IN (Sense Amplifier INput), SA_INB (sense amplifier bitline bar),
        # Input: SEL (SELect signals), BL/BLB (bitlines).
        nodes = ['VDD', 'VSS', 'SA_IN', 'SA_INB']
        nodes += [f'SEL{i}' for i in range(num_in)]  # input: Select signals (per input)
        nodes += [f'SELB{i}' for i in range(num_in)]
        nodes += [f'BL{i}' for i in range(num_in)]   # input: Bitlines
        nodes += [f'BLB{i}' for i in range(num_in)]  # input: Bitline bars
        self.NODES = tuple(nodes)

        super().__init__(
            nmos_model_name, pmos_model_name,
            base_nmos_width, base_pmos_width, length,
            w_rc, pi_res, pi_cap,
        )

        self.pmos_modle_choices=pmos_modle_choices
        self.nmos_modle_choices=nmos_modle_choices
        self.num_in = num_in
        self. sweep_columnmux =  sweep_columnmux

        self.REQUIRED_COLUMNS = ['pmos_model_columnmux', 'nmos_model_columnmux']
        # Read model names from parameter file
        self.mos_model_index = self.read_mos_model_from_param_file(self.REQUIRED_COLUMNS)
        self.add_switch_transistor() # Add multiplexer transistors
    
    
    def add_switch_transistor(self):
        # Add NMOS pass transistors for each column in the mux
        for i in range(self.num_in):    # Generate identical structure per input
            # We do not need to add RCs to node BL/BLB and SA_IN/SA_INB,
            # as these nodes will get their own RCs 
            # during the instantiations of SRAM core and SAs.
            if self.w_rc:                                    # Consider RC networks on SEL/SELB lines
                sel_node = self.add_rc_networks_to_node(f'SEL{i}', num_segs=1)
                selb_node = self.add_rc_networks_to_node(f'SELB{i}', num_segs=1)
            else:
                sel_node = f'SEL{i}'
                selb_node = f'SELB{i}'
            if not self.sweep_columnmux:
                # Bitline pass gate
                # self.M(f'Muxn_BL_{i}', f'BL{i}', sel_node, 'SA_IN', 'VDD', 
                #     model=self.pmos_pdk_model, w=self.base_pmos_width, 
                #     l=self.length)

                # # Bitline bar pass gate
                # self.M(f'Muxn_BLB_{i}', f'BLB{i}', sel_node, 'SA_INB', 'VDD',
                #     model=self.pmos_pdk_model, w=self.base_pmos_width, 
                #     l=self.length)
                # Bitline pass gate
                self.M(f'Muxn_BL_{i}', f'BL{i}', sel_node, 'SA_IN', 'VSS', 
                    model=self.nmos_pdk_model, w=self.base_nmos_width, 
                    l=self.length)
                self.M(f'Muxp_BL_{i}', f'BL{i}', selb_node, 'SA_IN', 'VDD', 
                    model=self.pmos_pdk_model, w=self.base_pmos_width, 
                    l=self.length)
                # Bitline bar pass gate
                self.M(f'Muxn_BLB_{i}', f'BLB{i}', sel_node, 'SA_INB', 'VSS',
                    model=self.nmos_pdk_model, w=self.base_nmos_width, 
                    l=self.length)
                self.M(f'Muxp_BLB_{i}', f'BLB{i}', selb_node, 'SA_INB', 'VDD',
                    model=self.pmos_pdk_model, w=self.base_pmos_width, 
                    l=self.length)

            else:     
                # Bitline pass gate
                # self.M(f'Muxn_BL_{i}', f'BL{i}', sel_node, 'SA_IN', 'VDD', 
                #     model=self.pmos_modle_choices[int(self.mos_model_index['pmos'])],
                #     w= 'pmos_width_mux', l='length_mux')
       
                # # Bitline bar pass gate
                # self.M(f'Muxn_BLB_{i}', f'BLB{i}', sel_node, 'SA_INB', 'VDD',
                #     model=self.pmos_modle_choices[int(self.mos_model_index['pmos'])],
                #     w= 'pmos_width_mux', l='length_mux')
                # Bitline pass gate
                self.M(f'Muxn_BL_{i}', f'BL{i}', sel_node, 'SA_IN', 'VSS', 
                    model=self.nmos_modle_choices[int(self.mos_model_index['nmos'])],
                    w= 'nmos_width_mux', l='length_mux')
                self.M(f'Muxp_BL_{i}', f'BL{i}', selb_node, 'SA_IN', 'VDD', 
                    model=self.pmos_modle_choices[int(self.mos_model_index['pmos'])],
                    w='pmos_width_mux', l='length_mux')
                # Bitline bar pass gate
                self.M(f'Muxn_BLB_{i}', f'BLB{i}', sel_node, 'SA_INB', 'VSS',
                    model=self.nmos_modle_choices[int(self.mos_model_index['nmos'])],
                    w= 'nmos_width_mux', l='length_mux')
                self.M(f'Muxp_BLB_{i}', f'BLB{i}', selb_node, 'SA_INB', 'VDD',
                    model=self.pmos_modle_choices[int(self.mos_model_index['pmos'])], 
                    w='pmos_width_mux', l='length_mux')
                

        # Performance considerations:
        # 1. NMOS width should be large enough to reduce resistance (~2-3x access transistor width).
        # 2. Ensure only one SEL signal is active at a time to avoid contention.



class SenseAmp(BaseSubcircuit):
    """Differential sense amplifier with enable signal."""
    
    NAME = 'SENSEAMP'
    # Input: VDD, VSS, SA_BL, SA_BLB, EN
    # Output: OUT, OUTB, 
    NODES = ('VDD', 'VSS', 'EN', 'IN', 'INB', 'Q', 'QB')

    def __init__(self, nmos_model_name, pmos_model_name, 
                 base_nmos_width=0.27e-6, base_pmos_width=0.54e-6, length=50e-9,
                 w_rc=False, pi_res=100 @ u_Ohm, pi_cap=0.001 @ u_pF,sweep_senseamp = False,
                 pmos_modle_choices='PMOS_VTG',nmos_modle_choices='NMOS_VTG'
                 ):
        """
        Args:
            nmos_model_name (str): NMOS model name.
            pmos_model_name (str): PMOS model name.
            base_nmos_width (float): Width of NMOS transistors.
            base_pmos_width (float): Width of PMOS transistors.
            length (float): Length of transistors.
        """
        super().__init__(
            nmos_model_name, pmos_model_name,
            base_nmos_width, base_pmos_width, length,
            w_rc, pi_res, pi_cap,
        )
        
        self.pmos_modle_choices=pmos_modle_choices
        self.nmos_modle_choices=nmos_modle_choices
        self.REQUIRED_COLUMNS = ['pmos_model_senseamp', 'nmos_model_senseamp']
        # Read model names from parameter file
        self.mos_model_index = self.read_mos_model_from_param_file(self.REQUIRED_COLUMNS)

        self.sweep_senseamp = sweep_senseamp
        self.pmos_width = self.base_pmos_width / 3 * 4  # Dedicated width for left/right pass transistors
        self.nmos_width = self.base_nmos_width
        self.add_sense_transistors()
    
   

    def add_sense_transistors(self):
        if self.w_rc:                                    # Consider adding RC, adjust node names
            en_node = self.add_rc_networks_to_node('EN', num_segs=2)
            in_node = self.add_rc_networks_to_node('IN', num_segs=2)
            inb_node = self.add_rc_networks_to_node('INB', num_segs=2)
            q_node = self.add_rc_networks_to_node('Q', num_segs=2)
            qb_node = self.add_rc_networks_to_node('QB', num_segs=2)
            net1_node = self.add_rc_networks_to_node('net1', num_segs=1)
        else:
            en_node = 'EN'
            in_node = 'IN'
            inb_node = 'INB'
            q_node = 'Q'
            qb_node = 'QB'
            net1_node = 'net1'
        if not self.sweep_senseamp:
            # Cross-coupled inverters for positive feedback
            self.M(1, 'Q', qb_node, 'net1', 'VSS', model=self.nmos_pdk_model,
                w=self.base_nmos_width, l=self.length)  # NMOS
            self.M(2, 'Q', qb_node, 'VDD', 'VDD', model=self.pmos_pdk_model,
                w=self.base_pmos_width, l=self.length)  # PMOS
            self.M(3, 'QB', q_node, 'net1', 'VSS', model=self.nmos_pdk_model,
                w=self.base_nmos_width, l=self.length)  # NMOS
            self.M(4, 'QB', q_node, 'VDD', 'VDD', model=self.pmos_pdk_model,
                w=self.base_pmos_width, l=self.length)  # PMOS

            # Sense enable transistors (note: left/right pass transistors use non-base width)
            self.M(5, 'Q', en_node, in_node, 'VDD', model=self.pmos_pdk_model,
                w=self.pmos_width, l=self.length)  # NMOS (wider for lower resistance)
            self.M(6, 'QB', en_node, inb_node, 'VDD', model=self.pmos_pdk_model,
                w=self.pmos_width, l=self.length)  # NMOS (wider for lower resistance)
            self.M(7, net1_node, en_node, 'VSS', 'VSS', model=self.nmos_pdk_model,
                w=self.base_nmos_width, l=self.length)  # NMOS
        else:
            self.M(1, 'Q', qb_node, 'net1', 'VSS', model=self.nmos_modle_choices[int(self.mos_model_index['nmos'])],
                w='nmos_width_senseamp', l='length_senseamp')  # NMOS
            self.M(2, 'Q', qb_node, 'VDD', 'VDD', model=self.pmos_modle_choices[int(self.mos_model_index['pmos'])],
                w='pmos_width_senseamp', l='length_senseamp')  # PMOS
            self.M(3, 'QB', q_node, 'net1', 'VSS', model=self.nmos_modle_choices[int(self.mos_model_index['nmos'])],
                w='nmos_width_senseamp', l='length_senseamp')  # NMOS
            self.M(4, 'QB', q_node, 'VDD', 'VDD', model=self.pmos_modle_choices[int(self.mos_model_index['pmos'])],
                w='pmos_width_senseamp', l='length_senseamp')  # PMOS

            # Sense enable transistors (note: left/right pass transistors use non-base width)
            self.M(5, 'Q', en_node, in_node, 'VDD', model=self.pmos_modle_choices[int(self.mos_model_index['pmos'])],
                w='pmos_width_senseamp', l='length_senseamp')  # NMOS (wider for lower resistance)
            self.M(6, 'QB', en_node, inb_node, 'VDD', model=self.pmos_modle_choices[int(self.mos_model_index['pmos'])],
                w='pmos_width_senseamp', l='length_senseamp')  # NMOS (wider for lower resistance)
            self.M(7, net1_node, en_node, 'VSS', 'VSS', model=self.nmos_modle_choices[int(self.mos_model_index['nmos'])],
                w='nmos_width_senseamp', l='length_senseamp')  # NMOS

        # Performance considerations:
        # 1. Cross-coupled inverters should be balanced for symmetric operation.
        # 2. Sense enable transistors should be wider to minimize resistance.
        # 3. Ensure SE signal is timed correctly to avoid premature sensing.
