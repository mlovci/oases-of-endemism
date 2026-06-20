import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import spearmanr
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA, FactorAnalysis
from sklearn.manifold import TSNE
import statsmodels.api as sm

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

def fit_poisson_with_bootstrap_ci(X_var, y, x_grid, n_boot=500):
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

def run_regional_factor_analysis(reg, features):
    print("="*65)
    print("1. FACTOR ANALYSIS (REGIONAL AQUIFER SPRINGS, N=45)")
    print("="*65)
    
    X = reg[features]
    y = reg["Endemics"]
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Fit Factor Analysis
    fa = FactorAnalysis(n_components=3, random_state=42)
    X_fa = fa.fit_transform(X_scaled)
    
    # Find correlations
    print("Correlations of Latent Factors with Endemic Richness:")
    factor_corrs = []
    for i in range(3):
        corr, p = spearmanr(y, X_fa[:, i])
        print(f"  Factor {i+1}: rs = {corr:.3f}, p = {p:.3e}")
        factor_corrs.append((i+1, corr, p))
        
    # Interpret Factor 2 (the highest correlating factor)
    print("\nEcological Loadings for Factor 2 (Benthic Habitat Quality Factor):")
    loadings = sorted(zip(features, fa.components_[1]), key=lambda x: abs(x[1]), reverse=True)
    for feat, load in loadings[:6]:
        print(f"  {feat:15}: {load: .3f}")
        
    # Plot Factor 2 vs Endemics with a Poisson fit (since Endemics is a count)
    plt.figure(figsize=(8, 6))
    
    # Add manual jitter for plotting
    np.random.seed(42)
    y_jitter = y + np.random.normal(0, 0.08, size=len(y))
    plt.scatter(X_fa[:, 1], y_jitter, color="#2ca02c", s=60, alpha=0.7, edgecolors="black", label="Observed Springs")
    
    # Fit Poisson GLM and calculate bootstrap confidence intervals
    x_grid = np.linspace(X_fa[:, 1].min() - 0.2, X_fa[:, 1].max() + 0.2, 200)
    model, y_pred, y_pred_low, y_pred_high, beta, beta_low, beta_high, p_val = fit_poisson_with_bootstrap_ci(
        X_fa[:, 1], y, x_grid
    )
    
    plt.plot(x_grid, y_pred, color="darkgreen", linewidth=2.5, label="Fitted Poisson Curve")
    plt.fill_between(x_grid, y_pred_low, y_pred_high, color="darkgreen", alpha=0.15, label="95% Bootstrap CI")
    
    # Display fit statistics on the plot
    info_text = f"Beta (slope): {beta:.3f}\n95% CI: [{beta_low:.3f}, {beta_high:.3f}]\np-value: {p_val:.3e}"
    plt.gca().text(0.05, 0.72, info_text, transform=plt.gca().transAxes, fontsize=10,
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="gray", alpha=0.8))
    plt.xlabel("Factor 2: Benthic Habitat Quality (Low Silt, Coarse substrate, High Temp)")
    plt.ylabel("Number of Endemic Taxa (#)")
    plt.title("Endemic Richness vs Latent Benthic Habitat Quality")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend(loc="upper left")
    
    plt.savefig("figures/Figure_3_Regional_FA_Benthic_Quality.png", dpi=300)
    plt.savefig("figures/Figure_3_Regional_FA_Benthic_Quality.pdf", dpi=300)
    plt.close()
    print("Factor 2 plot saved to: figures/Figure_3_Regional_FA_Benthic_Quality.png and .pdf")

def run_global_pca(df, features):
    print("\n" + "="*65)
    print("2. GLOBAL PCA & HABITAT DEGRADATION AXIS (N=1121)")
    print("="*65)
    
    X = df[features]
    y = df["Endemics"]
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    pca = PCA(n_components=3)
    X_pca = pca.fit_transform(X_scaled)
    
    print("Global PC correlations with Endemics:")
    for i in range(3):
        corr, p = spearmanr(y, X_pca[:, i])
        print(f"  PC{i+1}: rs = {corr:.3f}, p = {p:.3e}")
        
    print("\nEcological Loadings for Global PC3 (Grazing & Habitat Degradation Axis):")
    loadings = sorted(zip(features, pca.components_[2]), key=lambda x: abs(x[1]), reverse=True)
    for feat, load in loadings[:5]:
        print(f"  {feat:15}: {load: .3f}")
        
    # Plot PC3 vs Endemics with a Poisson fit
    plt.figure(figsize=(8, 6))
    np.random.seed(42)
    # Filter to springs that have at least some endemics for visual clarity, or plot all
    y_jitter = y + np.random.normal(0, 0.08, size=len(y))
    plt.scatter(X_pca[:, 2], y_jitter, color="#1f77b4", s=30, alpha=0.4, edgecolors="none", label="Observed Springs")
    
    # Fit Poisson GLM and calculate bootstrap confidence intervals
    x_grid = np.linspace(X_pca[:, 2].min(), X_pca[:, 2].max(), 200)
    model, y_pred, y_pred_low, y_pred_high, beta, beta_low, beta_high, p_val = fit_poisson_with_bootstrap_ci(
        X_pca[:, 2], y, x_grid
    )
    
    plt.plot(x_grid, y_pred, color="darkblue", linewidth=2.5, label="Fitted Poisson Curve")
    plt.fill_between(x_grid, y_pred_low, y_pred_high, color="darkblue", alpha=0.15, label="95% Bootstrap CI")
    
    # Display fit statistics on the plot
    info_text = f"Beta (slope): {beta:.3f}\n95% CI: [{beta_low:.3f}, {beta_high:.3f}]\np-value: {p_val:.3e}"
    plt.gca().text(0.05, 0.72, info_text, transform=plt.gca().transAxes, fontsize=10,
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="gray", alpha=0.8))
    plt.xlabel("Global PC3: Grazing & Habitat Degradation (High Cattle, Low Bank Cover)")
    plt.ylabel("Number of Endemic Taxa (#)")
    plt.title("Endemic Richness vs Latent Habitat Degradation")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend(loc="upper left")
    
    # Inset axes for PC3 loadings
    ax = plt.gca()
    inset_ax = ax.inset_axes([0.55, 0.52, 0.40, 0.43])
    pc3_loadings = pca.components_[2]
    loadings_series = pd.Series(pc3_loadings, index=features)
    sorted_loadings = loadings_series.sort_values(ascending=True)
    
    colors_list = ['#d62728' if v > 0 else '#1f77b4' for v in sorted_loadings.values]
    x_pos = np.arange(len(sorted_loadings))
    inset_ax.bar(x_pos, sorted_loadings.values, color=colors_list, edgecolor='none', width=0.7)
    inset_ax.set_xticks(x_pos)
    
    # Map feature names to intuitive descriptions showing the direction of association
    labels_mapping = {
        "Depth": "Pool Depth (-)",
        "Width": "Pool Width (-)",
        "Temperature": "Water Temp (-)",
        "Conductivity": "Conductivity (-)",
        "pH": "pH (-)",
        "Emerge Cover": "Emergent Cover (-)",
        "Bank Cover": "Bank Cover (-)",
        "Silt": "Silt Substrate (+)",
        "Sand": "Sand Substrate (+)",
        "Gravel": "Gravel Substrate (+)",
        "Cobble": "Cobble Substrate (-)",
        "Diversion": "Water Diversion (+)",
        "Equine": "Horse Disturbance (+)",
        "Cattle": "Cattle Grazing (+)",
        "Recreate": "Recreation Index (-)"
    }
    new_labels = [labels_mapping.get(feat, feat) for feat in sorted_loadings.index]
    inset_ax.set_xticklabels(new_labels, rotation=90, ha='center', fontsize=5)
    
    inset_ax.set_title("PC3 Loadings", fontsize=8, fontweight='bold', pad=4)
    inset_ax.tick_params(labelsize=6, pad=1)
    inset_ax.axhline(0, color='black', linewidth=0.5, linestyle='--')
    inset_ax.grid(True, axis='y', linestyle='--', alpha=0.3)
    
    plt.savefig("figures/Figure_4_Global_PCA_Habitat_Degradation.png", dpi=300)
    plt.savefig("figures/Figure_4_Global_PCA_Habitat_Degradation.pdf", dpi=300)
    plt.close()
    print("Global PC3 plot saved to: figures/Figure_4_Global_PCA_Habitat_Degradation.png and .pdf")
    
    return X_scaled, y

def run_global_tsne(X_scaled, y, df):
    print("\n" + "="*65)
    print("3. GLOBAL MANIFOLD LEARNING (t-SNE, N=1121)")
    print("="*65)
    
    print("Computing t-SNE coordinates...")
    tsne = TSNE(n_components=2, perplexity=30, random_state=42, max_iter=1000)
    X_tsne = tsne.fit_transform(X_scaled)
    
    # Center coordinates so that origin (0, 0) is the center of the manifold
    X_tsne = X_tsne - X_tsne.mean(axis=0)
    
    # Create a 2-panel figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 9))
    
    # PANEL A: Colored by Endemic Species Richness
    import matplotlib.colors as mcolors
    cmap = plt.colormaps["viridis"].resampled(9)
    bounds = [-0.5, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 7.5, 8.5, 9.5]
    norm = mcolors.BoundaryNorm(bounds, cmap.N)
    
    sizes = 30 + y * 35
    aq_types = df["Aquifer Type"].values
    marker_dict = {
        "Regional Aq": "o",
        "Local Hot": "v",
        "Local Cold": "d"
    }
    unique_aquifers = ["Regional Aq", "Local Hot", "Local Cold"]
    
    last_scatter = None
    for aq in unique_aquifers:
        mask = (aq_types == aq)
        if not mask.any():
            continue
        last_scatter = ax1.scatter(
            X_tsne[mask, 0], 
            X_tsne[mask, 1], 
            c=y[mask], 
            cmap=cmap, 
            norm=norm,
            s=sizes[mask], 
            marker=marker_dict[aq],
            alpha=0.6,
            edgecolors="none",
            label=aq
        )
    
    cbar = fig.colorbar(last_scatter, ax=ax1, ticks=[0, 1, 2, 3, 4, 5, 6.5, 8, 9], fraction=0.046, pad=0.04)
    cbar.set_ticklabels(['0', '1', '2', '3', '4', '5', '6-7', '8', '9'])
    cbar.set_label("Number of Endemic Taxa (#)", rotation=270, labelpad=15)
    
    leg1 = ax1.legend(title="Aquifer Type", loc="upper right", frameon=True)
    try:
        handles = leg1.legend_handles
    except AttributeError:
        handles = leg1.legendHandles
    for handle in handles:
        handle.set_sizes([60.0])
        handle.set_color("gray")
        
    ax1.set_xlabel("t-SNE Dimension 1", fontsize=12)
    ax1.set_ylabel("t-SNE Dimension 2", fontsize=12)
    ax1.set_title("A. Manifold colored by Endemic Richness", fontsize=14, fontweight="bold", pad=8)
    ax1.grid(True, linestyle="--", alpha=0.3)
    
    # PANEL B: Environmental Vector Overlays (envfit)
    color_dict = {
        "Regional Aq": "#17becf",
        "Local Hot": "#d62728",
        "Local Cold": "#1f77b4"
    }
    
    # Exaggerated point size scale based on number of endemic species
    sizes_exaggerated = 20 + y * 80
    
    for aq in unique_aquifers:
        mask = (aq_types == aq)
        if not mask.any():
            continue
        ax2.scatter(
            X_tsne[mask, 0], 
            X_tsne[mask, 1], 
            color=color_dict[aq],
            s=sizes_exaggerated[mask], 
            marker=marker_dict[aq],
            alpha=0.4,
            edgecolors="black",
            linewidths=0.3
        )
        
    # Fit vectors
    from sklearn.linear_model import LinearRegression
    features = ["Depth", "Width", "Temperature", "Conductivity", "pH", 
                "Emerge Cover", "Bank Cover", "Silt", "Sand", "Gravel", "Cobble",
                "Diversion", "Equine", "Cattle", "Recreate"]
                
    feature_labels = {
        "Depth": "Depth",
        "Width": "Width",
        "Temperature": "Temp",
        "Conductivity": "Cond",
        "pH": "pH",
        "Emerge Cover": "Emerg Cov",
        "Bank Cover": "Bank Cov",
        "Silt": "Silt",
        "Sand": "Sand",
        "Gravel": "Gravel",
        "Cobble": "Cobble",
        "Diversion": "Diversion",
        "Equine": "Equine",
        "Cattle": "Cattle",
        "Recreate": "Recreate"
    }
    
    scale_factor = 28.0
    for feat in features:
        val = df[feat].values
        reg = LinearRegression()
        reg.fit(X_tsne, val)
        
        coef = reg.coef_
        r2 = reg.score(X_tsne, val)
        r = np.sqrt(r2)
        
        norm_val = np.linalg.norm(coef)
        if norm_val > 0:
            direction = coef / norm_val
        else:
            direction = np.array([0.0, 0.0])
            
        dx = direction[0] * r * scale_factor
        dy = direction[1] * r * scale_factor
        
        if feat in ["Diversion", "Equine", "Cattle"]:
            arrow_color = "#d95f02"
        elif feat in ["Silt", "Sand", "Gravel", "Cobble"]:
            arrow_color = "#7570b3"
        else:
            arrow_color = "#1b9e77"
            
        if r > 0.05:
            ax2.arrow(0, 0, dx, dy, color=arrow_color, alpha=0.85, 
                      width=0.15, head_width=0.9, head_length=1.2, zorder=5)
            
            offset_x = dx * 1.15
            offset_y = dy * 1.15
            
            ax2.text(offset_x, offset_y, feature_labels[feat], color="black", 
                     fontsize=9.5, fontweight="bold", ha="center", va="center", 
                     bbox=dict(boxstyle="round,pad=0.15", facecolor="white", edgecolor="none", alpha=0.75),
                     zorder=6)
                     
    from matplotlib.patches import Patch
    arrow_legend = [
        Patch(color="#1b9e77", label="Physical & Water Chemistry"),
        Patch(color="#7570b3", label="Substrate Composition"),
        Patch(color="#d95f02", label="Anthropogenic Disturbance")
    ]
    from matplotlib.lines import Line2D
    marker_legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#17becf', markersize=8, label='Regional Aquifer'),
        Line2D([0], [0], marker='v', color='w', markerfacecolor='#d62728', markersize=8, label='Local Geothermal (Hot)'),
        Line2D([0], [0], marker='d', color='w', markerfacecolor='#1f77b4', markersize=8, label='Local Cold')
    ]
    ax2_legend_handles = arrow_legend + [Line2D([0], [0], color="none", label="")] + marker_legend_elements
    ax2.legend(handles=ax2_legend_handles, loc="upper right", frameon=True, fontsize=9.5)
    
    ax2.set_xlabel("t-SNE Dimension 1", fontsize=12)
    ax2.set_ylabel("t-SNE Dimension 2", fontsize=12)
    ax2.set_title("B. Environmental Gradients & Aquifer Distribution", fontsize=14, fontweight="bold", pad=8)
    ax2.grid(True, linestyle="--", alpha=0.3)
    
    ax1.set_xlim(-40, 40)
    ax1.set_ylim(-40, 40)
    ax2.set_xlim(-40, 40)
    ax2.set_ylim(-40, 40)
    
    fig.suptitle("Global t-SNE Manifold & Environmental Driver Gradients ($N=1121$)", fontsize=18, fontweight="bold", y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    
    plt.savefig("figures/Figure_5_Global_tSNE_Endemics.png", dpi=300)
    plt.savefig("figures/Figure_5_Global_tSNE_Endemics.pdf", dpi=300)
    plt.close()
    print("t-SNE Manifold plot saved to: figures/Figure_5_Global_tSNE_Endemics.png and .pdf")

def main():
    df = load_data()
    features = ["Depth", "Width", "Temperature", "Conductivity", "pH", 
                "Emerge Cover", "Bank Cover", "Silt", "Sand", "Gravel", "Cobble",
                "Diversion", "Equine", "Cattle", "Recreate"]
                
    reg = df[df["Aquifer Type"] == "Regional Aq"]
    
    run_regional_factor_analysis(reg, features)
    X_scaled, y = run_global_pca(df, features)
    run_global_tsne(X_scaled, y, df)
    print("\nUnsupervised latent analysis completed successfully!")

if __name__ == "__main__":
    main()
