import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.manifold import TSNE
from sklearn.neighbors import KNeighborsRegressor

# Ensure figures directory exists
os.makedirs("figures", exist_ok=True)

# Styling settings
sns.set_theme(style="ticks", context="talk")
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Calibri", "DejaVu Sans"],
    "figure.titlesize": 16,
    "axes.titlesize": 11,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "savefig.bbox": "tight"
})

def main():
    print("Loading dataset for t-SNE environmental grid...")
    df = pd.read_excel('Data_Table_S5.xlsx', header=[0, 1])
    df.columns = df.columns.get_level_values(0)
    
    features = ["Depth", "Width", "Temperature", "Conductivity", "pH", 
                "Emerge Cover", "Bank Cover", "Silt", "Sand", "Gravel", "Cobble",
                "Diversion", "Equine", "Cattle", "Recreate"]
                
    feature_labels = {
        "Depth": "Pool Depth (cm)",
        "Width": "Pool Width (m)",
        "Temperature": "Water Temp (°C)",
        "Conductivity": "Conductivity (µS/cm)",
        "pH": "pH",
        "Emerge Cover": "Emergent Cover %",
        "Bank Cover": "Bank Veg Cover %",
        "Silt": "Silt Substrate %",
        "Sand": "Sand Substrate %",
        "Gravel": "Gravel Substrate %",
        "Cobble": "Cobble Substrate %",
        "Diversion": "Water Diversion Index",
        "Equine": "Horse Disturbance Index",
        "Cattle": "Cattle Grazing Index",
        "Recreate": "Recreation Index"
    }
    
    # Scale features and compute t-SNE coordinates (exact same parameters as unsupervised_analysis.py)
    X = df[features].astype(float)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    print("Computing t-SNE coordinates for 1121 springs...")
    tsne = TSNE(n_components=2, perplexity=30, random_state=42, max_iter=1000)
    X_tsne = tsne.fit_transform(X_scaled)
    
    # Setup dense grid for background interpolation
    x_min, x_max = X_tsne[:, 0].min() - 2, X_tsne[:, 0].max() + 2
    y_min, y_max = X_tsne[:, 1].min() - 2, X_tsne[:, 1].max() + 2
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 150), np.linspace(y_min, y_max, 150))
    grid_points = np.c_[xx.ravel(), yy.ravel()]
    
    # 3 rows, 5 columns grid
    fig, axes = plt.subplots(3, 5, figsize=(24, 14), sharex=True, sharey=True)
    axes = axes.ravel()
    
    print("Painting t-SNE latent landscapes for each variable...")
    for idx, feat in enumerate(features):
        ax = axes[idx]
        val = df[feat].values
        
        # Fit KNN regressor to interpolate this variable across the t-SNE coordinates
        knn = KNeighborsRegressor(n_neighbors=25, weights='distance')
        knn.fit(X_tsne, val)
        
        # Predict on grid
        Z_grid = knn.predict(grid_points).reshape(xx.shape)
        
        # Paint the background contourf using viridis colormap
        v_min, v_max = val.min(), val.max()
        contour = ax.contourf(xx, yy, Z_grid, levels=15, cmap="viridis", alpha=0.25, vmin=v_min, vmax=v_max)
        
        # Plot observed spring coordinates shaped by aquifer type and sized by endemic richness
        aq_types = df["Aquifer Type"].values
        endemics = df["Endemics"].values
        sizes = 10 + endemics * 15  # Scale sizes by number of endemics
        
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
            last_scatter = ax.scatter(
                X_tsne[mask, 0], 
                X_tsne[mask, 1], 
                c=val[mask], 
                cmap="viridis", 
                vmin=v_min,
                vmax=v_max,
                s=sizes[mask], 
                marker=marker_dict[aq],
                alpha=0.55, 
                edgecolors="none",
                label=aq
            )
        
        # Add colorbar next to each panel
        cbar = fig.colorbar(last_scatter, ax=ax, fraction=0.046, pad=0.04)
        cbar.ax.tick_params(labelsize=8)
        
        ax.set_title(feature_labels[feat], fontsize=11, fontweight="bold", pad=6)
        ax.grid(True, linestyle="--", alpha=0.25)
        
        # Axis labeling only at boundaries to avoid clutter
        if idx >= 10:
            ax.set_xlabel("t-SNE Dimension 1", fontsize=8.5)
        if idx % 5 == 0:
            ax.set_ylabel("t-SNE Dimension 2", fontsize=8.5)
            
    fig.suptitle("Environmental Gradients Painted onto the t-SNE Latent Space\n(Continuous KNN-interpolated backgrounds overlaid with observed spring coordinates)", fontsize=16, fontweight="bold", y=0.98)
    
    # Add a unified legend for the shape/aquifer mapping at the bottom
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', markersize=10, label='Regional Aquifer'),
        Line2D([0], [0], marker='v', color='w', markerfacecolor='gray', markersize=10, label='Local Geothermal (Hot)'),
        Line2D([0], [0], marker='d', color='w', markerfacecolor='gray', markersize=10, label='Local Cold')
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=3, title="Aquifer Type Shapes", fontsize=11, title_fontsize=12, bbox_to_anchor=(0.5, 0.01))
    
    plt.tight_layout(rect=[0, 0.05, 1, 0.94])
    
    plt.savefig("figures/Figure_S1_tSNE_Environmental_Grid.png", dpi=300, bbox_inches="tight")
    plt.savefig("figures/Figure_S1_tSNE_Environmental_Grid.pdf", dpi=300, bbox_inches="tight")
    plt.close()
    
    print("Successfully generated t-SNE environmental grid: figures/Figure_S1_tSNE_Environmental_Grid.png and .pdf")

if __name__ == "__main__":
    main()
