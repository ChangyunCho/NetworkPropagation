import os
from utils import ensure_dir

def _safe_import_gseapy():
    try:
        import gseapy as gp
        return gp
    except Exception as e:
        raise RuntimeError("gseapy is required: %r" % (e,))

def top_n_genes(np_score_tsv, top_n):
    genes = []
    with open(np_score_tsv, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip().split("\t")
            if not s:
                continue
            gene = s[0]
            try:
                score = float(s[1])
            except Exception:
                if gene.lower() == "gene":
                    continue
                continue
            genes.append((gene, score))
    genes.sort(key=lambda x: x[1], reverse=True)
    return [g for g, _ in genes[:top_n]]

def run_reactome_enrich(np_score_tsv, deg_txt, out_dir, top_n=100, organism="Human"):
    gp = _safe_import_gseapy()
    ensure_dir(out_dir)
    genes_top = top_n_genes(np_score_tsv, top_n)
    enr_top = gp.enrichr(
        gene_list=genes_top,
        description=f"Top{top_n}_Reactome",
        gene_sets=["Reactome_2016"],
        organism=organism,
        outdir=out_dir,
        cutoff=1.0,
        no_plot=True,
    )
    df_top = enr_top.results
    top_path = os.path.join(out_dir, f"reactome_top{top_n}.tsv")
    df_top.to_csv(top_path, sep="\t", index=False)
    deg_genes = set()
    with open(deg_txt, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip().split()
            if s:
                deg_genes.add(s[0])
    genes_top_wo_deg = [g for g in genes_top if g not in deg_genes]
    if len(genes_top_wo_deg) == 0:
        df_wo = df_top.iloc[0:0].copy()
        wo_path = os.path.join(out_dir, f"reactome_top{top_n}_noDEG.tsv")
        df_wo.to_csv(wo_path, sep="\t", index=False)
        return
    enr_wo = gp.enrichr(
        gene_list=genes_top_wo_deg,
        description=f"Top{top_n}_noDEG_Reactome",
        gene_sets=["Reactome_2016"],
        organism=organism,
        outdir=out_dir,
        cutoff=1.0,
        no_plot=True,
    )
    df_wo = enr_wo.results
    wo_path = os.path.join(out_dir, f"reactome_top{top_n}_noDEG.tsv")
    df_wo.to_csv(wo_path, sep="\t", index=False)

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--np_scores", required=True)
    p.add_argument("--deg", required=True)
    p.add_argument("--out", default="results/reactome")
    p.add_argument("--topn", type=int, default=100)
    p.add_argument("--organism", default="Human")
    args = p.parse_args()
    run_reactome_enrich(
        np_score_tsv=args.np_scores,
        deg_txt=args.deg,
        out_dir=args.out,
        top_n=args.topn,
        organism=args.organism,
    )
