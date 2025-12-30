# standard_cells.py
from PySpice.Spice.Netlist import SubCircuitFactory, SubCircuit
from PySpice.Unit import u_Ohm, u_pF, u_um, u_m
from .base_subcircuit import BaseSubcircuit

class Pinv_for_wordline_driver(BaseSubcircuit):
    """
    CMOS Inverter based on sram_16x4_pinv netlist.
    Widths can be dynamically scaled based on num_cols.
    """
    NAME = "PINV"
    NODES = ('VDD', 'VSS', 'A', 'Z')

    def __init__(self,
                 nmos_model_name,
                 pmos_model_name,
                 base_pmos_width=0.27e-6,
                 base_nmos_width=0.09e-6,
                 length=0.05e-6,
                 num_cols=4,
                 w_rc=False,
                 pi_res=100 @ u_Ohm,
                 pi_cap=0.001 @ u_pF,
                 sweep_wordlinedriver=False,
                 pmos_modle_choices='PMOS_VTG',
                 nmos_modle_choices='NMOS_VTG'
                 ):
        super().__init__(
            nmos_model_name,
            pmos_model_name,
            base_nmos_width,
            base_pmos_width,
            length,
            w_rc=w_rc,
            pi_res=pi_res,
            pi_cap=pi_cap,
        )
        self.pmos_modle_choices = pmos_modle_choices
        self.nmos_modle_choices = nmos_modle_choices
        self.num_cols = num_cols
        self.sweep_wordlinedriver = sweep_wordlinedriver

        self.pmos_width = self.calculate_dynamic_width(base_pmos_width, num_cols)
        self.nmos_width = self.calculate_dynamic_width(base_nmos_width, num_cols)

        self.REQUIRED_COLUMNS = ['pmos_model_wld_invp', 'nmos_model_wld_invn']
        self.mos_model_index = self.read_mos_model_from_param_file(self.REQUIRED_COLUMNS)
        self.add_inverter_transistors()

    # ------------------------------------------------------------------ #
    def calculate_dynamic_width(self, base_width, num_cols_config):
        num_cols_config = max(num_cols_config, 4)
        scaling_factor = num_cols_config / 4.0
        return base_width * scaling_factor

    def add_inverter_transistors(self):
        if not self.sweep_wordlinedriver:
            self.M('pinv_pmos', 'Z', 'A', 'VDD', 'VDD',
                   model=self.pmos_pdk_model,
                   w=self.pmos_width, l=self.length)
            self.M('pinv_nmos', 'Z', 'A', 'VSS', 'VSS',
                   model=self.nmos_pdk_model,
                   w=self.nmos_width, l=self.length)
        else:
            self.M('pinv_pmos', 'Z', 'A', 'VDD', 'VDD',
                   model=self.pmos_modle_choices[int(self.mos_model_index['pmos'])],
                   w='pmos_width_wld_invp', l='length_wld')
            self.M('pinv_nmos', 'Z', 'A', 'VSS', 'VSS',
                   model=self.nmos_modle_choices[int(self.mos_model_index['nmos'])],
                   w='nmos_width_wld_invn', l='length_wld')


class PNAND2_for_wordline_driver(BaseSubcircuit):
    NAME = "PNAND2"
    NODES = ('VDD', 'VSS', 'A', 'B', 'Z')

    def __init__(self,
                 nmos_model_name,
                 pmos_model_name,
                 base_pmos_width=0.27e-6,
                 base_nmos_width=0.18e-6,
                 length=0.05e-6,
                 num_cols=4,
                 w_rc=False,
                 pi_res=100 @ u_Ohm,
                 pi_cap=0.001 @ u_pF,
                 sweep_wordlinedriver=False,
                 pmos_modle_choices='PMOS_VTG',
                 nmos_modle_choices='NMOS_VTG'):
        super().__init__(
            nmos_model_name,
            pmos_model_name,
            base_nmos_width,
            base_pmos_width,
            length,
            w_rc=w_rc,
            pi_res=pi_res,
            pi_cap=pi_cap,
        )
        self.pmos_modle_choices = pmos_modle_choices
        self.nmos_modle_choices = nmos_modle_choices
        self.sweep_wordlinedriver = sweep_wordlinedriver
        self.REQUIRED_COLUMNS = ['pmos_model_wld_nandp', 'nmos_model_wld_nandn']
        self.mos_model_index = self.read_mos_model_from_param_file(self.REQUIRED_COLUMNS)
        self.add_nand2_transistors()

    # ------------------------------------------------------------------ #
    def add_nand2_transistors(self):
        if not self.sweep_wordlinedriver:
            self.M('pnand2_pmos1', 'VDD', 'A', 'Z', 'VDD',
                   model=self.pmos_pdk_model,
                   w=self.base_pmos_width, l=self.length)
            self.M('pnand2_pmos2', 'Z', 'B', 'VDD', 'VDD',
                   model=self.pmos_pdk_model,
                   w=self.base_pmos_width, l=self.length)

            self.M('pnand2_nmos1', 'Z', 'B', 'net1_nand', 'VSS',
                   model=self.nmos_pdk_model,
                   w=self.base_nmos_width, l=self.length)
            self.M('pnand2_nmos2', 'net1_nand', 'A', 'VSS', 'VSS',
                   model=self.nmos_pdk_model,
                   w=self.base_nmos_width, l=self.length)
        else:
            self.M('pnand2_pmos1', 'VDD', 'A', 'Z', 'VDD',
                   model=self.pmos_modle_choices[int(self.mos_model_index['pmos'])],
                   w='pmos_width_wld_nandp', l='length_wld')
            self.M('pnand2_pmos2', 'Z', 'B', 'VDD', 'VDD',
                   model=self.pmos_modle_choices[int(self.mos_model_index['pmos'])],
                   w='pmos_width_wld_nandp', l='length_wld')

            self.M('pnand2_nmos1', 'Z', 'B', 'net1_nand', 'VSS',
                   model=self.nmos_modle_choices[int(self.mos_model_index['nmos'])],
                   w='nmos_width_wld_nandn', l='length_wld')
            self.M('pnand2_nmos2', 'net1_nand', 'A', 'VSS', 'VSS',
                   model=self.nmos_modle_choices[int(self.mos_model_index['nmos'])],
                   w='nmos_width_wld_nandn', l='length_wld')
            
class Pinv_for_decoder(BaseSubcircuit):  # Inverter
    """
    CMOS Inverter based on sram_16x4_pinv netlist.
    """
    NAME = "PINV"
    NODES = ('VDD', 'VSS', 'A', 'Z')

    def __init__(self, nmos_model_name, pmos_model_name,
                 base_pmos_width=0.27e-6, base_nmos_width=0.09e-6, length=0.05e-6,
                 w_rc=False, pi_res=100 @ u_Ohm, pi_cap=0.001 @ u_pF,sweep_decoder=False,
                 pmos_model_choices = 'PMOS_VTG',nmos_model_choices = 'NMOS_VTG'
                 ):
        super().__init__(
            nmos_model_name, pmos_model_name,
            base_nmos_width, base_pmos_width, length,
            w_rc=w_rc, pi_res=pi_res, pi_cap=pi_cap,
        )
        self.pmos_width = base_pmos_width
        self.nmos_width = base_nmos_width
        self.sweep_decoder=sweep_decoder
        self.pmos_model_choices=pmos_model_choices
        self.nmos_model_choices=nmos_model_choices
        
        # Column names required for this class
        self.REQUIRED_COLUMNS = ['pmos_model_decoder_invp', 'nmos_model_decoder_invn']
        # Read model names from parameter file
        self.mos_model_index = self.read_mos_model_from_param_file(self.REQUIRED_COLUMNS)
        self.add_inverter_transistors()  # Add inverter transistors

        
    def add_inverter_transistors(self):  # Inverter consists of one PMOS and one NMOS
        # Mpinv_pmos Z A vdd vdd pmos_vtg m=1 w=0.27u l=0.05u
        if not self.sweep_decoder:
            self.M(f'pinv_pmos', 'Z', 'A', 'VDD', 'VDD',
                model=self.pmos_pdk_model,
                w=self.pmos_width, l=self.length)
            # Mpinv_nmos Z A gnd gnd nmos_vtg m=1 w=0.09u l=0.05u
            self.M(f'pinv_nmos', 'Z', 'A', 'VSS', 'VSS',
                model=self.nmos_pdk_model,
                w=self.nmos_width, l=self.length)
        else:
            self.M(f'pinv_pmos', 'Z', 'A', 'VDD', 'VDD',
                model=self.pmos_model_choices[int(self.mos_model_index['pmos'])],
                w='pmos_width_decoder_invp', l='length_decoder')
            # Mpinv_nmos Z A gnd gnd nmos_vtg m=1 w=0.09u l=0.05u
            self.M(f'pinv_nmos', 'Z', 'A', 'VSS', 'VSS',
                model=self.nmos_model_choices[int(self.mos_model_index['nmos'])],
                w='nmos_width_decoder_invn', l='length_decoder')

class PNAND3_for_decoder(BaseSubcircuit):  # 3-input NAND gate
    """
    CMOS NAND3
    """
    NAME = "PNAND3"
    NODES = ('VDD', 'VSS', 'A', 'B', 'C', 'Z')

    def __init__(self, nmos_model_name, pmos_model_name,
                 base_pmos_width=0.27e-6, base_nmos_width=0.18e-6, length=0.05e-6,
                 w_rc=False, pi_res=100 @ u_Ohm, pi_cap=0.001 @ u_pF,sweep_decoder=False,
                 pmos_model_choices = 'PMOS_VTG',nmos_model_choices = 'MOS_VTG'
                 ):
        super().__init__(
            nmos_model_name, pmos_model_name,
            base_nmos_width, base_pmos_width, length,
            w_rc=w_rc, pi_res=pi_res, pi_cap=pi_cap,
        )
        self.sweep_decoder=sweep_decoder
        self.pmos_model_choices=pmos_model_choices
        self.nmos_model_choices=nmos_model_choices
        # Column names required for this class
        self.REQUIRED_COLUMNS = ['pmos_model_decoder_nandp', 'nmos_model_decoder_nandn']
        # Read model names from parameter file
        self.mos_model_index = self.read_mos_model_from_param_file(self.REQUIRED_COLUMNS)
        self.add_nand3_transistors()



    def add_nand3_transistors(self):
        if not self.sweep_decoder:
            self.M(f'pnand3_pmos1', 'Z', 'A', 'VDD', 'VDD',
                model=self.pmos_pdk_model,
                w=self.base_pmos_width, l=self.length)
            self.M(f'pnand3_pmos2', 'Z', 'B', 'VDD', 'VDD',
                model=self.pmos_pdk_model,
                w=self.base_pmos_width, l=self.length)
            self.M(f'pnand3_pmos3', 'Z', 'C', 'VDD', 'VDD',
                model=self.pmos_pdk_model,
                w=self.base_pmos_width, l=self.length)

            self.M(f'pnand3_nmos1', 'Z', 'A', 'net1_nand', 'VSS',
                model=self.nmos_pdk_model,
                w=self.base_nmos_width, l=self.length)
            self.M(f'pnand3_nmos2', 'net1_nand', 'B', 'net2_nand', 'VSS',
                model=self.nmos_pdk_model,
                w=self.base_nmos_width, l=self.length)
            self.M(f'pnand3_nmos3', 'net2_nand', 'C', 'VSS', 'VSS',
                model=self.nmos_pdk_model,
                w=self.base_nmos_width, l=self.length)
        else:
            self.M(f'pnand3_pmos1', 'Z', 'A', 'VDD', 'VDD',
                model=self.pmos_model_choices[int(self.mos_model_index['pmos'])],
                w='pmos_width_decoder_nandp', l='length_decoder')
            self.M(f'pnand3_pmos2', 'Z', 'B', 'VDD', 'VDD',
                model=self.pmos_model_choices[int(self.mos_model_index['pmos'])],
                w='pmos_width_decoder_nandp', l='length_decoder')
            self.M(f'pnand3_pmos3', 'Z', 'C', 'VDD', 'VDD',
                model=self.pmos_model_choices[int(self.mos_model_index['pmos'])],
                w='pmos_width_decoder_nandp', l='length_decoder')

            self.M(f'pnand3_nmos1', 'Z', 'A', 'net1_nand', 'VSS',
                model=self.nmos_model_choices[int(self.mos_model_index['nmos'])],
                w='nmos_width_decoder_nandn', l='length_decoder')
            self.M(f'pnand3_nmos2', 'net1_nand', 'B', 'net2_nand', 'VSS',
                model=self.nmos_model_choices[int(self.mos_model_index['nmos'])],
                w='nmos_width_decoder_nandn', l='length_decoder')
            self.M(f'pnand3_nmos3', 'net2_nand', 'C', 'VSS', 'VSS',
                model=self.nmos_model_choices[int(self.mos_model_index['nmos'])],
                w='nmos_width_decoder_nandn', l='length_decoder')
            
class PNAND2_for_decoder(BaseSubcircuit):  # Single 2-input NAND gate
    """
    CMOS NAND2 gate based on sram_16x4_pnand2 netlist in OpenRAM.
    Widths can be dynamically scaled based on num_cols.
    No width scaling by column count since it is not a heavy driver.
    """
    NAME = "PNAND2"
    NODES = ('VDD', 'VSS', 'A', 'B', 'Z')

    def __init__(self, nmos_model_name, pmos_model_name,
                 base_pmos_width=0.27e-6, base_nmos_width=0.18e-6, length=0.05e-6,
                 num_cols=4,  # Number of columns in the SRAM array configuration
                 w_rc=False, pi_res=100 @ u_Ohm, pi_cap=0.001 @ u_pF,sweep_decoder=False,
                 pmos_model_choices = 'PMOS_VTG',nmos_model_choices = 'MOS_VTG'
                 ):
        super().__init__(
            nmos_model_name, pmos_model_name,
            base_nmos_width, base_pmos_width, length,
            w_rc=w_rc, pi_res=pi_res, pi_cap=pi_cap,
        )
        self.sweep_decoder=sweep_decoder
        self.pmos_model_choices=pmos_model_choices
        self.nmos_model_choices=nmos_model_choices
        self.REQUIRED_COLUMNS = ['pmos_model_decoder_nandp', 'nmos_model_decoder_nandn']
        # Read model names from parameter file
        self.mos_model_index = self.read_mos_model_from_param_file(self.REQUIRED_COLUMNS)
        self.add_nand2_transistors()


    def add_nand2_transistors(self):
        if not self.sweep_decoder:
            self.M('pnand2_pmos1', 'Z', 'A', 'VDD', 'VDD',
                model=self.pmos_pdk_model,
                w=self.base_pmos_width, l=self.length)
            self.M('pnand2_pmos2', 'Z', 'B', 'VDD', 'VDD',
                model=self.pmos_pdk_model,
                w=self.base_pmos_width, l=self.length)

            self.M('pnand2_nmos1', 'Z', 'B', 'net1_nand', 'VSS',
                model=self.nmos_pdk_model,
                w=self.base_nmos_width, l=self.length)
            self.M('pnand2_nmos2', 'net1_nand', 'A', 'VSS', 'VSS',
                model=self.nmos_pdk_model,
                w=self.base_nmos_width, l=self.length)
        else:
            self.M('pnand2_pmos1', 'Z', 'A', 'VDD', 'VDD',
                model=self.pmos_model_choices[int(self.mos_model_index['pmos'])],
                w='pmos_width_decoder_nandp', l='length_decoder')
            self.M('pnand2_pmos2', 'Z', 'B', 'VDD', 'VDD',
                model=self.pmos_model_choices[int(self.mos_model_index['pmos'])],
                w='pmos_width_decoder_nandp', l='length_decoder')

            self.M('pnand2_nmos1', 'Z', 'B', 'net1_nand', 'VSS',
                model=self.nmos_model_choices[int(self.mos_model_index['nmos'])],
                w='nmos_width_decoder_nandn', l='length_decoder')
            self.M('pnand2_nmos2', 'net1_nand', 'A', 'VSS', 'VSS',
                model=self.nmos_model_choices[int(self.mos_model_index['nmos'])],
                w='nmos_width_decoder_nandn', l='length_decoder')
            
class Pbuff(BaseSubcircuit):  # Buffer composed of two cascaded inverters
    """
    CMOS Buffer (2-stage inverter chain) based on PINV.
    """
    NAME = "PBUFF"
    NODES = ('VDD', 'VSS', 'A', 'Z')

    def __init__(self, nmos_model_name, pmos_model_name,
                 base_pmos_width=1e-07, base_nmos_width=1e-07, length=5e-08,
                 w_rc=False, pi_res=100 @ u_Ohm, pi_cap=0.001 @ u_pF):
        super().__init__(
            nmos_model_name, pmos_model_name,
            base_nmos_width, base_pmos_width, length,
            w_rc=w_rc, pi_res=pi_res, pi_cap=pi_cap,
        )
        # First stage: same as PINV
        self.pmos_width_1 = base_pmos_width
        self.nmos_width_1 = base_nmos_width
        self.pmos_width_2 = base_pmos_width 
        self.nmos_width_2 = base_nmos_width 
        self.add_buffer_transistors()

    def add_buffer_transistors(self):
        # Internal node named Z_int (stage-one output / stage-two input)
        # First-stage inverter: input A, output Z_int
        self.M('buff_pmos_1', 'Z_int', 'A', 'VDD', 'VDD',
               model=self.pmos_pdk_model,
               w=self.pmos_width_1, l=self.length)

        self.M('buff_nmos_1', 'Z_int', 'A', 'VSS', 'VSS',
               model=self.nmos_pdk_model,
               w=self.nmos_width_1, l=self.length)

        # Second-stage inverter: input Z_int, output Z
        self.M('buff_pmos_2', 'Z', 'Z_int', 'VDD', 'VDD',
               model=self.pmos_pdk_model,
               w=self.pmos_width_2, l=self.length)

        self.M('buff_nmos_2', 'Z', 'Z_int', 'VSS', 'VSS',
               model=self.nmos_pdk_model,
               w=self.nmos_width_2, l=self.length)
