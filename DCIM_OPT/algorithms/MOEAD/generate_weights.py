"""
Generate MOEAD weight vector file.
For multiplier problem: 2 objectives, 800 weight vectors (H=799).
"""

import os

from moead_mean_vector import Mean_vector

# Create vector_csv_file directory
csv_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vector_csv_file")
if not os.path.exists(csv_dir):
    os.makedirs(csv_dir)
    print(f"Created directory: {csv_dir}")

# Generate weight vectors
output_path = os.path.join(csv_dir, "multiplier.csv")

print("=" * 70)
print("Generating MOEAD weight vectors")
print("=" * 70)
print("Objectives: 2")
print("Divisions H: 799")
print("Weight vectors: 800 (H+1)")
print(f"Output file: {output_path}")
print("=" * 70)

# H=799 -> generate 800 weight vectors
mv = Mean_vector(H=799, m=2, path=output_path)
weights = mv.generate()

print("=" * 70)
print("Generation complete!")
print("Weight vector samples:")
print(f"  #1:   [{weights[0][0]:.6f}, {weights[0][1]:.6f}]")
print(f"  #200: [{weights[199][0]:.6f}, {weights[199][1]:.6f}]")
print(f"  #400: [{weights[399][0]:.6f}, {weights[399][1]:.6f}]")
print(f"  #600: [{weights[599][0]:.6f}, {weights[599][1]:.6f}]")
print(f"  #800: [{weights[799][0]:.6f}, {weights[799][1]:.6f}]")
print("=" * 70)
