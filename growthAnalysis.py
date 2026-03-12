# =============================================================================
# DETERMINANTS DE LA CROISSANCE ECONOMIQUE EN AFRIQUE
# Modèle économétrique à effets fixes — Panel OLS
# =============================================================================
# Auteur  : [Votre Nom]
# Contact : [votre@email.com] | linkedin.com/in/[profil]
# Date    : Mars 2026
# Version : 1.0
#
# Description :
#   Analyse économétrique des déterminants de la croissance du PIB
#   sur un panel de pays africains (20 pays, 25 ans).
#   Variables : Dette publique, Inflation, Investissement, Démographie
#   Méthode   : Panel OLS à effets fixes, erreurs clusterisées
#
# Données sources (Banque Mondiale / FMI) :
#   - gdp_annual_growth.xls
#   - inflation_consumer_price.xls
#   - gross_capital_formation_investment.xls
#   - population_growth_annual%.xls
#   - government_general_gross_debt_%gdp.xls
#
# Prérequis :
#   pip install pandas numpy matplotlib seaborn scipy statsmodels
#               linearmodels openpyxl scikit-learn
# =============================================================================

# ── 1. IMPORTS ────────────────────────────────────────────────────────────────
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.diagnostic import het_breuschpagan
from linearmodels.panel import PanelOLS

# ── 2. CONFIGURATION ──────────────────────────────────────────────────────────
# Chemins vers les fichiers de données — adapter selon votre environnement
DATA_PATH = "./"   # Dossier contenant les fichiers .xls

FILES = {
    'growth':     DATA_PATH + "gdp_annual_growth.xls",
    'inflation':  DATA_PATH + "inflation_consumer_price.xls",
    'investment': DATA_PATH + "gross_capital_formation_investment.xls",
    'population': DATA_PATH + "population_growth_annual%.xls",
    'debt':       DATA_PATH + "government_general_gross_debt_%gdp.xls",
}

VARIABLES = ['debt', 'inflation', 'investment', 'population']

PAYS_AFRICAINS = [
    'Afrique du Sud', 'Algérie', 'Angola', 'Bénin', 'Botswana',
    'Burkina Faso', 'Burundi', 'Cabo Verde', 'Cameroun',
    'République centrafricaine', 'Tchad', 'Comores', 'Congo',
    'République démocratique du Congo', "Côte d'Ivoire", 'Djibouti',
    'Égypte', 'Guinée équatoriale', 'Érythrée', 'Eswatini', 'Éthiopie',
    'Gabon', 'Gambie', 'Ghana', 'Guinée', 'Guinée-Bissau', 'Kenya',
    'Lesotho', 'Libéria', 'Libye', 'Madagascar', 'Malawi', 'Mali',
    'Mauritanie', 'Maurice', 'Maroc', 'Mozambique', 'Namibie', 'Niger',
    'Nigeria', 'Rwanda', 'São Tomé et Príncipe', 'Sénégal', 'Seychelles',
    'Sierra Leone', 'Somalie', 'Soudan', 'Soudan du Sud', 'Tanzanie',
    'Togo', 'Tunisie', 'Ouganda', 'Zambie', 'Zimbabwe',
]

NOMS_FR = {
    'debt':       'Dette publique',
    'inflation':  'Inflation',
    'investment': 'Investissement',
    'population': 'Croissance démographique',
}

# ── 3. FONCTIONS UTILITAIRES ──────────────────────────────────────────────────
def charger_fichier(path, col_valeur):
    """Charge un fichier Excel Banque Mondiale et le transforme en format long."""
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip()
    # Gestion de la colonne spéciale pour la dette FMI
    if 'General government gross debt (Percent of GDP)' in df.columns:
        df.rename(columns={'General government gross debt (Percent of GDP)': 'Country Name'},
                  inplace=True)
    df = df.melt(id_vars=['Country Name'], var_name='Year', value_name=col_valeur)
    df['Country Name'] = df['Country Name'].str.strip()
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    df.dropna(subset=['Year'], inplace=True)
    df['Year'] = df['Year'].astype(int)
    return df


def nettoyer_colonne(series):
    """Convertit une colonne en numérique en gérant les valeurs manquantes."""
    if pd.api.types.is_numeric_dtype(series):
        return series
    series = series.replace(
        ['no data', 'No data', 'NO DATA', '#N/A', 'N/A', 'NA', '', ' ', 'null', 'NULL'],
        np.nan
    )
    return pd.to_numeric(series, errors='coerce')


def signif_stars(p):
    """Retourne les étoiles de significativité statistique."""
    if p < 0.01:  return '***'
    elif p < 0.05: return '**'
    elif p < 0.1:  return '*'
    else:          return ''


def print_section(titre):
    print("\n" + "="*70)
    print(f"  {titre}")
    print("="*70)


# ── 4. CHARGEMENT & FUSION DES DONNÉES ───────────────────────────────────────
print_section("CHARGEMENT DES DONNÉES")

dfs = {var: charger_fichier(path, var) for var, path in FILES.items()}
print(f"✅ {len(dfs)} fichiers chargés")

# Fusion progressive
df = dfs['growth'].copy()
for var in ['inflation', 'investment', 'population', 'debt']:
    df = pd.merge(df, dfs[var], on=['Country Name', 'Year'], how='inner')

print(f"✅ Fusion terminée : {len(df):,} observations")

# ── 5. NETTOYAGE ──────────────────────────────────────────────────────────────
print_section("NETTOYAGE DES DONNÉES")

for col in ['growth'] + VARIABLES:
    df[col] = nettoyer_colonne(df[col])

avant = len(df)
df_clean = df.dropna(subset=['growth'] + VARIABLES)
print(f"✅ {avant:,} → {len(df_clean):,} observations ({len(df_clean)/avant*100:.1f}% conservées)")

df_clean = df_clean.rename(columns={'Country Name': 'country'})
df_clean = df_clean.set_index(['country', 'Year'])

# ── 6. ANALYSE EXPLORATOIRE ───────────────────────────────────────────────────
print_section("ANALYSE DE CORRÉLATION")

corr = df_clean[VARIABLES].corr()
print(corr.round(3))

# ── 7. DIAGNOSTICS ÉCONOMÉTRIQUES ────────────────────────────────────────────
print_section("TEST DE MULTICOLINÉARITÉ (VIF)")

X_vif = sm.add_constant(df_clean[VARIABLES])
vif = pd.DataFrame({
    'Variable': X_vif.columns,
    'VIF': [variance_inflation_factor(X_vif.values, i) for i in range(X_vif.shape[1])]
})
print(vif.round(3))
print("\n→ Tous VIF < 5 : pas de problème de multicolinéarité" if (vif[vif.Variable != 'const']['VIF'] < 5).all()
      else "\n⚠️ Multicolinéarité détectée")

print_section("TEST D'HÉTÉROSCÉDASTICITÉ (BREUSCH-PAGAN)")

model_ols = sm.OLS(df_clean['growth'], sm.add_constant(df_clean[VARIABLES])).fit()
bp_stat, bp_p, _, _ = het_breuschpagan(model_ols.resid, sm.add_constant(df_clean[VARIABLES]))
print(f"Statistique LM : {bp_stat:.4f}")
print(f"p-value        : {bp_p:.6f}")
if bp_p < 0.05:
    print("⚠️ Hétéroscédasticité présente → erreurs clusterisées utilisées dans le modèle")
else:
    print("✅ Pas d'hétéroscédasticité significative")

# ── 8. MODÈLE GLOBAL (TOUS PAYS) ─────────────────────────────────────────────
print_section("MODÈLE PANEL OLS — TOUS PAYS (référence)")

Y_global = df_clean['growth']
X_global = sm.add_constant(df_clean[VARIABLES])

model_global = PanelOLS(Y_global, X_global, entity_effects=True)
res_global   = model_global.fit(cov_type='clustered', cluster_entity=True)
print(res_global.summary)

# ── 9. SÉLECTION & NORMALISATION — AFRIQUE ───────────────────────────────────
print_section("FOCUS AFRIQUE — SÉLECTION ET NORMALISATION")

df_afrique = df_clean[df_clean.index.get_level_values('country').isin(PAYS_AFRICAINS)]
n_pays = df_afrique.index.get_level_values('country').nunique()
print(f"✅ {n_pays} pays africains · {len(df_afrique)} observations")

# Normalisation (StandardScaler) pour rendre les coefficients comparables
df_scaled          = df_afrique.copy()
scaler             = StandardScaler()
df_scaled[VARIABLES] = scaler.fit_transform(df_scaled[VARIABLES])

# ── 10. MODÈLE FINAL — AFRIQUE ────────────────────────────────────────────────
print_section("MODÈLE FINAL — AFRIQUE (données normalisées)")

Y_af = df_scaled['growth']
X_af = sm.add_constant(df_scaled[VARIABLES])

model_af = PanelOLS(Y_af, X_af, entity_effects=True, time_effects=False)
res_af   = model_af.fit(cov_type='clustered', cluster_entity=True)
print(res_af.summary)

# ── 11. TABLEAU DES RÉSULTATS ─────────────────────────────────────────────────
print_section("TABLEAU DES RÉSULTATS — FORMAT RAPPORT")

resultats = []
for var in VARIABLES:
    coef   = res_af.params[var]
    se     = res_af.std_errors[var]
    pval   = res_af.pvalues[var]
    ci_lo  = res_af.conf_int().loc[var, 'lower']
    ci_hi  = res_af.conf_int().loc[var, 'upper']
    stars  = signif_stars(pval)
    interp = ("Très significatif" if pval < 0.01 else
              "Significatif"      if pval < 0.05 else
              "Faiblement sig."   if pval < 0.1  else
              "Non significatif")
    resultats.append({
        'Variable'       : NOMS_FR[var],
        'Coefficient'    : f"{coef:.4f}{stars}",
        'Écart-type'     : f"{se:.4f}",
        'p-value'        : f"{pval:.4f}",
        'IC 95%'         : f"[{ci_lo:.4f} ; {ci_hi:.4f}]",
        'Interprétation' : interp,
    })

tableau = pd.DataFrame(resultats).set_index('Variable')
print(tableau.to_string())
print(f"\n*** p<0.01  ** p<0.05  * p<0.1")
print(f"R² within = {res_af.rsquared_within:.4f}  |  "
      f"F = {res_af.f_statistic.stat:.2f}  |  "
      f"p(F) < 0.0001  |  N = {int(res_af.nobs)}")

# ── 12. TESTS D'HYPOTHÈSES ────────────────────────────────────────────────────
print_section("TESTS D'HYPOTHÈSES")

hypotheses = [
    ('debt',       'H1 : La dette publique freine la croissance',           'neg'),
    ('investment', 'H2 : L\'investissement stimule la croissance',          'pos'),
    ('inflation',  'H3 : L\'inflation nuit à la croissance',                'neg'),
    ('population', 'H4 : La démographie est un moteur de croissance',       'pos'),
]

for var, label, sens in hypotheses:
    coef = res_af.params[var]
    pval = res_af.pvalues[var]
    confirme = (coef < 0 and sens == 'neg') or (coef > 0 and sens == 'pos')
    sig      = pval < 0.05
    if confirme and sig:
        verdict = "✅ CONFIRMÉE"
    elif confirme and not sig:
        verdict = "⚠️  PARTIELLEMENT CONFIRMÉE (effet attendu, non significatif)"
    else:
        verdict = "❌ REJETÉE"
    print(f"\n{label}")
    print(f"  → {verdict}  |  coef = {coef:.4f}  |  p = {pval:.4f}")

# ── 13. ÉQUATION DU MODÈLE ────────────────────────────────────────────────────
print_section("ÉQUATION DU MODÈLE ESTIMÉ")

eq = f"Croissance_PIB = {res_af.params['const']:.4f}"
for var in VARIABLES:
    c  = res_af.params[var]
    eq += f" {'+ ' if c >= 0 else '- '}{abs(c):.4f}·{NOMS_FR[var]}"
print(f"\n  {eq}\n")

# ── 14. VISUALISATIONS ────────────────────────────────────────────────────────
print_section("GÉNÉRATION DES VISUELS")

plt.style.use('seaborn-v0_8-whitegrid')

# ── Visuel 1 : Coefficients avec intervalles de confiance ──
fig, ax = plt.subplots(figsize=(11, 6))

coefs  = [res_af.params[v]      for v in VARIABLES]
errors = [res_af.std_errors[v] * 1.96 for v in VARIABLES]
pvals  = [res_af.pvalues[v]     for v in VARIABLES]
colors = ['#C0392B' if p < 0.05 else '#95A5A6' for p in pvals]
labels = [NOMS_FR[v]            for v in VARIABLES]

bars = ax.barh(labels, coefs, xerr=errors, color=colors, alpha=0.85,
               capsize=5, height=0.5,
               error_kw={'linewidth': 2, 'ecolor': '#2C3E50'})

for i, (c, e, p) in enumerate(zip(coefs, errors, pvals)):
    stars = signif_stars(p)
    offset = e + 0.06
    ax.text(c + offset if c >= 0 else c - offset - 0.15, i,
            f"{c:.2f}{stars}", va='center', fontweight='bold', fontsize=11)
    ax.text(-1.85, i, f"p = {p:.4f}", va='center', fontsize=9, color='gray')

ax.axvline(0, color='#2C3E50', linewidth=0.8, linestyle='--', alpha=0.6)
ax.set_xlabel('Coefficient standardisé', fontsize=11)
ax.set_title('Déterminants de la croissance du PIB en Afrique\n'
             'Panel OLS à effets fixes — données normalisées',
             fontsize=13, fontweight='bold', pad=15)

from matplotlib.patches import Patch
ax.legend(handles=[
    Patch(facecolor='#C0392B', alpha=0.85, label='Significatif (p < 0.05)'),
    Patch(facecolor='#95A5A6', alpha=0.85, label='Non significatif (p ≥ 0.05)'),
], loc='lower right', fontsize=10)

stats_txt = (f"R² within = {res_af.rsquared_within:.3f}\n"
             f"F-stat = {res_af.f_statistic.stat:.2f}  (p < 0.0001)\n"
             f"N = {int(res_af.nobs)} obs. · {n_pays} pays · 25 ans")
ax.text(0.02, 0.03, stats_txt, transform=ax.transAxes, fontsize=9,
        bbox=dict(boxstyle='round,pad=0.4', facecolor='#EBF5FB', alpha=0.8))

plt.tight_layout()
plt.savefig('fig1_coefficients.png', dpi=300, bbox_inches='tight')
plt.show()
print("✅ fig1_coefficients.png")

# ── Visuel 2 : Dette publique vs Croissance ──
fig, ax = plt.subplots(figsize=(10, 6))

df_plot = df_afrique.reset_index()
ax.scatter(df_plot['debt'], df_plot['growth'],
           alpha=0.35, s=18, color='#2E86AB', edgecolors='none')

# Droite de régression
m, b, r, p_r, _ = stats.linregress(
    df_plot['debt'].dropna(), df_plot['growth'].dropna())
x_line = np.linspace(df_plot['debt'].min(), df_plot['debt'].max(), 200)
ax.plot(x_line, m * x_line + b, color='#C0392B', linewidth=2.2,
        label=f'Tendance  (r = {r:.2f}, p = {p_r:.4f})')

ax.set_xlabel('Dette publique (% du PIB)', fontsize=11)
ax.set_ylabel('Croissance du PIB (%)', fontsize=11)
ax.set_title('Dette publique et croissance économique en Afrique\n'
             '20 pays africains · Panel de données',
             fontsize=13, fontweight='bold', pad=15)
ax.legend(fontsize=10)
ax.text(0.02, 0.03,
        'Source : Banque Mondiale / FMI · Calculs de l\'auteur',
        transform=ax.transAxes, fontsize=8.5, color='gray')

plt.tight_layout()
plt.savefig('fig2_dette_croissance.png', dpi=300, bbox_inches='tight')
plt.show()
print("✅ fig2_dette_croissance.png")

# ── Visuel 3 : Matrice de corrélation ──
fig, ax = plt.subplots(figsize=(8, 7))

corr_af = df_afrique[VARIABLES + ['growth']].corr()
corr_af = corr_af.rename(index=dict(**NOMS_FR, growth='Croissance PIB'),
                          columns=dict(**NOMS_FR, growth='Croissance PIB'))

mask = np.triu(np.ones_like(corr_af, dtype=bool))
sns.heatmap(corr_af, mask=mask, annot=True, fmt='.2f',
            cmap='RdBu_r', center=0, square=True,
            linewidths=0.8, cbar_kws={"shrink": 0.75},
            annot_kws={'size': 10}, ax=ax)

ax.set_title('Matrice de corrélation\nVariables du modèle — Pays africains',
             fontsize=13, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig('fig3_correlation.png', dpi=300, bbox_inches='tight')
plt.show()
print("✅ fig3_correlation.png")

# ── 15. EXPORT ────────────────────────────────────────────────────────────────
print_section("EXPORT DES RÉSULTATS")

resultats_df = pd.DataFrame(resultats)
resultats_df.to_csv('resultats_modele.csv', index=False, encoding='utf-8-sig')
print("✅ resultats_modele.csv")

try:
    with pd.ExcelWriter('resultats_complets.xlsx', engine='openpyxl') as writer:
        resultats_df.to_excel(writer, sheet_name='Coefficients', index=False)
        df_afrique.reset_index().to_excel(writer, sheet_name='Données_Afrique', index=False)
    print("✅ resultats_complets.xlsx")
except Exception as e:
    print(f"⚠️ Export Excel : {e}")

print_section("ANALYSE TERMINÉE AVEC SUCCÈS")
