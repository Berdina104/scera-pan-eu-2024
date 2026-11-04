# Regulated pharmaceuticals in municipal wastewater effluent vs. EU river limits (2024 data)

Code and generated note behind the two-page technical note `report/pan_eu_2024_developers.pdf`.
It compares the concentrations of five pharmaceuticals in treated wastewater at 26 municipal plants in 13 EU member states (sampled March-September 2024)
with the annual-average river limits in Directive (EU) 2026/805, and reports per-plant removal. Screening-level analysis: treated water is compared with an in-river limit without dilution.

## Data
| What | Where it comes from | In this repository? |
|---|---|---|
| Measured concentrations | Meyer et al. (2026), *Water Research* 308:127008, [doi:10.1016/j.watres.2026.127008](https://doi.org/10.1016/j.watres.2026.127008), supplementary file `mmc1.xlsx` (SI-A1), open access (CC BY) | **No.** Download it yourself (below) |
| EU river limits (AA-EQS) | Directive (EU) 2026/805, OJ L, 20.4.2026, annex (transcribed) | Yes: `data/inputs/aa_eqs_2026_805.csv` |

## Reproduce
1. Python (tested with 3.14) and, for the PDF, a LaTeX installation with `latexmk`.
2. Download the supplementary file of the paper (article page -> "Appendix A. Supplementary data" -> `...-mmc1.xlsx`) and save it as `data/raw/parc_2024/mmc1.xlsx`.
3. Run:
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -I scripts/01_parse_parc_2024.py          # tidy table of all results, per lab and plant -> data/interim/
python -I scripts/02_table1_developer_note.py    # Table 1 + numbers used in the text -> report/table1_regulated.tex, report/pan_eu_2024_numbers.tex
cd report && latexmk -pdf pan_eu_2024_developers.tex
```
Every number in the note comes from the generated files; nothing is typed by hand.

## Main choices (details in `METHODS.md`)
- Only the 26 plants in EU member states are used (the 4 plants in Great Britain and Switzerland are excluded).
- The two laboratories (Eawag, UFZ) are reported separately and never averaged.
- Below-detection results are never replaced by a number; a literal 0 in the spreadsheet is treated as not detected.
- Removal is calculated per plant from the same laboratory's influent and effluent; the paper's own removal values (which substitute half the detection limit) are not used. Plants with below-detection treated water are covered by lower/upper bounds.

## Limitations
One sampling campaign per plant (three-day composites), municipal plants only, effluent compared with a river limit, no information on which plant uses which process, values not cross-checked against the paper's figures.

## License
Code: MIT (see `LICENSE`). The data are not redistributed; please cite the paper and the Directive.
