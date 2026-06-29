import argparse
import sys
from pathlib import Path

from nbit_exact import generate_Exact   
from nbit_approx import (
    DEFAULT_CONFIG_DIR,
    generate_Appro_4_2,
    read_compressor_config,
    write_compressor_config_template,
)
from nbit_log import generate_Log


REPO_ROOT = Path(__file__).resolve().parents[2]

# Default settings. Change these values in code instead of typing them at runtime.
DEFAULT_BIT_WIDTH = 8
OUTPUT_DIR = REPO_ROOT / "DCIM" / "multiplier"
GENERATE_EXACT = True
GENERATE_APPROX = True
GENERATE_LOG = True


def parse_args():
    parser = argparse.ArgumentParser(description="Generate exact, approximate, and log multipliers.")
    parser.add_argument(
        "--bit_width",
        type=int,
        nargs="+",
        default=[DEFAULT_BIT_WIDTH],
        help=f"Multiplier bit width(s) to generate. Default: {DEFAULT_BIT_WIDTH}",
    )
    parser.add_argument(
        "--config_dir",
        type=Path,
        default=DEFAULT_CONFIG_DIR,
        help=f"Approximate compressor config directory. Default: {DEFAULT_CONFIG_DIR}",
    )
    parser.add_argument(
        "--init_config",
        action="store_true",
        help="Create approximate compressor config template(s) only, then exit.",
    )
    args = parser.parse_args()

    invalid_bit_widths = [bits for bits in args.bit_width if bits < 1]
    if invalid_bit_widths:
        parser.error(f"Bit width must be positive; invalid values: {invalid_bit_widths}")

    return args


if __name__ == "__main__":
    args = parse_args()
    bit_widths = args.bit_width

    if args.init_config:
        for bits in bit_widths:
            write_compressor_config_template(bits, config_dir=args.config_dir)
        sys.exit(0)

    try:
        compressor_config = {
            bits: read_compressor_config(bits, config_dir=args.config_dir)
            for bits in bit_widths
        }
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    bit_width_label = ", ".join(f"{bits}-bit" for bits in bit_widths)
    print(f"Generating {bit_width_label} multiplier files in: {OUTPUT_DIR}")

    if GENERATE_EXACT:
        generate_Exact(bit_widths, output_dir=OUTPUT_DIR)
    if GENERATE_APPROX:
        generate_Appro_4_2(
            bit_widths,
            compressor_config=compressor_config,
            output_dir=OUTPUT_DIR,
            prompt_for_missing=False,
        )
    if GENERATE_LOG:
        generate_Log(bit_widths, output_dir=OUTPUT_DIR)
