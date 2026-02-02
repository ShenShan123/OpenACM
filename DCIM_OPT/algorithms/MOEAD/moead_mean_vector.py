"""
Mean vector generation utility.
Based on MOEAD-master/src/Mean_Vector_Util.py.
Used to generate evenly distributed weight vectors.
"""

import os

import numpy as np


class Mean_vector:
    """
    Generate weight vectors for multi-objective optimization.
    For 2 objectives: H+1 vectors [(0, 1), (1/H, 1-1/H), ..., (1, 0)].
    """
    def __init__(self, H=99, m=2, path="out.csv"):
        """
        H: divisions (for 2 objectives, generates H+1 vectors)
        m: number of objectives
        path: output path
        """
        self.H = H
        self.m = m
        self.path = path
        self.stepsize = 1 / H

    def perm(self, sequence):
        """Permutations without duplicates."""
        l = sequence
        if len(l) <= 1:
            return [l]
        r = []
        for i in range(len(l)):
            if i != 0 and sequence[i - 1] == sequence[i]:
                continue
            s = l[:i] + l[i + 1:]
            p = self.perm(s)
            for x in p:
                r.append(l[i:i + 1] + x)
        return r

    def get_mean_vectors(self):
        """Generate weight vectors."""
        H = self.H
        m = self.m
        sequence = []

        # Build the sequence for permutations
        for _ in range(H):
            sequence.append(0)
        for _ in range(m - 1):
            sequence.append(1)

        ws = []
        pe_seq = self.perm(sequence)

        for sq in pe_seq:
            s = -1
            weight = []
            for i in range(len(sq)):
                if sq[i] == 1:
                    w = i - s
                    w = (w - 1) / H
                    s = i
                    weight.append(w)
            nw = H + m - 1 - s
            nw = (nw - 1) / H
            weight.append(nw)

            if weight not in ws:
                ws.append(weight)

        return ws

    def save_mv_to_file(self, mv):
        """Save weight vectors to file."""
        f = np.array(mv, dtype=np.float64)
        # Ensure target directory exists when given a relative path
        dir_name = os.path.dirname(os.path.abspath(self.path))
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)
        np.savetxt(fname=self.path, X=f, delimiter=",", fmt="%.6f")
        print(f"Weight vectors saved to: {self.path}")
        print(f"Weight vector count: {len(mv)}")

    def generate(self):
        """Generate and save weight vectors."""
        m_v = self.get_mean_vectors()
        self.save_mv_to_file(m_v)
        return m_v


if __name__ == "__main__":
    # Test: generate 100 weight vectors for 2 objectives
    mv = Mean_vector(H=99, m=2, path="test_weights.csv")
    weights = mv.generate()
    print("Generated weight vector samples:")
    print(f"  #1: {weights[0]}")
    print(f"  #50: {weights[49]}")
    print(f"  #100: {weights[99]}")
