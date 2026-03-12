# africa-growth-determinants
# 📊 Determinants of Economic Growth in Africa
### Panel Fixed-Effects Econometric Analysis | Python

> **Does public debt really hold back growth in Africa?**
> This study uses 25 years of macroeconomic panel data across 20 African countries to answer this question rigorously.

---

## 👤 Author

**Stephane GANHI** — Senior Data Analyst & Economic Reform Specialist
CEPICI (Investment Promotion Center of Côte d'Ivoire)

📧 stephaneganhi@hotmail.com · 🔗 linkedin.com/in/stephane-ganhi-3482bb1a7 · 📍 Abidjan, Côte d'Ivoire

---

## 📋 Table of Contents

- [Context & Motivation](#-context--motivation)
- [Data](#-data)
- [Methodology](#-methodology)
- [Results](#-results)
- [Visualizations](#-visualizations)
- [Policy Implications](#-policy-implications)
- [Limitations](#-limitations)
- [How to Run](#-how-to-run)
- [Project Structure](#-project-structure)

---

## 🌍 Context & Motivation

African economies face a critical policy dilemma: **invest more to grow, or control debt and inflation first?**

This study applies panel econometrics to quantify the **actual magnitude and statistical significance** of four macroeconomic variables on GDP growth across 20 African countries over 25 years (2000–2024).

The goal is not only academic — the findings carry direct implications for economic reform agendas tracked by institutions like the **World Bank, IFC, AfDB, and IMF**.

---

## 📦 Data

| Variable | Source | Description |
|---|---|---|
| `growth` | World Bank (WDI) | GDP annual growth rate (%) |
| `inflation` | World Bank (WDI) | Consumer price inflation (%) |
| `investment` | World Bank (WDI) | Gross capital formation (% of GDP) |
| `population` | World Bank (WDI) | Population growth rate (%) |
| `debt` | IMF (WEO) | General government gross debt (% of GDP) |

**Panel structure:**
- 🌍 **20 African countries** 
- 📅 **25 years** of observations
- 📊 **398 usable observations** (after cleaning)

> ⚠️ **Data files not included** in this repository due to size and licensing.
> Download directly from:
> - [World Bank Open Data](https://data.worldbank.org/)
> - [IMF World Economic Outlook Database](https://www.imf.org/en/Publications/WEO)
>
> Place all `.xls` files in the root folder before running the script.

---

## 🔬 Methodology

### Model Specification

The study uses a **Panel OLS model with country fixed effects**:

$$\text{Growth}_{it} = \alpha_i + \beta_1 \cdot \text{Debt}_{it} + \beta_2 \cdot \text{Inflation}_{it} + \beta_3 \cdot \text{Investment}_{it} + \beta_4 \cdot \text{Population}_{it} + \varepsilon_{it}$$

Where:
- $\alpha_i$ = country fixed effects (absorbs time-invariant heterogeneity)
- $i$ = country, $t$ = year
- Variables are **standardized** (StandardScaler) to make coefficients directly comparable

### Econometric Diagnostics

| Test | Purpose | Result |
|---|---|---|
| **VIF** | Multicollinearity detection | ✅ All VIF < 1.10 — no problem |
| **Breusch-Pagan** | Heteroscedasticity | ⚠️ Detected → corrected with clustered SE |
| **F-test for Poolability** | Justifies fixed effects | ✅ p < 0.0001 — fixed effects valid |
| **Residual analysis** | Model fit diagnostics | Q-Q plot, fitted vs residuals |

### Why Fixed Effects?

The F-test for Poolability rejects pooled OLS at p < 0.0001, confirming that **country-specific characteristics** (institutions, geography, historical factors) significantly affect growth and must be controlled for.

### Why Clustered Standard Errors?

The Breusch-Pagan test confirms heteroscedasticity (p < 0.0001), meaning error variance is not constant across countries. **Clustering at the country level** provides robust inference.

---

## 📈 Results

### Main Findings — African Sample (Standardized Data)

| Variable | Coefficient | Std. Error | p-value | Significance |
|---|---|---|---|---|
| **Public Debt** | **−1.3256** | 0.3569 | 0.0002 | *** |
| **Inflation** | **−0.8011** | 0.1814 | < 0.0001 | *** |
| Investment | +0.2651 | 0.3327 | 0.4260 | — |
| Demographics | +0.0946 | 0.4453 | 0.8319 | — |

`*** p<0.01 · ** p<0.05 · * p<0.1`

**Model Statistics:**

| Metric | Value |
|---|---|
| R² within | 0.0985 |
| R² between | −0.4985 |
| R² overall | 0.0463 |
| F-statistic | 10.21 |
| p-value (F) | < 0.0001 |
| Observations | 398 |
| Countries | 20 |

### Estimated Equation

```
Growth_GDP = 4.27 − 1.33·Public_Debt − 0.80·Inflation + 0.27·Investment + 0.09·Demographics
```

### Hypothesis Testing

| Hypothesis | Result |
|---|---|
| H1: Public debt suppresses growth | ✅ **Confirmed** — negative, p = 0.0002 |
| H2: Investment boosts growth | ⚠️ Partially confirmed — positive but not significant |
| H3: Inflation hurts growth | ✅ **Confirmed** — negative, p < 0.0001 |
| H4: Demographics drive growth | ⚠️ Partially confirmed — positive but not significant |

### Key Interpretation

- A **1 standard deviation increase in public debt** → GDP growth reduced by **1.33 percentage points**
- A **1 standard deviation increase in inflation** → GDP growth reduced by **0.80 percentage points**
- **Investment and demographics** point in the expected positive direction but are not statistically isolated — likely absorbed by cross-country heterogeneity

> 💡 **The counter-intuitive finding:** Investment is not the binding constraint in the short run. **Macroeconomic stability** — controlling debt and inflation — is the primary driver of growth variation across African countries in this dataset.

---

## 📊 Visualizations

### Figure 1 — Coefficients with Confidence Intervals
![Coefficients](fig1_coefficients.png)
<img width="3567" height="2369" alt="linkedin_coefficients" src="https://github.com/user-attachments/assets/238f3232-e7c5-4d97-9dc4-d46595eb9209" />


*Red bars = statistically significant (p < 0.05) · Grey bars = not significant*

### Figure 2 — Public Debt vs. GDP Growth
![Dette vs Croissance](fig2_dette_croissance.png)
<img width="1000" height="600" alt="Figure_1" src="https://github.com/user-attachments/assets/4a2f6810-a401-43af-9019-351616d710ed" />


*Negative relationship clearly visible — confirmed by the regression line (slope = −0.02, p < 0.01)*

### Figure 3 — Correlation Matrix
![Correlation](fig3_correlation.png)
<img width="2565" height="2366" alt="linkedin_correlation" src="https://github.com/user-attachments/assets/4bc2e1a8-16f9-4763-85f1-407543d1e1b2" />


*Low inter-variable correlations confirm absence of multicollinearity (all VIF < 1.10)*

---

## 🏛️ Policy Implications

Based on the empirical findings, three priorities emerge for African policymakers:

**1️⃣ Debt Sustainability Before Fiscal Expansion**
High debt levels significantly constrain growth. Fiscal consolidation and debt restructuring should precede expansionary programs to unlock the growth dividend.

**2️⃣ Monetary Stability as a Growth Enabler**
Inflation is the second most powerful growth suppressor in this model. Strengthening central bank independence and inflation-targeting frameworks is not a luxury — it is a prerequisite for growth.

**3️⃣ Condition Investment on Macro Stability**
Investment spending must be directed toward high-multiplier sectors (infrastructure, human capital) and conditioned on macroeconomic stability to generate statistically detectable growth effects.

---

## ⚠️ Limitations

- **Sample size:** Only 20 African countries had sufficient data coverage for the analysis
- **Threshold effects:** The model assumes linearity — non-linear debt effects (e.g., Reinhart-Rogoff threshold) are not captured
- **Institutional variables:** Absence of governance indicators (Mo Ibrahim, CPIA) as controls
- **Endogeneity:** Some reverse causality between growth and investment may exist
- **Data coverage:** Missing values required dropping observations (81.6% of merged data retained)

---

## 🚀 How to Run

### Prerequisites

```bash
pip install pandas numpy matplotlib seaborn scipy statsmodels linearmodels openpyxl scikit-learn
```

### Setup

```bash
# Clone the repository
git clone https://github.com/StephaneGanhi/africa-growth-determinants.git
cd africa-growth-determinants

# Download data files from World Bank & IMF (see Data section)

# Place all .xls files in the root folder

# Run the analysis
python growthAnalysis.py
```

### Expected Outputs

```
africa-growth-determinants/
├── fig1_coefficients.png       ← Coefficient plot
├── fig2_dette_croissance.png   ← Debt vs Growth scatter
├── fig3_correlation.png        ← Correlation matrix
├── resultats_modele.csv        ← Results table (CSV)
└── resultats_complets.xlsx     ← Full results (Excel)
```

---

## 📁 Project Structure

```
africa-growth-determinants/
│
├── growthAnalysis.py           ← Main analysis script (production-ready)
├── README.md                   ← This file
│
├── data/                       ← Place your .xls files here (not included)
│   ├── gdp_annual_growth.xls
│   ├── inflation_consumer_price.xls
│   ├── gross_capital_formation_investment.xls
│   ├── population_growth_annual%.xls
│   └── government_general_gross_debt_%gdp.xls
│
├── outputs/                    ← Generated automatically
│   ├── fig1_coefficients.png
│   ├── fig2_dette_croissance.png
│   ├── fig3_correlation.png
│   ├── resultats_modele.csv
│   └── resultats_complets.xlsx
│
└── visuals/                    ← Pre-generated visuals for reference
    └── dette_publique_et_croissance.png
```

---

## 📚 References

- Reinhart, C. & Rogoff, K. (2010). *Growth in a Time of Debt*. American Economic Review.
- Arellano, M. & Bond, S. (1991). *Some Tests of Specification for Panel Data*. Review of Economic Studies.
- World Bank (2024). *World Development Indicators*. Washington D.C.
- IMF (2024). *World Economic Outlook Database*. Washington D.C.
- Mo Ibrahim Foundation (2024). *Ibrahim Index of African Governance*.

---

## 📄 License

This project is licensed under the **MIT License** — free to use, adapt and share with attribution.

---

## 🤝 Contact & Collaboration

Interested in collaborating on data analysis, economic modeling, or business climate reform studies in Africa?

📧 **Stephane GANHI**
🔗 **linkedin.com/in/stephane-ganhi-3482bb1a7**
📍 **Abidjan, Côte d'Ivoire**

*Open to: consulting missions · research collaboration · institutional partnerships*

---

<div align="center">

⭐ **If this study was useful, please star the repository** ⭐

*Made with Python · pandas · statsmodels · linearmodels*

</div>
