"""Table 1 + number macros for report/pan_eu_2024_developers.tex, generated from the analysis outputs so every number is exact and reproducible.
Scope: EU member-state plants only (Great Britain and Switzerland excluded: Directive (EU) 2026/805 binds EU member states) = 26 of the 30 PARC plants.
Inputs: data/interim/pan_eu_2024_tidy.csv (scripts/01), pan_eu_2024_candidates.csv. Outputs: report/table1_regulated.tex (complete tabular, \\input outside any tabular), report/pan_eu_2024_numbers.tex (\\newcommand macros used in the text).
Removal columns: (a) plants where influent and effluent are both measurable; (b) bounds that also use plants with a below-detection effluent: lower bound = effluent set to the lab's lowest measurable amount, upper bound = effluent 0
(no single substituted value; the paper's 0.5 x LOQ lies between). Plants with a below-detection or zero INFLUENT are excluded from removal."""
import pandas as pd, numpy as np
A = "data/interim/"
NONEU = ["Great Britain", "Switzerland"]
t = pd.read_csv(A + "pan_eu_2024_tidy.csv"); t = t[~t.country.isin(NONEU)]
c = pd.read_csv(A + "pan_eu_2024_candidates.csv"); c = c[~c.country.isin(NONEU)]
NPL = t.plant.nunique(); NCTRY = t.country.nunique()
def f3(x):   # 3 significant figures, thousands separator
    if pd.isna(x): return "--"
    if x >= 1000: return f"{int(round(x, -len(str(int(x))) + 3)):,}"
    if x >= 100: return f"{x:.0f}"
    return f"{x:#.3g}".rstrip(".")
def f1(x): return "--" if pd.isna(x) else f"{x:.1f}".replace("-", "$-$")
order = [("Diclofenac", 40, "dic"), ("Clarithromycin", 130, "cla"), ("Carbamazepine", 2500, "car"), ("Erythromycin", 500, "ery"), ("Azithromycin", 19, "azi")]
rows, mac = [], {"Nplants": str(NPL), "Nctry": str(NCTRY)}
def removal(n, lab):
    i = t[(t.compound == n) & (t.lab == lab) & (t.matrix == "influent") & ~t.censored & (t.value_ngL > 0)][["plant", "value_ngL"]].rename(columns={"value_ngL": "cin"})
    e = t[(t.compound == n) & (t.lab == lab) & (t.matrix == "effluent")][["plant", "censored", "value_ngL", "lab_limit_ngL"]]
    m = i.merge(e, on="plant"); both = m[~m.censored]
    r = (both.cin - both.value_ngL) / both.cin * 100
    lo = (m.cin - np.where(m.censored, m.lab_limit_ngL, m.value_ngL)) / m.cin * 100      # effluent = lowest measurable amount
    hi = (m.cin - np.where(m.censored, 0.0, m.value_ngL)) / m.cin * 100                  # effluent = 0
    return r, lo, hi
for n, lim, k in order:
    labs = [l for l in ["Eawag", "UFZ"] if not c[(c.compound == n) & (c.lab == l)].empty]
    for j, lab in enumerate(labs):
        g = c[(c.compound == n) & (c.lab == lab)]; q = g[~g.censored]; N = g.plant.nunique(); cens = int(g.censored.sum())
        r, lo, hi = removal(n, lab); L = lab[0].lower()
        first = f"{n} ({lim:,.0f})" if j == 0 else ""
        if len(q):
            R = q.effluent_over_limit
            if len(q) == 1: cc, rr, cs, rs = f"{f3(q.value_ngL.iloc[0])} (n=1)", f"{f3(R.iloc[0])} (n=1)", "n.a.", "n.a."
            else:
                cc = f"{f3(q.value_ngL.median())} [{f3(q.value_ngL.min())}--{f3(q.value_ngL.max())}]"; rr = f"{f3(R.median())} [{f3(R.min())}--{f3(R.max())}]"
                cs = f"{f3(q.value_ngL.mean())} $\\pm$ {f3(q.value_ngL.std(ddof=1))}"; rs = f"{f3(R.mean())} $\\pm$ {f3(R.std(ddof=1))}"
            nab = f"{int((R > 1).sum())}/{N}"
            mac.update({f"{k}MedR{L}": f3(R.median()), f"{k}MinR{L}": f3(R.min()), f"{k}MaxR{L}": f3(R.max()), f"{k}Above{L}": f"{int((R > 1).sum())}/{N}",
                        f"{k}RedMed{L}": f"{100 * (1 - 1 / R.median()):.1f}", f"{k}RedMax{L}": f"{100 * (1 - 1 / R.max()):.1f}"})
        else: cc, rr, cs, rs, nab = "below detection at all plants", "not assessable", "n.a.", "n.a.", "n.a."
        if len(r): mac.update({f"{k}Rem{L}": f1(r.median()), f"{k}RemN{L}": str(len(r))})
        rm = f"{f1(r.median())} [{f1(r.quantile(.1))}; {f1(r.quantile(.9))}] ({len(r)})" if len(r) >= 3 else (f"n={len(r)}, not reported" if len(r) else "--")
        rsd = f"{f1(r.mean())} $\\pm$ {f1(r.std(ddof=1))}" if len(r) >= 3 else "n.a."
        bnd = f"[{f1(np.median(lo))}; {f1(np.median(hi))}] ({len(lo)})" if len(lo) else "--"
        rows.append(" & ".join([first, lab, f"{N} / {cens}", f3(g.lab_limit_ngL.median()), cc, cs, rr, rs, nab, rm, rsd, bnd]) + r" \\" + (r" \cmidrule(l{2pt}r{2pt}){2-12}" if j < len(labs) - 1 else ""))
        if n == "Erythromycin": mac[f"eryNrem{L}"] = str(len(r)); mac[f"eryBelow{L}"] = str(cens)
    rows.append(r"\midrule")
rows.append(r"Ibuprofen (140); estrone (0.36); 17$\beta$-estradiol (0.18); 17$\alpha$-ethinylestradiol (0.017) & \multicolumn{11}{l}{not in the campaign's target list for effluent (no data)} \\")
# lab ratio + azithromycin
for n, k in [("Diclofenac", "dic"), ("Clarithromycin", "cla")]:
    m = c[(c.compound == n) & ~c.censored].groupby("lab").effluent_over_limit.median(); mac[f"{k}LabRatio"] = f"{m['UFZ'] / m['Eawag']:.2f}"
r_, lo_, hi_ = removal("Azithromycin", "Eawag"); mac["aziBndLo"] = f1(np.median(lo_)); mac["aziBndHi"] = f1(np.median(hi_)); mac["aziBndN"] = str(len(lo_))
az = c[c.compound == "Azithromycin"]; mac["aziLOQ"] = f3(az.lab_limit_ngL.median()); mac["aziLOQratio"] = f"{az.lab_limit_ngL.median() / 19:.1f}"
mac["carMaxR"] = f3(c[(c.compound == "Carbamazepine") & ~c.censored].effluent_over_limit.max()); mac["eryMaxR"] = f3(c[(c.compound == "Erythromycin") & ~c.censored].effluent_over_limit.max())
HEAD = r"""\begin{tabular}{@{}>{\raggedright\arraybackslash}p{2.3cm} >{\raggedright\arraybackslash}p{0.9cm} R{1.2cm} R{1.4cm} >{\raggedright\arraybackslash}p{2.4cm} >{\raggedright\arraybackslash}p{2.0cm} >{\raggedright\arraybackslash}p{2.5cm} >{\raggedright\arraybackslash}p{1.8cm} R{1.2cm} >{\raggedright\arraybackslash}p{2.8cm} >{\raggedright\arraybackslash}p{1.9cm} >{\raggedright\arraybackslash}p{2.5cm}@{}}
\toprule
\textbf{Substance (EU river limit, \ngL)} & \textbf{Lab} & \textbf{Plants measured / below detection} & \textbf{Lowest amount the lab can measure (\ngL)} & \textbf{Treated-water concentration (\ngL): median [lowest--highest]} & \textbf{Treated-water concentration (\ngL): mean $\pm$ standard deviation} & \textbf{Ratio of treated-water concentration to EU river limit: median [lowest--highest]} & \textbf{Ratio: mean $\pm$ standard deviation} & \textbf{Plants over the limit (ratio $>$ 1)} & \textbf{Removal (\%), plants measurable on both sides: median [10th--90th percentile] (number of plants)} & \textbf{Removal (\%): mean $\pm$ standard deviation} & \textbf{Removal (\%), also counting below-detection plants: median [lower bound; upper bound] (number of plants)} \\
\midrule
"""
open("report/table1_regulated.tex", "w", encoding="utf-8").write(HEAD + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")
open("report/pan_eu_2024_numbers.tex", "w", encoding="utf-8").write("".join(f"\\newcommand{{\\{k}}}{{{v}}}\n" for k, v in mac.items()))
print(NPL, "plants,", NCTRY, "countries;", sorted(t.country.unique()))
print("\n".join(rows)); print(mac)
