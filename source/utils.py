import os
import csv

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def read_deg_file(deg_path):
    genes = []
    with open(deg_path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip().split()
            if not s:
                continue
            gene = s[0]
            weight = 1.0
            if len(s) >= 2:
                try:
                    weight = float(s[1])
                except Exception:
                    weight = 1.0
            genes.append((gene, weight))
    return genes

def write_tsv(rows, out_path, header=None):
    ensure_dir(os.path.dirname(out_path) or ".")
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t")
        if header:
            w.writerow(header)
        for r in rows:
            w.writerow(list(r))
