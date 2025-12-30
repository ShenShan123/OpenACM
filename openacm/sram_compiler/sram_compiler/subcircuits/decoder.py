from PySpice.Spice.Netlist import SubCircuitFactory, Circuit
from PySpice.Unit import u_Ohm, u_pF, u_V, u_ns
from .base_subcircuit import BaseSubcircuit
from numpy.f2py.crackfortran import endifs
import math
from math import ceil, log2
from .standard_cell import PNAND3_for_decoder,Pinv_for_decoder,PNAND2_for_decoder # type: ignore

class AND3(BaseSubcircuit):  # 3-input AND = NAND + INV

    NAME = "AND3"
    NODES = ('VDD', 'VSS', 'A', 'B', 'C', 'Z')

    def __init__(self, nmos_model_name, pmos_model_name,
                 # Base widths for NAND gate transistors
                 base_nand_pmos_width=0.27e-6, base_nand_nmos_width=0.18e-6,
                 # Base widths for Inverter transistors
                 base_inv_pmos_width=0.27e-6, base_inv_nmos_width=0.09e-6,
                 length=0.05e-6,
                 w_rc=False, pi_res=100 @ u_Ohm, pi_cap=0.001 @ u_pF,sweep_decoder=False,
                 pmos_model_choices = 'PMOS_VTG',nmos_model_choices = 'NMOS_VTG'
                 ):

        super().__init__(
            nmos_model_name, pmos_model_name,
            base_nand_nmos_width, base_nand_pmos_width, length,
            w_rc=w_rc, pi_res=pi_res, pi_cap=pi_cap,
        )
        self.sweep_decoder=sweep_decoder
        self.pmos_model_choices=pmos_model_choices
        self.nmos_model_choices=nmos_model_choices
        # This is the nand gate
        self.nand_gate = PNAND3_for_decoder(nmos_model_name=nmos_model_name,
                                pmos_model_name=pmos_model_name,
                                base_pmos_width=base_nand_pmos_width,
                                base_nmos_width=base_nand_nmos_width,
                                length=length,sweep_decoder=self.sweep_decoder,
                                pmos_model_choices = self.pmos_model_choices,
                                nmos_model_choices = self.nmos_model_choices
                                )
        self.subcircuit(self.nand_gate)  # Add NAND gate

        # This is the inverter for driving WLs
        self.inv_driver = Pinv_for_decoder(nmos_model_name=nmos_model_name,
                                        pmos_model_name=pmos_model_name,
                                        base_pmos_width=base_inv_pmos_width,
                                        base_nmos_width=base_inv_nmos_width,
                                        length=length,sweep_decoder=self.sweep_decoder,
                                        pmos_model_choices = self.pmos_model_choices,
                                        nmos_model_choices = self.nmos_model_choices
                                        )
        self.subcircuit(self.inv_driver)  # Add inverter

        self.add_and3_components()

    def add_and3_components(self):
        
        a_node = 'A'
        b_node = "B"
        c_node = "C"
        zb_node = "zb_int"
        z_node = "Z"

        """Instantiate the `PNAND3` and `Pinv` gates"""  # instantiate
        self.X(f'PNAND3', self.nand_gate.name,
               'VDD', 'VSS', a_node, b_node, c_node, zb_node)
        self.X(f'PINV', self.inv_driver.name,
               'VDD', 'VSS', zb_node, z_node)

class AND2(BaseSubcircuit):  # 2-input AND = NAND2 + INV

    NAME = "AND2"
    NODES = ('VDD', 'VSS', 'A', 'B', 'Z')

    def __init__(self, nmos_model_name, pmos_model_name,
                 # Base widths for NAND gate transistors
                 base_nand_pmos_width=0.27e-6, base_nand_nmos_width=0.18e-6,
                 # Base widths for Inverter transistors
                 base_inv_pmos_width=0.27e-6, base_inv_nmos_width=0.09e-6,
                 length=0.05e-6,
                 w_rc=False, pi_res=100 @ u_Ohm, pi_cap=0.001 @ u_pF,sweep_decoder=False,
                 pmos_model_choices = 'PMOS_VTG',nmos_model_choices = 'NMOS_VTG'
                 ):

        super().__init__(
            nmos_model_name, pmos_model_name,
            base_nand_nmos_width, base_nand_pmos_width, length,
            w_rc=w_rc, pi_res=pi_res, pi_cap=pi_cap,
        )
        self.sweep_decoder=sweep_decoder
        self.pmos_model_choices=pmos_model_choices
        self.nmos_model_choices=nmos_model_choices
        # This is the nand gate
        self.nand_gate = PNAND2_for_decoder(nmos_model_name=nmos_model_name,
                                pmos_model_name=pmos_model_name,
                                base_pmos_width=base_nand_pmos_width,
                                base_nmos_width=base_nand_nmos_width,
                                length=length,sweep_decoder=self.sweep_decoder,
                                pmos_model_choices = self.pmos_model_choices,
                                nmos_model_choices = self.nmos_model_choices
                                )
        self.subcircuit(self.nand_gate)  # Add NAND gate

        # This is the inverter for driving WLs
        self.inv_driver = Pinv_for_decoder(nmos_model_name=nmos_model_name,
                                        pmos_model_name=pmos_model_name,
                                        base_pmos_width=base_inv_pmos_width,
                                        base_nmos_width=base_inv_nmos_width,
                                        length=length,sweep_decoder=self.sweep_decoder,
                                        pmos_model_choices = self.pmos_model_choices,
                                        nmos_model_choices = self.nmos_model_choices
                                        )
        self.subcircuit(self.inv_driver)  # Add inverter

        self.add_and3_components()

    def add_and3_components(self):
       
        a_node = 'A'
        b_node = "B"
        zb_node = "zb_int"
        z_node = "Z"

        """Instantiate the `PNAND3` and `Pinv` gates"""  # instantiate
        self.X(f'PNAND3', self.nand_gate.name,
               'VDD', 'VSS', a_node, b_node, zb_node)
        self.X(f'PINV', self.inv_driver.name,
               'VDD', 'VSS', zb_node, z_node)


class DECODER3_8(BaseSubcircuit):  # 3-to-8 decoder with enable EN

    NAME = "DECODER3_8"
    NODES = ('VDD', 'VSS','EN', 'A0', 'A1', 'A2', 'WL0', 'WL1', 'WL2', 'WL3', 'WL4', 'WL5', 'WL6', 'WL7')

    def __init__(self, nmos_model_name, pmos_model_name,
                 # Base widths for NAND gate transistors
                 base_nand_pmos_width=0.27e-6, base_nand_nmos_width=0.18e-6,
                 # Base widths for Inverter transistors
                 base_inv_pmos_width=0.27e-6, base_inv_nmos_width=0.09e-6,
                 length=0.05e-6,
                 w_rc=False, pi_res=100 @ u_Ohm, pi_cap=0.001 @ u_pF,sweep_decoder=False,
                 pmos_model_choices = 'PMOS_VTG',nmos_model_choices = 'NMOS_VTG'
                 ):

        super().__init__(
            nmos_model_name, pmos_model_name,
            base_nand_nmos_width, base_nand_pmos_width, length,
            w_rc=w_rc, pi_res=pi_res, pi_cap=pi_cap,
        )
        self.sweep_decoder=sweep_decoder
        self.pmos_model_choices=pmos_model_choices
        self.nmos_model_choices=nmos_model_choices
        # Create three inverters to generate input complements
        self.inv_A0 = Pinv_for_decoder(
            nmos_model_name=nmos_model_name,
            pmos_model_name=pmos_model_name,
            base_pmos_width=base_inv_pmos_width,
            base_nmos_width=base_inv_nmos_width,
            length=length,
            sweep_decoder=self.sweep_decoder,
            pmos_model_choices = self.pmos_model_choices,
            nmos_model_choices = self.nmos_model_choices
        )
        self.subcircuit(self.inv_A0)

        self.inv_A1 = Pinv_for_decoder(
            nmos_model_name=nmos_model_name,
            pmos_model_name=pmos_model_name,
            base_pmos_width=base_inv_pmos_width,
            base_nmos_width=base_inv_nmos_width,
            length=length,
            sweep_decoder=self.sweep_decoder,
            pmos_model_choices = self.pmos_model_choices,
            nmos_model_choices = self.nmos_model_choices
        )
        self.subcircuit(self.inv_A1)

        self.inv_A2 =Pinv_for_decoder(
            nmos_model_name=nmos_model_name,
            pmos_model_name=pmos_model_name,
            base_pmos_width=base_inv_pmos_width,
            base_nmos_width=base_inv_nmos_width,
            length=length,
            sweep_decoder=self.sweep_decoder,
            pmos_model_choices = self.pmos_model_choices,
            nmos_model_choices = self.nmos_model_choices
        )
        self.subcircuit(self.inv_A2)

        # Create eight 3-input AND gates
        self.and_gates = []
        for _ in range(8):
            and_gate = AND3(
                nmos_model_name=nmos_model_name,
                pmos_model_name=pmos_model_name,
                base_nand_pmos_width=base_nand_pmos_width,
                base_nand_nmos_width=base_nand_nmos_width,
                base_inv_pmos_width=base_inv_pmos_width,
                base_inv_nmos_width=base_inv_nmos_width,
                length=length,
                w_rc=w_rc,
                pi_res=pi_res,
                pi_cap=pi_cap,
                sweep_decoder=self.sweep_decoder,
                pmos_model_choices = self.pmos_model_choices,
                nmos_model_choices = self.nmos_model_choices
            )
            self.subcircuit(and_gate)
            self.and_gates.append(and_gate)
        # Create eight AND gates for enable
        self.and_for_en = []
        for _ in range(8):
            and_for_en = AND2(
                nmos_model_name=nmos_model_name,
                pmos_model_name=pmos_model_name,
                base_nand_pmos_width=base_nand_pmos_width,
                base_nand_nmos_width=base_nand_nmos_width,
                base_inv_pmos_width=base_inv_pmos_width,
                base_inv_nmos_width=base_inv_nmos_width,
                length=length,
                w_rc=w_rc,
                pi_res=pi_res,
                pi_cap=pi_cap,
                sweep_decoder=self.sweep_decoder,
                pmos_model_choices = self.pmos_model_choices,
                nmos_model_choices = self.nmos_model_choices
            )
            self.subcircuit(and_for_en)
            self.and_for_en.append(and_for_en)

        self.add_decoder_components()

    def add_decoder_components(self):
        # Instantiate three inverter subcircuits
        self.X('INV_A1', self.inv_A0.name, 'VDD', 'VSS', 'A0', 'A0b')
        self.X('INV_A2', self.inv_A1.name, 'VDD', 'VSS', 'A1', 'A1b')
        self.X('INV_A3', self.inv_A2.name, 'VDD', 'VSS', 'A2', 'A2b')

        # Define input combinations (truth table) for each AND gate
        input_combinations = [
            ('A0b', 'A1b', 'A2b'),  # WL0: 000
            ('A0b', 'A1b', 'A2'),  # WL1: 001
            ('A0b', 'A1', 'A2b'),  # WL2: 010
            ('A0b', 'A1', 'A2'),  # WL3: 011
            ('A0', 'A1b', 'A2b'),  # WL4: 100
            ('A0', 'A1b', 'A2'),  # WL5: 101
            ('A0', 'A1', 'A2b'),  # WL6: 110
            ('A0', 'A1', 'A2')  # WL7: 111
        ]

        # Instantiate eight AND gates and corresponding EN AND gates
        for i in range(8):
            inputs = input_combinations[i]
            self.X(f"AND{i}", self.and_gates[i].name,
                   'VDD', 'VSS',
                   inputs[0],  # input A
                   inputs[1],  # input B
                   inputs[2],  # input C
                   f'WL{i}_pre'  # output
                   )
            self.X(f"AND_EN{i}", self.and_for_en[i].name,
                   'VDD', 'VSS',
                   f'WL{i}_pre',  # input A
                   'EN',  # input B
                   f'WL{i}'  # output
                   )


class DECODER_CASCADE(BaseSubcircuit):
    """Cascaded row address decoder; supports arbitrary row counts"""
    NAME = "DECODER_CASCADE"
    
    def __init__(self, nmos_model_name, pmos_model_name, num_rows=16,
                 base_inv_pmos_width=0.27e-6, base_inv_nmos_width=0.09e-6,
                 base_nand_pmos_width=0.27e-6, base_nand_nmos_width=0.18e-6,
                 length=0.05e-6,
                 w_rc=False, pi_res=100 @ u_Ohm, pi_cap=0.001 @ u_pF,sweep_decoder=False,
                pmos_model_choices = 'PMOS_VTG',nmos_model_choices = 'NMOS_VTG'
                 ):
        # Compute address bit-width and number of levels
        self.w_rc=w_rc
        self.num_rows = num_rows
        self.sweep_decoder = sweep_decoder
        self.pmos_model_choices=pmos_model_choices
        self.nmos_model_choices=nmos_model_choices
        self.n_bits = ceil(log2(num_rows)) if num_rows > 1 else 1
        self.n_levels = ceil(self.n_bits / 3.0)
        # NODES = ['VDD', 'VSS', 'EN'] + [f'A{i}' for i in range(self.n_bits)] + [f'WL{i}' for i in range(num_rows)]

        # Compute decoder counts per level (starting from the last level)
        level_groups = [0] * self.n_levels
        level_groups[self.n_levels - 1] = ceil(num_rows / 8.0)
        for level in range(self.n_levels - 2, -1, -1):
            level_groups[level] = ceil(level_groups[level + 1] / 8.0)
        self.level_groups = level_groups

         # Define nodes: VDD, VSS, address lines, wordlines
        nodes = ['VDD', 'VSS']
        nodes.extend([f'A{i}' for i in range(self.n_bits)])
        nodes.extend([f'WL{i}' for i in range(num_rows)])
        self.NODES = nodes
        super().__init__(
            nmos_model_name, pmos_model_name,
            base_nand_nmos_width, base_nand_pmos_width, length,
            w_rc=w_rc, pi_res=pi_res, pi_cap=pi_cap,
        )
        
        

        # Store decoders per level and output nodes
        self.decoders_by_level = []
        self.level_output_nodes = [[] for _ in range(self.n_levels)]


        # Create all decoders
        for level in range(self.n_levels):
            level_decoders = []
            for decoder_idx in range(self.level_groups[level]):
                # Compute address bits used by this level
                address_nodes = []
                # Compute start bit: from most significant bit
                start_bit = 3 * (self.n_levels-level-1)
                for bit in range(3):
                    bit_idx = start_bit + bit
                    if bit_idx >= 0 and bit_idx < self.n_bits:
                        address_nodes.append(f'A{bit_idx}')
                    else:
                        address_nodes.append('VSS')  # Tie to ground if address bits are insufficient
                # Instantiate decoder instance
                decoder = DECODER3_8(
                    nmos_model_name=nmos_model_name,
                    pmos_model_name=pmos_model_name,
                    base_inv_pmos_width=base_inv_pmos_width,
                    base_inv_nmos_width=base_inv_nmos_width,
                    base_nand_pmos_width=base_nand_pmos_width,
                    base_nand_nmos_width=base_nand_nmos_width,
                    length=length,
                    w_rc=self.w_rc,
                    sweep_decoder=self.sweep_decoder,
                    pmos_model_choices = self.pmos_model_choices,
                    nmos_model_choices = self.nmos_model_choices
                )
                self.subcircuit(decoder)
                level_decoders.append(decoder)

                # Determine enable signal
                if level == 0:
                    enable_signal = 'VDD'
                else:
                    # Get enable from previous level output nodes
                    if decoder_idx < len(self.level_output_nodes[level - 1]):
                        enable_signal = self.level_output_nodes[level - 1][decoder_idx]
                    else:
                        enable_signal = 'VSS'

                # Determine output nodes
                output_nodes = []
                for out_idx in range(8):
                    if level == self.n_levels - 1:  # Final level: output wordlines
                        wl_idx = decoder_idx * 8 + out_idx
                        if wl_idx < num_rows:
                            node_name = f'WL{wl_idx}'
                        else:
                            node_name = f'NC_{level}_{decoder_idx}_{out_idx}'
                    else:  # Intermediate levels: output enable signals
                        node_name = f'EN_{level}_{decoder_idx}_{out_idx}'
                    output_nodes.append(node_name)

                # Save output nodes (for next level enables)
                self.level_output_nodes[level].extend(output_nodes)

                # Instantiate decoder
                self.X(f'DEC_{level}_{decoder_idx}', decoder.NAME,
                       'VDD', 'VSS',
                       enable_signal,
                       address_nodes[2], address_nodes[1], address_nodes[0],  # A0, A1, A2
                       *output_nodes
                       )
            self.decoders_by_level.append(level_decoders)



if __name__ == '__main__':
    # Create 3-to-8 decoder instance
    decoder = DECODER_CASCADE(
        nmos_model_name="NMOS_VTG",
        pmos_model_name="PMOS_VTG",
        num_rows=2,
        base_inv_pmos_width=0.27e-6,
        base_inv_nmos_width=0.09e-6,
        base_nand_pmos_width=0.27e-6,
        base_nand_nmos_width=0.18e-6,
        length=0.05e-6,
        w_rc=False
    )

    # Print netlist info
    print("=" * 80)
    print("CASCADE DECODER NETLIST")
    print("=" * 80)
    print(decoder)
    print("=" * 80)

    # Print structure info
    print("\nDecoder Structure:")
    print(f"- Total levels: {decoder.n_levels}")
    for level, count in enumerate(decoder.level_groups):
        print(f"  Level {level}: {count} decoders")
    print(f"Total word lines: {decoder.num_rows}")
