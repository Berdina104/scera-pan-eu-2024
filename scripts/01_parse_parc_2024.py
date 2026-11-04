"""Parse SI-A1 of Meyer et al. 2026 (Water Research 308:127008, doi 10.1016/j.watres.2026.127008): PARC pan-European wastewater campaign, 30 WWTPs, March-Sept 2024.
Reads only the lab-specific 72 h composite blocks (ENV influent 'INF_ENV', effluent 'EFF_ENV'; labs Eawag, UFZ, MUI). The WBE blocks, blanks and the authors' 'averaged' block are not used.
Rules: nothing imputed; '<LOQ'/'<MDL' strings stay censored (value empty, lab limit kept, never zero); a literal 0 in the sheet is flagged censored too (zero_in_source); labs are never averaged (one row per lab x plant x compound x matrix);
statistic = single 72 h composite per plant (one campaign); per-plant removal only where influent and effluent are both quantified by the SAME lab.
Run from the repository root: python -I scripts/01_parse_parc_2024.py
Outputs (data/interim/): pan_eu_2024_tidy.csv, pan_eu_2024_candidates.csv, pan_eu_2024_removal.csv"""
import openpyxl, pandas as pd, numpy as np, re
SRC = "data/raw/parc_2024/mmc1.xlsx"      # supplementary file mmc1.xlsx of the paper, downloaded by the user (see README)
OUT = "data/interim/"
CIT = "Meyer et al. 2026, Water Research 308:127008"; DOI = "10.1016/j.watres.2026.127008"
CTRY = {"AT": "Austria", "BE": "Belgium", "CZ": "Czech Republic", "DK": "Denmark", "FR": "France", "DE": "Germany", "GB": "Great Britain", "IT": "Italy", "NL": "Netherlands", "PL": "Poland", "SK": "Slovakia", "SI": "Slovenia", "ES": "Spain", "SE": "Sweden", "CH": "Switzerland"}
wb = openpyxl.load_workbook(SRC, read_only=True, data_only=True)
rows = list(wb["SI-A1 CompoundsResults"].iter_rows(values_only=True)); hdr = rows[3]
# limits per lab (ng/L): Eawag LOQ_Effluent / LOQ_Influent (cols named), UFZ 'SPE MDL [ng/L]'; MUI gives none in this sheet
ci = {h: i for i, h in enumerate(hdr) if h}
def lim(lab, matrix, r):
    if lab == "Eawag": return r[ci["LOQ_Influent" if matrix == "influent" else "LOQ_Effluent"]]
    if lab == "UFZ": return r[ci["SPE MDL [ng/L]"]]
    return None
pat = re.compile(r"^([A-Z]{2})([12])?_(INF|EFF)_ENV_(Eawag|UFZ|MUI)$")
cols = [(i, pat.match(h)) for i, h in enumerate(hdr) if h and pat.match(h)]
out = []
for r in rows[4:]:
    if not r[1]: continue
    name = str(r[1]).strip(); cas = str(r[7]).strip() if r[7] else ""
    for i, m in cols:
        cc, num, im, lab = m.groups(); v = r[i]
        if v is None: continue
        zero = (not isinstance(v, str)) and float(v) <= 0      # a literal 0 in the sheet is not a measurement (blank-corrected or not detected): treated as censored, never as a value
        censored = isinstance(v, str) or zero
        if isinstance(v, str) and not v.strip().startswith(("<", "below")): continue    # unknown text: skip
        matrix = "influent" if im == "INF" else "effluent"
        out.append(dict(compound=name, cas=cas, therapeutic_class=r[10], parent_or_metabolite=r[13], plant=f"{cc}{num or ''}", country=CTRY[cc], year=2024, matrix=matrix, lab=lab,
                        censored=censored, value_ngL=np.nan if censored else float(v), lab_limit_ngL=lim(lab, matrix, r), censor_text=(v if isinstance(v, str) else "0 in source (not a measurement)") if censored else "", zero_in_source=zero,
                        stat_type="single (72 h composite, one campaign)", source="PARC pan-European campaign SI-A1", citation=CIT, doi=DOI))
t = pd.DataFrame(out); t.to_csv(OUT + "pan_eu_2024_tidy.csv", index=False)
print("tidy rows", len(t), "| plants", t.plant.nunique(), "| compounds", t.compound.nunique(), "| censored", int(t.censored.sum()))
# estrogens present?
print("estrogens in compound list:", sorted(c for c in t.compound.unique() if re.search(r"estr|ethinyl|estron", c, re.I)))

# --- candidates vs river limit (AA-EQS) in Directive 2026/805 (existing thresholds table, keyed on CAS)
th = pd.read_csv("data/inputs/aa_eqs_2026_805.csv")[["key", "substance", "thr_ngL"]].drop_duplicates("key").rename(columns={"substance": "limit_name", "thr_ngL": "river_limit_ngL"})
t["key"] = t.cas
c = t[t.key.isin(th.key)].merge(th, on="key")
e = c[c.matrix == "effluent"].copy()
e["effluent_over_limit"] = e.value_ngL / e.river_limit_ngL
e["limit_can_be_checked"] = (e.lab_limit_ngL.notna()) & (e.lab_limit_ngL < e.river_limit_ngL)       # quantification limit below the river limit
e["lab_limit_known"] = e.lab_limit_ngL.notna()
e.sort_values(["compound", "lab", "plant"]).to_csv(OUT + "pan_eu_2024_candidates.csv", index=False)
print("\nCandidate substances found by CAS:", sorted(e.compound.unique()))
def summ(g):
    q = g[~g.censored]
    return pd.Series(dict(n_plants_measured=g.plant.nunique(), n_quantified=len(q), n_below_limit_of_lab=int(g.censored.sum()), median_ngL=q.value_ngL.median(), min_ngL=q.value_ngL.min(), max_ngL=q.value_ngL.max(),
                          median_over_river_limit=q.effluent_over_limit.median(), plants_above_limit=int((q.effluent_over_limit > 1).sum()), lab_limit_median_ngL=g.lab_limit_ngL.median(), river_limit_ngL=g.river_limit_ngL.iloc[0]))
for scope, d in [("all 15 countries (30 plants)", e)]:
    print("\n==", scope, "(effluent, per lab; never averaged across labs)")
    print(d.groupby(["compound", "lab"]).apply(summ, include_groups=False).round(2).to_string())

# --- per-plant removal, same lab both sides, both quantified (no imputation)
i_ = t[(t.matrix == "influent")].rename(columns={"value_ngL": "c_in", "censored": "cens_in"})[["compound", "cas", "plant", "country", "lab", "c_in", "cens_in"]]
o_ = t[(t.matrix == "effluent")].rename(columns={"value_ngL": "c_out", "censored": "cens_out"})[["compound", "plant", "lab", "c_out", "cens_out"]]
p = i_.merge(o_, on=["compound", "plant", "lab"])
p = p[~p.cens_in & ~p.cens_out & (p.c_in > 0)].copy(); p["removal_pct"] = (p.c_in - p.c_out) / p.c_in * 100
p.to_csv(OUT + "pan_eu_2024_removal.csv", index=False)
k = p[p.cas.isin(th.key)]
print("\n== removal per plant (same lab, both sides quantified), candidate substances")
print(k.groupby(["compound", "lab"]).removal_pct.agg(n="size", median="median", p10=lambda s: s.quantile(.1), p90=lambda s: s.quantile(.9), share_negative=lambda s: (s < 0).mean()).round(1).to_string())
