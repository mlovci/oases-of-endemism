import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler
from statsmodels.stats.stattools import durbin_watson

# Ensure figures directory exists
os.makedirs("figures", exist_ok=True)

# Styling settings
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

def fit_poisson_raw_with_bootstrap_ci(X_var, y, x_grid, n_boot=500):
    # Convert inputs to numpy arrays to avoid pandas index alignment issues in statsmodels
    X_arr = np.asarray(X_var)
    y_arr = np.asarray(y)
    
    # Main fit with robust standard errors
    X_model = sm.add_constant(X_arr)
    model = sm.GLM(y_arr, X_model, family=sm.families.Poisson()).fit(cov_type='HC3')
    y_pred = model.predict(sm.add_constant(x_grid))
    
    # Bootstrap
    np.random.seed(42)
    boot_preds = []
    boot_betas = []
    
    for _ in range(n_boot):
        idx = np.random.choice(len(y_arr), size=len(y_arr), replace=True)
        X_b = X_arr[idx]
        y_b = y_arr[idx]
        try:
            m_b = sm.GLM(y_b, sm.add_constant(X_b), family=sm.families.Poisson()).fit()
            boot_preds.append(m_b.predict(sm.add_constant(x_grid)))
            boot_betas.append(m_b.params[1])
        except Exception:
            pass
            
    boot_preds = np.array(boot_preds)
    y_pred_low = np.percentile(boot_preds, 2.5, axis=0)
    y_pred_high = np.percentile(boot_preds, 97.5, axis=0)
    
    beta_low = np.percentile(boot_betas, 2.5)
    beta_high = np.percentile(boot_betas, 97.5)
    
    return model, y_pred, y_pred_low, y_pred_high, model.params[1], beta_low, beta_high, model.pvalues[1]

def bootstrap_poisson(X_scaled, y, n_resamples=2000, seed=42):
    """
    Performs non-parametric bootstrapping to compute empirical 95% confidence intervals.
    Controls for low sample sizes (N=45) without relying on asymptotic normal assumptions.
    """
    np.random.seed(seed)
    boot_coefs = []
    
    # Ensure constant is present
    if 'const' not in X_scaled.columns:
        X_scaled = sm.add_constant(X_scaled)
        
    for _ in range(n_resamples):
        # Sample with replacement
        idx = np.random.choice(X_scaled.index, size=len(X_scaled), replace=True)
        X_boot = X_scaled.loc[idx]
        y_boot = y.loc[idx]
        try:
            model = sm.GLM(y_boot, X_boot, family=sm.families.Poisson()).fit()
            boot_coefs.append(model.params)
        except Exception:
            pass
            
    boot_df = pd.DataFrame(boot_coefs)
    cis = {}
    for col in boot_df.columns:
        low = np.percentile(boot_df[col], 2.5)
        high = np.percentile(boot_df[col], 97.5)
        cis[col] = (low, high)
    return cis

def analyze_latent_pattern_1(df):
    """
    Invasion-Diversity Oasis Coupling (Poisson GLM & Bootstrapping)
    """
    print("\n" + "="*60)
    print("LATENT PATTERN 1: The Invasion-Diversity Oasis Coupling (Poisson GLM)")
    print("="*60)
    
    reg_df = df[df["Aquifer Type"] == "Regional Aq"]
    
    # 1. Z-Normalize Predictor
    scaler = StandardScaler()
    x_raw = reg_df[["Non Natives"]]
    x_scaled = pd.DataFrame(scaler.fit_transform(x_raw), columns=["Non Natives_scaled"], index=reg_df.index)
    X_model = sm.add_constant(x_scaled)
    y = reg_df["Endemics"]
    
    # 2. Fit Poisson GLM with Robust Standard Errors (HC3)
    model = sm.GLM(y, X_model, family=sm.families.Poisson()).fit(cov_type='HC3')
    
    # 3. Perform Bootstrapping
    boot_cis = bootstrap_poisson(x_scaled, y)
    
    # 4. Check Autocorrelation
    dw_stat = durbin_watson(model.resid_pearson)
    
    print("\nPoisson GLM results (Standardized Predictor):")
    print(f"  Coefficient (Beta_standardized) = {model.params['Non Natives_scaled']:.4f}")
    print(f"  Robust HC3 SE                   = {model.bse['Non Natives_scaled']:.4f}")
    print(f"  z-statistic                     = {model.tvalues['Non Natives_scaled']:.4f}")
    print(f"  p-value                         = {model.pvalues['Non Natives_scaled']:.3e}")
    print(f"  Bootstrapped 95% CI             = [{boot_cis['Non Natives_scaled'][0]:.4f}, {boot_cis['Non Natives_scaled'][1]:.4f}]")
    print(f"  Durbin-Watson residual stat     = {dw_stat:.4f} (Checking for serial autocorrelation)")
    
    plt.figure(figsize=(8, 6))
    
    # Add manual jitter for plotting discrete count data on continuous numerical scale
    np.random.seed(42)
    x_jitter = reg_df["Non Natives"] + np.random.normal(0, 0.08, size=len(reg_df))
    y_jitter = reg_df["Endemics"] + np.random.normal(0, 0.08, size=len(reg_df))
    
    plt.scatter(
        x_jitter, 
        y_jitter, 
        color="#2ca02c", 
        s=60, 
        alpha=0.7, 
        edgecolors="black",
        linewidths=1,
        label="Observed Springs"
    )
    
    # Generate smooth predictions curve and calculate bootstrap confidence intervals
    x_grid = np.linspace(reg_df["Non Natives"].min(), reg_df["Non Natives"].max(), 200)
    model_raw, y_pred, y_pred_low, y_pred_high, beta, beta_low, beta_high, p_val = fit_poisson_raw_with_bootstrap_ci(
        reg_df["Non Natives"], y, x_grid
    )
    
    plt.plot(x_grid, y_pred, color="darkgreen", linewidth=2.5, label="Fitted Poisson Curve")
    plt.fill_between(x_grid, y_pred_low, y_pred_high, color="darkgreen", alpha=0.15, label="95% Bootstrap CI")
    
    # Display fit statistics on the plot
    info_text = f"Beta (slope): {beta:.3f}\n95% CI: [{beta_low:.3f}, {beta_high:.3f}]\np-value: {p_val:.3e}"
    plt.gca().text(0.05, 0.72, info_text, transform=plt.gca().transAxes, fontsize=10,
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="gray", alpha=0.8))
    
    plt.xlabel("Number of Non-Native Species (#)")
    plt.ylabel("Number of Endemic Taxa (#)")
    plt.title("Invasion-Diversity Oasis Coupling in Regional Springs")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(loc="upper left")
    
    plt.savefig("figures/Figure_15_Regional_Invasion_Diversity_Coupling.png", dpi=300)
    plt.savefig("figures/Figure_15_Regional_Invasion_Diversity_Coupling.pdf", dpi=300)
    plt.close()
    print("Invasion-Diversity plot saved to: figures/Figure_15_Regional_Invasion_Diversity_Coupling.png and .pdf")

def analyze_latent_pattern_2(df):
    """
    The Conservation/Management Disconnect
    """
    print("\n" + "="*50)
    print("LATENT PATTERN 2: The Conservation/Management Disconnect")
    print("="*50)
    
    means = df.groupby("Aquifer Type")[["Cattle", "Non Natives", "Endemics"]].mean()
    print("Mean values by spring type:")
    print(means.round(2))
    
    df_melted = df.melt(
        id_vars=["Aquifer Type"], 
        value_vars=["Cattle", "Non Natives", "Endemics"], 
        var_name="Metric", 
        value_name="Value"
    )
    
    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=df_melted,
        x="Aquifer Type",
        y="Value",
        hue="Metric",
        errorbar="se",
        palette=["#d62728", "#bcbd22", "#1f77b4"]
    )
    
    plt.ylabel("Average Value (Index / Species Count)")
    plt.xlabel("Spring Aquifer Type")
    plt.title("The Conservation Disconnect and Endemic Species Richness")
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.legend(title="Variable")
    
    plt.savefig("figures/Figure_16_Conservation_Disconnect.png", dpi=300)
    plt.savefig("figures/Figure_16_Conservation_Disconnect.pdf", dpi=300)
    plt.close()
    print("Conservation disconnect plot saved to: figures/Figure_16_Conservation_Disconnect.png and .pdf")

def analyze_latent_pattern_3(df):
    """
    Siltation as a Driver of Endemic Decline (Poisson GLM & Bootstrapping)
    """
    print("\n" + "="*50)
    print("LATENT PATTERN 3: Benthic Siltation Impact (Poisson GLM)")
    print("="*50)
    
    reg_df = df[df["Aquifer Type"] == "Regional Aq"]
    
    # 1. Z-Normalize Predictor
    scaler = StandardScaler()
    x_raw = reg_df[["Silt"]]
    x_scaled = pd.DataFrame(scaler.fit_transform(x_raw), columns=["Silt_scaled"], index=reg_df.index)
    X_model = sm.add_constant(x_scaled)
    y = reg_df["Endemics"]
    
    # 2. Fit Poisson GLM with Robust Standard Errors (HC3)
    model = sm.GLM(y, X_model, family=sm.families.Poisson()).fit(cov_type='HC3')
    
    # 3. Perform Bootstrapping
    boot_cis = bootstrap_poisson(x_scaled, y)
    
    # 4. Check Autocorrelation
    dw_stat = durbin_watson(model.resid_pearson)
    
    print("\nPoisson GLM results (Standardized Predictor):")
    print(f"  Coefficient (Beta_standardized) = {model.params['Silt_scaled']:.4f}")
    print(f"  Robust HC3 SE                   = {model.bse['Silt_scaled']:.4f}")
    print(f"  z-statistic                     = {model.tvalues['Silt_scaled']:.4f}")
    print(f"  p-value                         = {model.pvalues['Silt_scaled']:.3e}")
    print(f"  Bootstrapped 95% CI             = [{boot_cis['Silt_scaled'][0]:.4f}, {boot_cis['Silt_scaled'][1]:.4f}]")
    print(f"  Durbin-Watson residual stat     = {dw_stat:.4f} (Checking for serial autocorrelation)")
    
    plt.figure(figsize=(8, 6))
    
    # Add manual jitter to the discrete count y-values (since Silt is a continuous percentage x-axis)
    np.random.seed(42)
    y_jitter = reg_df["Endemics"] + np.random.normal(0, 0.08, size=len(reg_df))
    
    plt.scatter(
        reg_df["Silt"],
        y_jitter,
        color="#8c564b",
        s=60,
        alpha=0.7,
        edgecolors="black",
        linewidths=1,
        label="Observed Springs"
    )
    
    # Generate smooth predictions curve and calculate bootstrap confidence intervals
    x_grid = np.linspace(0, 100, 200)
    model_raw, y_pred, y_pred_low, y_pred_high, beta, beta_low, beta_high, p_val = fit_poisson_raw_with_bootstrap_ci(
        reg_df["Silt"], y, x_grid
    )
    
    plt.plot(x_grid, y_pred, color="darkred", linewidth=2.5, label="Fitted Poisson Curve")
    plt.fill_between(x_grid, y_pred_low, y_pred_high, color="darkred", alpha=0.15, label="95% Bootstrap CI")
    
    # Display fit statistics on the plot
    info_text = f"Beta (slope): {beta:.3f}\n95% CI: [{beta_low:.3f}, {beta_high:.3f}]\np-value: {p_val:.3e}"
    plt.gca().text(0.05, 0.72, info_text, transform=plt.gca().transAxes, fontsize=10,
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="gray", alpha=0.8))
    
    plt.xlabel("Silt Substrate Percentage (%)")
    plt.ylabel("Number of Endemic Taxa (#)")
    plt.title("Endemic Species Decline with Substrate Siltation")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(loc="upper right")
    
    plt.savefig("figures/Figure_8_Regional_Siltation_Decline.png", dpi=300)
    plt.savefig("figures/Figure_8_Regional_Siltation_Decline.pdf", dpi=300)
    plt.close()
    print("Siltation decline plot saved to: figures/Figure_8_Regional_Siltation_Decline.png and .pdf")

def main():
    df = load_data()
    analyze_latent_pattern_1(df)
    analyze_latent_pattern_2(df)
    analyze_latent_pattern_3(df)
    print("\nRigorous latent pattern analyses completed successfully!")

if __name__ == "__main__":
    main()
