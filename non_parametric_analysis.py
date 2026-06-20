import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import spearmanr
from sklearn.ensemble import RandomForestRegressor
import statsmodels.api as sm

# Ensure figures directory exists
os.makedirs("figures", exist_ok=True)

# Set publication quality styling
sns.set_theme(style="ticks", context="talk")
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Calibri", "DejaVu Sans"],
    "figure.titlesize": 16,
    "axes.titlesize": 14,
    "axes.labelsize": 12,
    "xtick.labelsize": 11,
    "ytick.labelsize": 11,
    "legend.fontsize": 11,
    "savefig.bbox": "tight"
})

def load_data(file_path="Data_Table_S5.xlsx"):
    df = pd.read_excel(file_path, header=[0, 1])
    df.columns = df.columns.get_level_values(0)
    return df

def run_spearman_analysis(df):
    print("="*65)
    # Filter regional springs
    reg = df[df["Aquifer Type"] == "Regional Aq"]
    
    print(f"1. SPEARMAN RANK CORRELATIONS (rs) IN REGIONAL SPRINGS (N={len(reg)})")
    print("="*65)
    
    # Spearman correlations between Endemics and all environmental variables
    features = ["Depth", "Width", "Temperature", "Conductivity", "pH", 
                "Emerge Cover", "Bank Cover", "Silt", "Sand", "Gravel", "Cobble",
                "Diversion", "Equine", "Cattle", "Recreate"]
                
    spearman_results = []
    for f in features:
        corr, p = spearmanr(reg["Endemics"], reg[f])
        spearman_results.append((f, corr, p))
        
    spearman_results.sort(key=lambda x: abs(x[1]), reverse=True)
    print(f"  {"Feature":15} | {"Spearman rs":11} | {"p-value":10}")
    print("  " + "-"*44)
    for f, corr, p in spearman_results:
        print(f"  {f:15} | {corr: .3f}       | {p:.3e}")
        
    # Spearman correlations between biological counts
    print("\nSpearman correlations among all species counts:")
    species_cols = ["Endemics", "Crenophilies", "Springsnails", "Non Natives", "Native Fish"]
    corr_matrix, p_matrix = spearmanr(reg[species_cols])
    
    # Format and print correlation matrix
    corr_df = pd.DataFrame(corr_matrix, index=species_cols, columns=species_cols)
    print(corr_df.round(3))
    
    return reg, features

def run_random_forest_importance(reg, features):
    print("\n" + "="*65)
    print("2. NON-PARAMETRIC RANDOM FOREST FEATURE IMPORTANCE")
    print("="*65)
    
    X = reg[features]
    y = reg["Endemics"]
    
    # Fit Random Forest Regressor
    rf = RandomForestRegressor(n_estimators=500, random_state=42)
    rf.fit(X, y)
    
    importances = pd.Series(rf.feature_importances_, index=features).sort_values(ascending=False)
    print("Random Forest Feature Importances:")
    for f, imp in importances.items():
        print(f"  {f:15}: {imp:.3f}")
        
    # Plot feature importances
    plt.figure(figsize=(9, 6))
    sns.barplot(
        x=importances.values, 
        y=importances.index, 
        palette="viridis",
        hue=importances.index,
        legend=False
    )
    plt.xlabel("Gini Importance Score")
    plt.ylabel("Environmental Feature")
    plt.title("Random Forest Feature Importance predicting Endemics")
    plt.grid(axis='x', linestyle='--', alpha=0.5)
    
    plt.savefig("figures/Figure_S3_Random_Forest_Importance.png", dpi=300)
    plt.savefig("figures/Figure_S3_Random_Forest_Importance.pdf", dpi=300)
    plt.close()
    print("Feature Importance plot saved to: figures/Figure_S3_Random_Forest_Importance.png and .pdf")

def plot_lowess_smoothing(reg):
    print("\n" + "="*65)
    print("3. LOWESS SMOOTHING (Locally Weighted Scatterplot Smoothing)")
    print("="*65)
    
    # Lowess 1: Endemics ~ Non Natives
    plt.figure(figsize=(8, 6))
    np.random.seed(42)
    x_jitter = reg["Non Natives"] + np.random.normal(0, 0.08, size=len(reg))
    y_jitter = reg["Endemics"] + np.random.normal(0, 0.08, size=len(reg))
    
    plt.scatter(x_jitter, y_jitter, color="#2ca02c", s=60, alpha=0.6, edgecolors="black", label="Observed Springs")
    
    # Fit LOWESS (frac represents the fraction of data used for local smoothing)
    lowess_fit = sm.nonparametric.lowess(reg["Endemics"], reg["Non Natives"], frac=0.6)
    plt.plot(lowess_fit[:, 0], lowess_fit[:, 1], color="darkgreen", linewidth=2.5, label="LOWESS Fit (frac=0.6)")
    
    plt.xlabel("Number of Non-Native Species (#)")
    plt.ylabel("Number of Endemic Taxa (#)")
    plt.title("Non-parametric LOWESS: Endemics vs Non-Natives")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(loc="upper left")
    
    plt.savefig("figures/Figure_S4_LOWESS_Invasion.png", dpi=300)
    plt.savefig("figures/Figure_S4_LOWESS_Invasion.pdf", dpi=300)
    plt.close()
    print("LOWESS Invasion plot saved to: figures/Figure_S4_LOWESS_Invasion.png and .pdf")
    
    # Lowess 2: Endemics ~ Silt %
    plt.figure(figsize=(8, 6))
    y_jitter_silt = reg["Endemics"] + np.random.normal(0, 0.08, size=len(reg))
    plt.scatter(reg["Silt"], y_jitter_silt, color="#8c564b", s=60, alpha=0.6, edgecolors="black", label="Observed Springs")
    
    lowess_fit_silt = sm.nonparametric.lowess(reg["Endemics"], reg["Silt"], frac=0.6)
    plt.plot(lowess_fit_silt[:, 0], lowess_fit_silt[:, 1], color="darkred", linewidth=2.5, label="LOWESS Fit (frac=0.6)")
    
    plt.xlabel("Silt Substrate Percentage (%)")
    plt.ylabel("Number of Endemic Taxa (#)")
    plt.title("Non-parametric LOWESS: Endemic Decline with Siltation")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(loc="upper right")
    
    plt.savefig("figures/Figure_S5_LOWESS_Siltation.png", dpi=300)
    plt.savefig("figures/Figure_S5_LOWESS_Siltation.pdf", dpi=300)
    plt.close()
    print("LOWESS Siltation plot saved to: figures/Figure_S5_LOWESS_Siltation.png and .pdf")

def main():
    df = load_data()
    reg, features = run_spearman_analysis(df)
    run_random_forest_importance(reg, features)
    plot_lowess_smoothing(reg)
    print("\nNon-parametric analyses completed successfully!")

if __name__ == "__main__":
    main()
