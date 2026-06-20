import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.preprocessing import StandardScaler
from sklearn.inspection import PartialDependenceDisplay
from joblib import Parallel, delayed

# Ensure figures directory exists
os.makedirs("figures", exist_ok=True)

# Styling settings
sns.set_theme(style="ticks", context="talk")
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Calibri", "DejaVu Sans"],
    "figure.titlesize": 16,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "savefig.bbox": "tight"
})

def load_data(file_path="Data_Table_S5.xlsx"):
    df = pd.read_excel(file_path, header=[0, 1])
    df.columns = df.columns.get_level_values(0)
    return df

def run_single_bootstrap(X_scaled, y, seed):
    """
    Fits a single bootstrap Random Forest regressor and returns validation metrics.
    """
    np.random.seed(seed)
    train_idx = np.random.choice(X_scaled.index, size=len(X_scaled), replace=True)
    val_idx = np.array(list(set(X_scaled.index) - set(train_idx)))
    
    X_train, y_train = X_scaled.loc[train_idx], y.loc[train_idx]
    X_val, y_val = X_scaled.loc[val_idx], y.loc[val_idx]
    
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=4,
        max_features="sqrt",
        random_state=seed
    )
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_val)
    try:
        val_r2 = r2_score(y_val, y_pred)
    except Exception:
        val_r2 = np.nan
    val_mse = mean_squared_error(y_val, y_pred)
    
    return model.feature_importances_, val_r2, val_mse

def analyze_aquifer(df, aquifer_name, n_iterations=1000):
    print("\n" + "="*70)
    print(f"ANALYSIS FOR AQUIFER TYPE: {aquifer_name}")
    print("="*70)
    
    # Subset data
    subset = df[df["Aquifer Type"] == aquifer_name].copy()
    print(f"Sample size: N = {len(subset)}")
    
    features = ["Depth", "Width", "Temperature", "Conductivity", "pH", 
                "Emerge Cover", "Bank Cover", "Silt", "Sand", "Gravel", "Cobble",
                "Diversion", "Equine", "Cattle", "Recreate", "Non Natives"]
                
    X_raw = subset[features].astype(float)
    y = subset["Endemics"]
    
    # 1. Standardize predictors for bootstrap regression
    scaler = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X_raw), columns=features, index=subset.index)
    
    # 2. Run Parallelized Bootstrapping
    print(f"Running {n_iterations} bootstrap replicates in parallel...")
    results = Parallel(n_jobs=-1)(
        delayed(run_single_bootstrap)(X_scaled, y, 42 + i) for i in range(n_iterations)
    )
    
    importances_list = [r[0] for r in results]
    r2_scores = [r[1] for r in results if not np.isnan(r[1])]
    mse_scores = [r[2] for r in results]
    
    # 3. Print Validation Metrics
    mean_r2 = np.mean(r2_scores)
    median_r2 = np.median(r2_scores)
    mean_mse = np.mean(mse_scores)
    print(f"\nOut-of-Sample OOB Validation Metrics:")
    print(f"  Mean R-squared (R2)  = {mean_r2:.4f}")
    print(f"  Median R-squared (R2)= {median_r2:.4f}")
    print(f"  Mean Squared Error   = {mean_mse:.4f}")
    
    # 4. Generate Feature Importance Boxplot
    importances_df = pd.DataFrame(importances_list, columns=features)
    sorted_features = importances_df.median().sort_values(ascending=False).index
    
    plt.figure(figsize=(10, 8))
    sns.boxplot(
        data=importances_df, 
        order=sorted_features, 
        orient="h",
        palette="viridis",
        hue_order=sorted_features
    )
    plt.xlabel("Feature Importance Score (Gini)")
    plt.ylabel("Environmental & Biological Features")
    plt.title(f"Bootstrap Feature Importance: {aquifer_name} (N = {n_iterations} splits)")
    plt.grid(axis='x', linestyle='--', alpha=0.5)
    
    sanitized_name = aquifer_name.lower().replace(" ", "_")
    if sanitized_name == "regional_aq":
        box_num, pdp_num = "Figure_9", "Figure_10"
        display_name = "Regional_Aq"
    elif sanitized_name == "local_hot":
        box_num, pdp_num = "Figure_11", "Figure_12"
        display_name = "Local_Hot"
    else:
        box_num, pdp_num = "Figure_13", "Figure_14"
        display_name = "Local_Cold"
        
    box_base = f"figures/{box_num}_Bootstrap_Importance_{display_name}"
    plt.savefig(f"{box_base}.png", dpi=300)
    plt.savefig(f"{box_base}.pdf", dpi=300)
    plt.close()
    print(f"Bootstrap Importance Boxplot saved to: {box_base}.png and .pdf")
    
    # 5. Calculate and Plot Partial Dependence Plots
    # Fit model on raw features
    rf_raw = RandomForestRegressor(
        n_estimators=500,
        max_depth=4,
        max_features="sqrt",
        random_state=42
    )
    rf_raw.fit(X_raw, y)
    
    fig, axes = plt.subplots(4, 4, figsize=(16, 14))
    axes_flat = axes.flatten()
    
    print("Calculating partial dependencies...")
    display = PartialDependenceDisplay.from_estimator(
        rf_raw, 
        X_raw, 
        features, 
        ax=axes_flat,
        grid_resolution=50
    )
    
    # Format axes labels
    for idx, ax in enumerate(axes_flat):
        ax.set_title(features[idx], fontsize=11, fontweight="bold")
        ax.set_xlabel("")
        ax.grid(True, linestyle="--", alpha=0.4)
        
    fig.suptitle(f"Partial Dependence Plots: {aquifer_name} Springs", fontsize=15, fontweight="bold", y=0.98)
    fig.text(0.5, 0.01, "Feature Value (Raw Units)", ha="center", fontsize=12)
    fig.text(0.01, 0.5, "Partial Dependence (Expected Endemics)", va="center", rotation="vertical", fontsize=12)
    
    plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.96])
    pdp_base = f"figures/{pdp_num}_PDP_{display_name}"
    plt.savefig(f"{pdp_base}.png", dpi=300)
    plt.savefig(f"{pdp_base}.pdf", dpi=300)
    plt.close()
    print(f"Partial Dependence plot saved to: {pdp_base}.png and .pdf")
    
    # 6. Extract PDP deltas for comparison
    print("\nPDP Marginal Response Ranges (Max Deltas):")
    deltas = []
    for idx, feat in enumerate(features):
        pd_data = display.pd_results[idx]
        preds = pd_data['average'][0]
        min_p = np.min(preds)
        max_p = np.max(preds)
        delta = max_p - min_p
        deltas.append((feat, min_p, max_p, delta))
        
    # Sort and print
    deltas.sort(key=lambda x: x[3], reverse=True)
    print(f"  {"Feature":15} | {"Min Response":12} | {"Max Response":12} | {"Max Delta":10}")
    print("  " + "-"*56)
    for feat, min_p, max_p, delta in deltas:
        print(f"  {feat:15} | {min_p:12.4f} | {max_p:12.4f} | {delta:10.4f}")
        
    return {
        "aquifer": aquifer_name,
        "mean_r2": mean_r2,
        "median_r2": median_r2,
        "mean_mse": mean_mse,
        "importances": importances_df.mean().to_dict(),
        "deltas": {d[0]: d[3] for d in deltas}
    }

def main():
    df = load_data()
    aquifers = ["Regional Aq", "Local Hot", "Local Cold"]
    
    all_summaries = []
    for aq in aquifers:
        summary = analyze_aquifer(df, aq)
        all_summaries.append(summary)
        
    # Compile a master summary table of top features
    print("\n" + "="*70)
    print("MASTER SUMMARY: TOP PREDICTORS BY AQUIFER TYPE")
    print("="*70)
    
    for s in all_summaries:
        print(f"\nAquifer Type: {s['aquifer']}")
        print(f"  Median OOB R-squared: {s['median_r2']:.4f}")
        print("  Top 5 Features by Mean Gini Importance:")
        sorted_imps = sorted(s["importances"].items(), key=lambda x: x[1], reverse=True)[:5]
        for f, imp in sorted_imps:
            print(f"    - {f:15}: {imp:.4f} (PDP Max Delta = {s['deltas'][f]:.4f})")
            
    print("\nAll independent analyses completed successfully!")

if __name__ == "__main__":
    main()
