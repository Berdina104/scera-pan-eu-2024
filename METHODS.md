# Methods

**Source.** Supplementary file SI-A1 of Meyer et al. (2026), sheet `SI-A1 CompoundsResults`: concentrations (ng/L) of 419 compounds in influent and effluent of 30 municipal wastewater treatment plants (two per country, 15 countries), 72 h composite samples, March-September 2024, analysed by three laboratories (Eawag, UFZ, MUI). We use only the laboratory-specific 72 h composite blocks (`*_INF_ENV_*`, `*_EFF_ENV_*`); the blocks for wastewater-based epidemiology, blanks and the authors' averaged values are not used.

**Plants.** Directive (EU) 2026/805 applies to EU member states, so the two plants each in Great Britain and Switzerland are excluded: 26 plants in 13 countries remain (AT, BE, CZ, DK, FR, DE, IT, NL, PL, SK, SI, ES, SE).

**Limits.** Annual-average environmental quality standards (AA-EQS) for inland surface water from the annex of Directive (EU) 2026/805 (`data/inputs/aa_eqs_2026_805.csv`, matched to the data by CAS number): diclofenac 40, clarithromycin 130, carbamazepine 2,500, erythromycin 500, azithromycin 19 ng/L (ibuprofen, estrone, estradiol and ethinylestradiol are regulated but not in the campaign's effluent target list). These are in-stream standards, not effluent limits; no dilution is applied.

**Ratio.** Per plant and laboratory: ratio = effluent concentration / AA-EQS. Table 1 gives median [lowest-highest] and mean +/- sample standard deviation (n-1) over the plants where the substance was measurable.

**Below detection.** Results given as "<LOQ" or "<MDL" are censored: never set to zero or a fraction of the limit. A censored result counts as "at or below the limit" only if the laboratory's own limit (Eawag: limit of quantification in the matrix; UFZ: SPE method detection limit) is below the EU limit; otherwise it is undetermined (azithromycin: Eawag limit of about 775 ng/L vs. EU limit 19 ng/L). MUI gives no limit in this sheet and is not used in the table. A literal 0 in the spreadsheet is treated as not detected (our reading; the authors do not state what a 0 means).

**Removal.** Per plant and laboratory: (influent - effluent)/influent x 100, both measurable (plants with below-detection or zero influent are excluded). Reported as median [10th; 90th percentile] and mean +/- SD. Because leaving out plants whose effluent is below detection biases removal low, a second version counts those plants with a lower bound (effluent set to the laboratory's limit) and an upper bound (effluent set to 0) and reports the median of each bound. No single substituted value is used (the paper substitutes half the limit, which lies between the bounds). For diclofenac, clarithromycin, carbamazepine and erythromycin the bounds equal the measured median; for azithromycin they span -77.8 % to 100 %.

**Required reduction.** For a ratio R > 1 the effluent concentration must fall by at least 1 - 1/R to reach the limit without dilution (simple arithmetic; with a dilution factor D the requirement is R/D <= 1).

**Not done.** No cross-check against the paper's figures; no information on the treatment process of individual plants (the paper classifies the 30 plants as 26 conventional activated sludge, 3 sequencing batch reactors and 1 trickling filter, and the mapping is not in the SI); no unregulated substances.
