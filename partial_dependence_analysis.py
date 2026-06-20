import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import PartialDependenceDisplay

# Ensure figures directory exists
os.makedirs("figures", exist_ok=True)

# Styling settings
sns.set_theme(style="ticks", context="talk")
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Calibri", "DejaVu Sans"],
    "figure.titlesize": 16,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "savefig.bbox": "tight"
})

def load_data(file_path="Data_Table_S5.xlsx"):
    df = pd.read_excel(file_path, header=[0, 1])
    df.columns = df.columns.get_level_values(0)
    return df

def run_partial_dependence(df):
    print("="*65)
    print("PARTIAL DEPENDENCE PLOTS (PDP) ANALYSIS")
    print("="*65)
    
    # Subset to Regional Aquifer springs
    reg = df[df["Aquifer Type"] == "Regional Aq"].copy()
    
    features = ["Depth", "Width", "Temperature", "Conductivity", "pH", 
                "Emerge Cover", "Bank Cover", "Silt", "Sand", "Gravel", "Cobble",
                "Diversion", "Equine", "Cattle", "Recreate", "Non Natives"]
                
    # Cast to float to avoid sklearn integer validation issues
    X = reg[features].astype(float)
    y = reg["Endemics"]
    
    # Fit model (raw scale for interpretable PDP x-axes)
    rf = RandomForestRegressor(
        n_estimators=500,
        max_depth=4,
        max_features="sqrt",
        random_state=42
    )
    rf.fit(X, y)
    
    # Setup subplots grid (4x4)
    fig, axes = plt.subplots(4, 4, figsize=(16, 14))
    axes_flat = axes.flatten()
    
    # Generate PDPs
    print("Calculating partial dependencies...")
    display = PartialDependenceDisplay.from_estimator(
        rf, 
        X, 
        features, 
        ax=axes_flat,
        grid_resolution=50
    )
    
    # Refine visual labels and layout
    for idx, ax in enumerate(axes_flat):
        ax.set_title(features[idx], fontsize=11, fontweight="bold")
        ax.set_xlabel("") # Remove feature label since it is in the title
        ax.grid(True, linestyle="--", alpha=0.4)
        
    fig.suptitle("Partial Dependence Plots (PDP) of Spring Features on Endemic Richness", fontsize=15, fontweight="bold", y=0.98)
    fig.text(0.5, 0.01, "Feature Value (Raw Units)", ha="center", fontsize=12)
    fig.text(0.01, 0.5, "Partial Dependence (Expected Endemics)", va="center", rotation="vertical", fontsize=12)
    
    plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.96])
    
    plot_path = "figures/partial_dependence_plots.png"
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print(f"Partial Dependence plot saved to: {plot_path}")
    
    # Extract and print PDP results for quantitative description
    print("\nQuantitative Summary of Marginal Effects (PDP Ranges):")
    print(f"  {"Feature":15} | {"Min Response":12} | {"Max Response":12} | {"Max Delta":10}")
    print("  " + "-"*56)
    
    # In scikit-learn, display.pd_results is a list of results dictionaries
    for idx, feat in enumerate(features):
        pd_data = display.pd_results[idx]
        # pd_data['average'][0] contains the average predictions
        preds = pd_data['average'][0]
        min_p = np.min(preds)
        max_p = np.max(preds)
        delta = max_p - min_p
        print(f"  {feat:15} | {min_p:12.4f} | {max_p:12.4f} | {delta:10.4f}")
        
    print("\nTop features by PDP marginal effect size (Max Delta):")
    deltas = []
    for idx, feat in enumerate(features):
        pd_data = display.pd_results[idx]
        preds = pd_data['average'][0]
        deltas.append((feat, np.max(preds) - np.min(preds)))
    deltas.sort(key=lambda x: x[1], reverse=True)
    for feat, delta in deltas:
        print(f"  {feat:15}: {delta:.4f}")

def main():
    df = load_data()
    run_partial_dependence(df)
    print("\nPartial dependence analysis completed successfully!")

if __name__ == "__main__":
    main()
