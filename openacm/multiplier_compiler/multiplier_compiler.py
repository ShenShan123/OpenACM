import argparse
from pathlib import Path

from nbit_exact import generate_Exact   
from nbit_approx import generate_Appro_4_2
from nbit_log import generate_Log


REPO_ROOT = Path(__file__).resolve().parents[2]

# Default settings. Change these values in code instead of typing them at runtime.
DEFAULT_BIT_WIDTH = 8
OUTPUT_DIR = REPO_ROOT / "DCIM" / "multiplier"
GENERATE_EXACT = True
GENERATE_APPROX = True
GENERATE_LOG = True

# Approximate compressor type mapping:
# 1: ACCI1, 2: kong2, 3: antonio, 4: momeni, 5: ha, 6: akbar1, 7: akbar2, 8: sabetz
# Change the numbers in each list to customize the approximate multiplier.
APPROX_COMPRESSOR_TYPES = {
    8: [
        1, 1, 1, 1, 1, 1, 1, 1, 1,
    ],
    16: [
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1,
    ],
    32: [
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1,
    ],
}


def parse_args():
    parser = argparse.ArgumentParser(description="Generate exact, approximate, and log multipliers.")
    parser.add_argument(
        "--bit_width",
        type=int,
        choices=sorted(APPROX_COMPRESSOR_TYPES),
        default=DEFAULT_BIT_WIDTH,
        help=f"Multiplier bit width to generate. Default: {DEFAULT_BIT_WIDTH}",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    bit_widths = [args.bit_width]

    print(f"Generating {args.bit_width}-bit multiplier files in: {OUTPUT_DIR}")

    if GENERATE_EXACT:
        generate_Exact(bit_widths, output_dir=OUTPUT_DIR)
    if GENERATE_APPROX:
        generate_Appro_4_2(
            bit_widths,
            compressor_config=APPROX_COMPRESSOR_TYPES,
            output_dir=OUTPUT_DIR,
            prompt_for_missing=False,
        )
    if GENERATE_LOG:
        generate_Log(bit_widths, output_dir=OUTPUT_DIR)
