import os
import argparse
from NP import Walker
from utils import ensure_dir, write_tsv

def run_network_propagation(ppi_path, deg_path, out_path, restart_prob=0.1, normalize=False, constant_weight=False, absolute_weight=False, add_bidirectional_edge=False):
    ensure_dir(os.path.dirname(out_path) or ".")
    wk = Walker(
        original_ppi=ppi_path,
        low_list=[],
        remove_nodes=[],
        constantWeight=bool(constant_weight),
        absWeight=bool(absolute_weight),
        addBidirectionEdge=bool(add_bidirectional_edge),
    )
    seed2weight = {}
    with open(deg_path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip().split()
            if not s:
                continue
            gene = s[0]
            w = 1.0
            if len(s) >= 2:
                try:
                    w = float(s[1])
                except ValueError:
                    continue
            seed2weight[gene] = w
    results = wk.run_exp(
        seed2weight=seed2weight,
        restart_prob=restart_prob,
        og_prob=None,
        normalize=bool(normalize),
    )
    rows = ((gene, score) for gene, score, _trace in results)
    write_tsv(rows, out_path, header=["Gene", "NP_Score"])

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ppi", default=os.path.join("..", "network", "ppi.tsv"))
    ap.add_argument("--deg", default=os.path.join("..", "DEGs", "deg.txt"))
    ap.add_argument("--out", default=os.path.join("..", "results", "np_scores.tsv"))
    ap.add_argument("--restart", type=float, default=0.1)
    ap.add_argument("--normalize", action="store_true")
    ap.add_argument("--constant_weight", action="store_true")
    ap.add_argument("--absolute_weight", action="store_true")
    ap.add_argument("--add_bidir", action="store_true")
    args = ap.parse_args()
    run_network_propagation(
        ppi_path=args.ppi,
        deg_path=args.deg,
        out_path=args.out,
        restart_prob=args.restart,
        normalize=args.normalize,
        constant_weight=args.constant_weight,
        absolute_weight=args.absolute_weight,
        add_bidirectional_edge=args.add_bidir,
    )
