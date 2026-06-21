import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy.stats import kruskal, f_oneway

# Ensure figure directory exists
os.makedirs("figures", exist_ok=True)

# Set styling for publication-quality plots
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
    print(f"Loading dataset from: {file_path}")
    df = pd.read_excel(file_path, header=[0, 1])
    # Flatten MultiIndex columns to level 0 (variable names)
    df.columns = df.columns.get_level_values(0)
    return df

def analyze_groups(df):
    print("\n" + "="*50)
    print("1. DESCRIPTIVE STATISTICS BY AQUIFER TYPE")
    print("="*50)
    
    bio_cols = ["Endemics", "Crenophilies", "Springsnails", "Non Natives", "Native Fish"]
    env_cols = ["Temperature", "Conductivity", "Depth", "Width", "pH"]
    
    # Calculate group means and standard errors
    summary_mean = df.groupby("Aquifer Type")[bio_cols + env_cols].mean()
    summary_std = df.groupby("Aquifer Type")[bio_cols + env_cols].std()
    
    print("\nMean Values:")
    print(summary_mean.round(2))
    
    print("\nStandard Deviations:")
    print(summary_std.round(2))
    
    # Statistical Significance Testing (Kruskal-Wallis non-parametric ANOVA)
    print("\n" + "="*50)
    print("2. STATISTICAL SIGNIFICANCE TESTING (Kruskal-Wallis)")
    print("="*50)
    
    groups = df["Aquifer Type"].unique()
    for col in bio_cols:
        group_data = [df[df["Aquifer Type"] == g][col].values for g in groups]
        stat, p_val = kruskal(*group_data)
        print(f"Kruskal-Wallis H-test for {col}:")
        print(f"  H-statistic = {stat:.3f}, p-value = {p_val:.3e}")
        if p_val < 0.05:
            print(f"  --> Significant difference in {col} richness across spring types.")
        else:
            print(f"  --> No significant difference in {col} richness.")
            
    return summary_mean

def run_pca_analysis(df):
    print("\n" + "="*50)
    print("3. PRINCIPAL COMPONENT ANALYSIS (PCA)")
    print("="*50)
    
    # Include all 20 variables (both environmental and biological) to replicate the paper's PCA exactly
    features = ["Depth", "Width", "Temperature", "Conductivity", "pH", 
                "Emerge Cover", "Bank Cover", "Silt", "Sand", "Gravel", "Cobble",
                "Diversion", "Equine", "Cattle", "Recreate",
                "Endemics", "Crenophilies", "Springsnails", "Non Natives", "Native Fish"]
                
    X = df[features].astype(float)
    y = df["Aquifer Type"]
    
    # Square root transform biological variables prior to scaling as described in the paper's methods
    bio_cols = ["Endemics", "Crenophilies", "Springsnails", "Non Natives", "Native Fish"]
    X_transformed = X.copy()
    X_transformed[bio_cols] = np.sqrt(X_transformed[bio_cols])
    
    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_transformed)
    
    # Run PCA
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    
    # Flip the signs of PC1 and PC2 to match the paper's coordinate convention exactly
    X_pca[:, 0] = -X_pca[:, 0]
    X_pca[:, 1] = -X_pca[:, 1]
    pca.components_[0, :] = -pca.components_[0, :]
    pca.components_[1, :] = -pca.components_[1, :]
    
    print(f"Explained Variance Ratio: PC1 = {pca.explained_variance_ratio_[0]:.2%}, PC2 = {pca.explained_variance_ratio_[1]:.2%}")
    
    # Create PCA plot
    plt.figure(figsize=(10, 8))
    
    # Plot individual springs with shapes and colors matching the paper
    # Regional Aq: Teal/Cyan circles
    mask_reg = (y == "Regional Aq")
    plt.scatter(X_pca[mask_reg, 0], X_pca[mask_reg, 1], marker="o", color="#17becf", label="Regional Aq", alpha=0.7, edgecolors="none", s=50)
    
    # Local Hot: Red downward triangles
    mask_hot = (y == "Local Hot")
    plt.scatter(X_pca[mask_hot, 0], X_pca[mask_hot, 1], marker="v", color="red", label="Local Hot", alpha=0.8, edgecolors="black", linewidths=0.5, s=50)
    
    # Local Cold: Dark blue open diamonds
    mask_cold = (y == "Local Cold")
    plt.scatter(X_pca[mask_cold, 0], X_pca[mask_cold, 1], marker="d", facecolors="none", edgecolors="#000080", label="Local Cold", alpha=0.8, s=40, linewidths=1.0)
    
    # Plot loading vectors (green arrows in the paper)
    scale_factor = 8.0 # Scale up for readability against data coordinate range
    labels_mapping = {
        "Depth": "Depth",
        "Width": "Width",
        "Temperature": "Temperature",
        "Conductivity": "Conductivity",
        "pH": "pH",
        "Emerge Cover": "Emergent cover",
        "Bank Cover": "Bank cover",
        "Silt": "Silt",
        "Sand": "Sand",
        "Gravel": "Gravel",
        "Cobble": "Cobble",
        "Diversion": "Diversion",
        "Equine": "Equine",
        "Cattle": "Cattle",
        "Recreate": "Recreate",
        "Endemics": "Endemics",
        "Crenophilies": "Crenophiles",
        "Springsnails": "Springsnails",
        "Non Natives": "Non-natives",
        "Native Fish": "Native fish"
    }
    
    for i, feature in enumerate(features):
        dx = pca.components_[0, i] * scale_factor
        dy = pca.components_[1, i] * scale_factor
        plt.arrow(0, 0, dx, dy, color='green', alpha=0.6, head_width=0.2, head_length=0.25, zorder=5)
        # Avoid label crowding by offsetting slightly
        lbl = labels_mapping.get(feature, feature)
        plt.text(dx * 1.1, dy * 1.1, lbl, color='black', ha='center', va='center', fontsize=8, fontweight='normal', zorder=6)
        
    plt.xlabel(f"PC1 ({pca.explained_variance_ratio_[0]:.1%}) - Hydrological Permanence & Biological Richness Axis")
    plt.ylabel(f"PC2 ({pca.explained_variance_ratio_[1]:.1%})")
    plt.title("Principal Component Analysis (PCA) - Replicating Paper Figure 5a")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(title="Aquifer Type", loc="upper right")
    plt.axhline(0, color='black', linewidth=0.8, linestyle='--')
    plt.axvline(0, color='black', linewidth=0.8, linestyle='--')
    
    # Set plot boundaries to accommodate all points and vectors
    plt.xlim(-18, 5)
    plt.ylim(-8, 8)
    
    plt.savefig("figures/Figure_S2_PCA_Biplot.png", dpi=300)
    plt.savefig("figures/Figure_S2_PCA_Biplot.pdf", dpi=300)
    plt.close()
    print("PCA Biplot saved to: figures/Figure_S2_PCA_Biplot.png and .pdf")
    
    return X_pca

def plot_biodiversity(df):
    print("\n" + "="*50)
    print("4. GENERATING BIODIVERSITY VISUALIZATIONS")
    print("="*50)
    
    # Boxplot of Endemic Richness
    plt.figure(figsize=(8, 6))
    
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
    sns.boxplot(
        data=df, 
        x="Aquifer Type", 
        y="Endemics", 
        palette=colors,
        hue="Aquifer Type",
        legend=False,
        showfliers=False  # Hide extreme outliers to improve visual scaling
    )
    # Overlay individual data points for visibility
    sns.stripplot(
        data=df, 
        x="Aquifer Type", 
        y="Endemics", 
        color="black", 
        alpha=0.3, 
        jitter=0.2, 
        size=4
    )
    
    plt.xlabel("Spring Aquifer Type")
    plt.ylabel("Number of Endemic Taxa (#)")
    plt.title("Endemic Species Richness by Spring Type")
    
    plt.savefig("figures/Figure_1_Biodiversity_by_Type.png", dpi=300)
    plt.savefig("figures/Figure_1_Biodiversity_by_Type.pdf", dpi=300)
    plt.close()
    print("Biodiversity Boxplot saved to: figures/Figure_1_Biodiversity_by_Type.png and .pdf")

def plot_disturbance_correlations(df):
    # Correlation Matrix between disturbances, biological richness, and key environmental metrics
    cols = ["Diversion", "Equine", "Cattle", "Recreate", "Endemics", "Crenophilies", "Non Natives", "Temperature", "Conductivity"]
    corr = df[cols].corr()
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        corr, 
        annot=True, 
        cmap="coolwarm", 
        vmin=-1, 
        vmax=1, 
        fmt=".2f", 
        linewidths=0.5,
        cbar_kws={"label": "Pearson Correlation Coefficient"}
    )
    plt.title("Correlation Matrix: Disturbances, Biology, and Environment")
    
    plt.savefig("figures/Figure_2_Disturbance_Correlation.png", dpi=300)
    plt.savefig("figures/Figure_2_Disturbance_Correlation.pdf", dpi=300)
    plt.close()
    print("Disturbance Correlation Matrix saved to: figures/Figure_2_Disturbance_Correlation.png and .pdf")

def main():
    df = load_data()
    analyze_groups(df)
    run_pca_analysis(df)
    plot_biodiversity(df)
    plot_disturbance_correlations(df)
    print("\nAnalysis completed successfully!")

if __name__ == "__main__":
    main()
