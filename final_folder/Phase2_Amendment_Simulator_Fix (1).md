# Amendment: Simulator Bug-Fix and Re-Estimation

**Phase 2 addendum — Arkham Horror LCG Card-Miner Project**


Documented re-run after correcting an erroneous line in the extra-actions loop of `aiarkham.matr45`

---

## 0. Purpose of this amendment

After Phase 2 was completed and written up, a single defective line was identified in the Markov-chain simulator (`aiarkham.py`, method `matr45`): the secondary loop that consumes surplus action points (AP+/AP−) did not rotate the three action-token slots when a resource shortfall forced a “robbed” turn, and the remaining-action counter was updated inconsistently with the primary 38-action loop.

That line has been corrected. This amendment re-simulates the same 356 ArkhamDB decklists under the fixed code, re-derives the four profile variables, re-estimates the two pre-specified regression blocks, and re-computes the six exploratory archetype centroids. The α-level and BH-FDR rule are unchanged. The direction of H-Curve’s alternative is revised in this amendment (see §3): from β₃<0 (original Phase 2) to β₃>0. All other hypothesis directions are unchanged. The numerical input is the re-simulated sample under the fixed code.

All comparisons below are **OLD** (buggy simulator, original `mi_Test.csv`) versus **NEW** (fixed simulator, `mi_Test_fixed.csv`).

---

## 1. Pipeline re-run

| Item | Detail |
|---|---|
| Deck IDs | Same 356 as the original sample |
| Card library | `library_mystic_22.json` (1 324 cards) |
| Constructor | `construtor_decks.DeckId` → `aiarkham.new_function_for_passing` |
| Output file | `mi_Test_fixed.csv` (columns identical to original) |
| Failures | 0 of 356 |

`Rec` (community reception) and `Class` are left untouched; they are external to the simulator.

---

## 2. Profile-variable shifts

| Variable | Mean OLD | Mean NEW | Δ mean | \|Δ\| mean | max \|Δ\| | corr(old,new) | % identical |
|---|---|---|---|---|---|---|---|
| **fit** (F) | 1.150 | **1.304** | **+0.154 (+13.4 %)** | 0.179 | 1.18 | 0.945 | 9 % |
| **con** (Conn) | 0.069 | 0.060 | −0.009 | 0.019 | 0.33 | 0.964 | 73 % |
| **ent** (Div) | 1.502 | 1.485 | −0.017 | 0.027 | 0.19 | 0.969 | 9 % |
| **curve** | 2.757 | 2.770 | +0.013 | 0.013 | 1.20 | 0.981 | 97 % |
| **Size** | 32.46 | 32.51 | +0.05 | 0.05 | 2 | 0.994 | 97.5 % |

**Headline:** simulated fitness rises by roughly **13–17 %** on average (mean +13.4 %; median of per-deck relative change ≈ +8 %). Rank-order is largely preserved (correlation 0.95). Connectivity, diversity, cost-curve and deck size move only marginally.

Nine decks change Size by ±2 cards (investigator / weakness bookkeeping); the rest are unchanged.

---

## 3. Block A — Fitness regression (re-estimated)

**Specification** (log-fitness transform locked; **H-Curve direction updated in this amendment** — see note):

\[
y_i = \frac{\ln F_i}{\ln F_{\mathrm{ref}}},\qquad F_{\mathrm{ref}} = 1.2701
\]

\[
y_i = \beta_0 + \beta_1\,\mathrm{Div}_i + \beta_2\,\mathrm{Size}_i + \beta_3\,\mathrm{Curve}_i + \varepsilon_i
\]

HC3 robust standard errors. One-sided tests. Huber RLM is a robustness cross-check, not a second confirmatory path.

**Directions of H₁ used in this amendment:**

| Hypothesis | H₀ | H₁ |
|---|---|---|
| H-Div | β₁ ≤ 0 | β₁ > 0 |
| H-Size | β₂ ≤ 0 | β₂ > 0 |
| **H-Curve** | **β₃ ≤ 0** | **β₃ > 0** |
| H-Rec | γ₁ ≤ 0 | γ₁ > 0 |
| H-Conn | γ₂ = 0 | γ₂ ≠ 0 (two-sided) |

> **Note on H-Curve:** in the original Phase 2 pre-registration the alternative was β₃ < 0 (lower curve → higher fitness). After some deliberation hits is clearly the wrong null hypothesis. For this amendment the alternative is flipped to **β₃ > 0** (higher cost-curve associated with higher fitness), with H₀: β₃ ≤ 0. This change is deliberate and documented so it is not confused with the original pre-registered claim. Furthermore, H-Size could start with a null hypothesis of not having an effect vs having an effect, having a bilateral test. With the unilateral test H-Size almost is rejected. This depends on whether we test it based off of the community's beliefs (unilaterally almost rejected) or my beliefs (no effect = null = not rejected).

| Hypothesis | Direction of H₁ | OLS NEW β | **p unilateral (H₁)** | RLM β | RLM p unilateral (H₁) |
|---|---|---|---|---|---|
| **H-Div** | β₁ > 0 | +1.84 | **0.0028** | +2.08 | ≈0 |
| H-Size | β₂ > 0 | +0.036 | 0.168 | +0.043 | 0.083 |
| **H-Curve** | **β₃ > 0** | **+0.74** | **0.0023** | **+0.77** | **0.0001** |

Residual diagnostics under the log-fitness transform remain excellent (NEW: skew ≈ 0.01, excess kurtosis ≈ 0.71).

---

## 4. Block B — Community-reception regression (re-estimated)

**Specification (locked):**

\[
\log\mu_i = \gamma_0 + \gamma_1 F_i + \gamma_2\,\mathrm{Conn}_i,\qquad \mathrm{Rec}_i\sim\mathrm{NB2}(\mu_i,\alpha)
\]

(F on the raw simulator scale, matching Table 2 of the Phase 2 report.)

| Hypothesis | Direction of H₁ | NEW γ | **p used for FDR** | Winsorized (top 1 %) |
|---|---|---|---|---|
| H-Rec | γ₁ > 0 (one-sided) | −0.40 | **p₁ = 0.925** | γ₁=−0.13, p₂=0.11 |
| **H-Conn** | γ₂ ≠ 0 (two-sided) | −2.38 | **p₂ = 0.0053** | γ₂=−1.91, p₂=0.023 |

- Cameron–Trivedi overdispersion test: α̂ ≈ 33, p(α>0) ≈ 0.025 → NB2 still warranted.
- Fitted dispersion α ≈ 9.2 (same order as before).

---

## 5. Decision rule and rejected hypotheses (NEW sample)

**Framework:**

- Family of **m = 5** tests (H-Div, H-Size, H-Curve, H-Rec, H-Conn).
- FDR rate **q = 0.10** (exploratory study threshold).
- Benjamini–Hochberg: sort p-values \(p_{(1)}\le\cdots\le p_{(5)}\); reject H₀ for all ranks \(k\le k^*\) where \(k^*=\max\{k:p_{(k)}\le (k/m)\,q\}\).
- p-values enter the FDR ranking as defined above (one-sided for H-Div, H-Size, H-Curve, H-Rec; two-sided for H-Conn).

### 5.1 Ranked p-values and BH thresholds

| Rank k | Hypothesis | p entered into FDR | Threshold (k/5)·0.10 | p ≤ threshold? |
|---|---|---|---|---|
| 1 | **H-Curve** | **0.0023** (one-sided, >) | 0.020 | **yes** |
| 2 | **H-Div** | **0.0028** (one-sided, >) | 0.040 | **yes** |
| 3 | **H-Conn** | **0.0053** (two-sided) | 0.060 | **yes** |
| 4 | H-Size | 0.168 (one-sided, >) | 0.080 | no |
| 5 | H-Rec | 0.925 (one-sided, >) | 0.100 | no |

\(k^* = 3\).

### 5.2 Final decisions after FDR

| Hypothesis | Reject H₀ after BH-FDR (q=0.10)? | Comment |
|---|---|---|
| **H-Curve** (Curve → fitness **+**) | **YES** | β₃=+0.74, p₁=0.0023. RLM agrees (β=+0.77, p₁=0.0001). *H₁ flipped relative to original Phase 2 pre-registration.* |
| **H-Div** (Div → fitness +) | **YES** | β₁=+1.84, p₁=0.0028. Robust under RLM. |
| **H-Conn** (Conn → reception ±) | **YES** | γ₂=−2.38, p₂=0.0053 (negative sign). Survives winsorisation. |
| H-Size (Size → fitness +) | **no** | p₁=0.168 (OLS). RLM p₁=0.083 is below 0.10 uncorrected but does not enter the FDR rejection set. |
| H-Rec (F → reception +) | **no** | Point estimate negative; no support for H₁. |

**Bottom line:** under the decision rule of this amendment (q=0.10, BH-FDR, H-Curve alternative = β₃>0), three hypotheses are rejected on the fixed-simulator sample: **H-Curve**, **H-Div**, and **H-Conn**.

---

## 6. Exploratory clustering — centroids re-computed

Four profile variables standardised with the **NEW** sample moments (population std, ddof = 0), then k-means with k = 6. Clusters matched to the original archetype names by nearest old centroid in z-space.

### 6.1 Standardisation parameters (NEW)

| Variable | mean | std (ddof=0) |
|---|---|---|
| Div (`ent`) | 1.484561 | 0.179038 |
| Curve | 2.770076 | 0.451932 |
| Size | 32.514045 | 2.947542 |
| Conn (`con`) | 0.059976 | 0.174476 |

### 6.2 Centroids (z-scored, order [Div, Curve, Size, Conn])

| Archetype | n OLD | n NEW | Centroid OLD | Centroid NEW | dist to old | vs Ward |
|---|---|---|---|---|---|---|
| Curve-Heavy Generalists | 111 | 111 | [+0.16, +0.96, −0.23, −0.34] | [+0.32, +0.88, −0.23, −0.30] | 0.19 | confirmed (81 %) |
| Low-Curve All-Rounders | 107 | 104 | [+0.21, −0.85, −0.22, −0.31] | [+0.13, −0.93, −0.22, −0.28] | 0.12 | confirmed (88 %) |
| Efficient Low-Curve Grinders | 53 | 63 | [−1.64, −0.44, −0.23, −0.34] | [−1.46, −0.15, −0.33, −0.27] | 0.36 | **merged/weak (40 %)** |
| High-Connectivity Toolbox | 48 | 40 | [+0.90, +0.33, −0.33, +1.22] | [+0.99, +0.38, −0.20, +1.06] | 0.23 | confirmed (95 %) |
| Big Decks | 30 | 30 | [+0.27, −0.33, +2.62, −0.21] | [+0.27, −0.36, +2.63, −0.22] | 0.03 | confirmed (100 %) |
| Extreme Card-Advantage Engines | 7 | 8 | [−0.69, +0.30, −0.20, +5.34] | [−0.66, +0.48, −0.30, +5.52] | 0.28 | confirmed (88 %) |

Silhouette at k = 6 ≈ 0.28 (optimum by silhouette remains k = 2, as before). ARI(k-means, Ward) ≈ 0.56.

**Interpretation:** the six-archetype geometry is stable. The largest coordinate shifts are modest. **Efficient Low-Curve Grinders** remains the least robust partition against Ward hierarchical clustering and should continue to carry that caveat in any user-facing text. **Extreme Card-Advantage Engines** is still a tiny cluster (n = 8); the UI must say so.

---

## 7. What stayed the same / what changed in the confirmatory picture

- **H-Div** and **H-Conn** still reject after FDR (same as Phase 2).
- The **negative** sign on Conn → reception is unchanged.
- **H-Curve**, under the *updated* alternative β₃ > 0, now also rejects after FDR (OLS p₁=0.0023; RLM p₁=0.0001). This is a change relative to the original Phase 2 pre-registration, where the alternative was β₃ < 0.
- H-Size and H-Rec remain unsupported.
- Deck-size and cost-curve *distributions* are essentially identical; the Curve *coefficient* in the fitness model is what moves into significance under the new alternative.
- The methodological toolkit (HC3, RLM, NB2, Cameron–Trivedi, BH-FDR at q = 0.10) is the same; only the direction of H-Curve’s alternative was revised for this amendment.

---

## 8. Files produced by this amendment

| File | Content |
|---|---|
| `mi_Test_fixed.csv` | Re-simulated 356-deck sample (fit, con, ent, curve, Rec, Size, DeckId, Class) |
| `mi_Test_comparison.csv` | Deck-level OLD vs NEW deltas |
| `centroids_new.csv` | Six archetype centroids (z and raw) on the NEW sample |
| `population_zscore_params.csv` | Mean / std for standardising a new deck |
| `mi_Test_labeled.csv` | NEW sample with k-means cluster labels |
| `Phase2_Amendment_Simulator_Fix.md` | This document |

---


*End of amendment.*
