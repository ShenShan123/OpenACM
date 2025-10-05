from nbit_exact import generate_Exact   
from nbit_approx import generate_Appro_4_2
from nbit_log import generate_Log
if __name__ == "__main__":
    
    bit_widths = [8, 16, 32]
    generate_Exact(bit_widths)
    generate_Appro_4_2(bit_widths)
    generate_Log(bit_widths)
