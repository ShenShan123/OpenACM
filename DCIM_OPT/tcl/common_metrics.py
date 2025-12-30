import torch

# Min-Max values for normalization
MIN_MAX_8BIT = {
    'MRED': (0.00086214, 0.15909895),
    'NMED': (0.00009676, 0.00313291),
    'Area': (435.97400000, 480.92800000),
    'Delay': (1.30000000, 1.34000000),
    'Power': (0.00014600, 0.00018400)
}

MIN_MAX_16BIT = {
    'MRED': (0.00000533, 0.00375792),
    'NMED': (0.00000012, 0.00002442),
    'Delay': (1.70, 1.94),
    'Area': (1573.12400000, 1693.35600000),
    'Power': (0.00060700, 0.00088600)
}

def get_min_max(circuit_type='8bit'):
    if circuit_type == '16bit':
        return MIN_MAX_16BIT
    return MIN_MAX_8BIT

def safe_get(value):
    """Safely convert tensor/numpy/float to python float."""
    if hasattr(value, 'item'):
        return float(value.item())
    try:
        return float(value)
    except:
        return value

def normalize(value, key, min_max_dict):
    min_val, max_val = min_max_dict[key]
    if max_val == min_val:
        return 0.0
    val = safe_get(value)
    return (val - min_val) / (max_val - min_val)

def denormalize(value, key, min_max_dict):
    min_val, max_val = min_max_dict[key]
    val = safe_get(value)
    return val * (max_val - min_val) + min_val

def get_pdp_range(min_max_dict):
    """Calculate PDP min/max based on Delay and Power ranges."""
    d_min, d_max = min_max_dict['Delay']
    p_min, p_max = min_max_dict['Power']
    # PDP = Delay * Power * 1e6
    pdp_min = d_min * p_min * 1e6
    pdp_max = d_max * p_max * 1e6
    return pdp_min, pdp_max

def normalize_pdp(delay_raw, power_raw, min_max_dict):
    pdp_raw = safe_get(delay_raw) * safe_get(power_raw) * 1e6
    pdp_min, pdp_max = get_pdp_range(min_max_dict)
    return (pdp_raw - pdp_min) / (pdp_max - pdp_min)
