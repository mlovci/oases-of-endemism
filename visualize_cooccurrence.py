import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.cluster.hierarchy import linkage, optimal_leaf_ordering, dendrogram
from scipy.spatial.distance import squareform

# Set styling for publication-quality plots
sns.set_theme(style="ticks", context="talk")
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Calibri", "DejaVu Sans"],
    "figure.titlesize": 14,
    "axes.titlesize": 12,
    "axes.labelsize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "savefig.bbox": "tight"
})

def main():
    print("Loading dataset for co-occurrence analysis of 5 biological variables...")
    df = pd.read_excel('Data_Table_S5.xlsx', header=[0, 1])
    df.columns = df.columns.get_level_values(0)
    
    # Filter to Regional Aquifer Springs (the stable thermal oases of endemism)
    reg = df[df['Aquifer Type'] == 'Regional Aq']
    
    # 5 biological variables to cluster
    biological_vars = ['Endemics', 'Crenophilies', 'Springsnails', 'Non Natives', 'Native Fish']
    label_mapping = {
        'Endemics': 'Endemic Richness',
        'Crenophilies': 'Crenophile Richness',
        'Springsnails': 'Springsnail Richness',
        'Non Natives': 'Non-Native Richness',
        'Native Fish': 'Native Fish Richness'
    }
    
    # 1. Compute Spearman correlation matrix
    corr = reg[biological_vars].corr(method='spearman')
    
    # 2. Perform average-linkage hierarchical clustering with OLO
    dist = 1.0 - corr
    condensed = squareform(dist.values - np.diag(np.diag(dist.values))) # ensure diagonal is exactly 0 distance
    Z = linkage(condensed, method='average')
    Z_ordered = optimal_leaf_ordering(Z, condensed)
    
    # Extract OLO leaf ordering
    dend = dendrogram(Z_ordered, no_plot=True)
    leaves = dend['leaves']
    ordered_taxa = [biological_vars[i] for i in leaves]
    
    # Re-order correlation matrix
    ordered_corr = corr.loc[ordered_taxa, ordered_taxa]
    ordered_labels = [label_mapping[t] for t in ordered_taxa]
    
    # 3. Setup Matplotlib Grid (Left: Dendrogram, Right: Heatmap + Drivers Panel)
    fig = plt.figure(figsize=(13.5, 7.5))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 5.5], wspace=0.35)
    
    ax_heat = fig.add_subplot(gs[1])
    ax_dend = fig.add_subplot(gs[0], sharey=ax_heat)
    
    # 4. Plot Left Dendrogram (horizontally pointing left)
    dend_plot = dendrogram(
        Z_ordered,
        orientation='left',
        labels=ordered_labels,
        ax=ax_dend,
        color_threshold=0,
        above_threshold_color='darkblue'
    )
    
    # Align dendrogram leaves (y: 5 to 45) with heatmap rows (y: 0.5 to 4.5)
    # Since SciPy dendrogram plots them as a LineCollection, we scale the y-segments.
    for collection in ax_dend.collections:
        segments = collection.get_segments()
        new_segments = []
        for seg in segments:
            new_seg = seg.copy()
            new_seg[:, 1] = seg[:, 1] / 10.0
            new_segments.append(new_seg)
        collection.set_segments(new_segments)
        
    for line in ax_dend.lines:
        ydata = line.get_ydata()
        line.set_ydata(ydata / 10.0)
        
    ax_dend.set_axis_off()
    
    # 5. Plot Heatmap
    sns.heatmap(
        ordered_corr,
        annot=True,
        cmap="Blues",
        vmin=0,
        vmax=1.0,
        fmt=".3f",
        cbar_kws={"label": "Spearman Correlation ($r_s$)", "orientation": "horizontal", "pad": 0.28, "shrink": 0.6},
        ax=ax_heat,
        square=True,
        cbar=True,
        linewidths=1.5,
        linecolor="white"
    )
    
    # Force ax_dend to match the vertical position and height of ax_heat physically
    # (since sns.heatmap(square=True) squishes ax_heat vertically)
    fig.canvas.draw()
    pos_heat = ax_heat.get_position()
    pos_dend = ax_dend.get_position()
    ax_dend.set_position([pos_dend.x0, pos_heat.y0, pos_dend.width, pos_heat.height])
    
    # Position row and column tick labels
    ax_heat.set_xticks(np.arange(len(ordered_labels)) + 0.5)
    ax_heat.set_xticklabels(ordered_labels, rotation=40, ha='right', fontsize=9.5, fontweight='bold')
    
    ax_heat.set_yticks(np.arange(len(ordered_labels)) + 0.5)
    ax_heat.set_yticklabels(ordered_labels, rotation=0, fontsize=9.5, fontweight='bold', va='center')
    
    ax_heat.set_ylabel("")
    ax_heat.set_xlabel("")
    
    # Set x-limits to reserve blank space on the right for drivers
    ax_heat.set_xlim(0, 9.2)
    ax_heat.set_ylim(5.0, 0.0)
    
    # 6. Annotate environmental drivers on the right of the heatmap
    # Green = Positive correlation, Red = Negative correlation, Orange = Disturbance
    drivers_mapping = {
        'Endemics': [
            ("+Pool Depth", "green"),
            ("-Siltation", "red"),
            ("+Diversion", "orange")
        ],
        'Crenophilies': [
            ("+Pool Depth", "green"),
            ("-Siltation", "red"),
            ("+Water Temp", "green")
        ],
        'Springsnails': [
            ("+Water Temp", "green"),
            ("+Sand Substrate", "green"),
            ("+Pool Depth", "green")
        ],
        'Non Natives': [
            ("+Pool Depth", "green"),
            ("-Siltation", "red"),
            ("+Diversion", "orange")
        ],
        'Native Fish': [
            ("+Pool Depth", "green"),
            ("-Siltation", "red"),
            ("-Emergent Cover", "red")
        ]
    }
    
    x_base = 5.25
    for row_idx, taxon in enumerate(ordered_taxa):
        drivers = drivers_mapping[taxon]
        y_pos = row_idx + 0.5
        
        # Label the header "Top Drivers:"
        ax_heat.text(x_base, y_pos - 0.15, "Top Drivers:", color="gray", fontsize=8, fontstyle="italic", va="center", ha="left")
        
        # Write each driver in its own color box side-by-side
        x_offset = 0.0
        for driver_text, color in drivers:
            text_obj = ax_heat.text(
                x_base + x_offset,
                y_pos + 0.18,
                driver_text,
                color=color,
                fontsize=8.5,
                fontweight="bold",
                va="center",
                ha="left"
            )
            # Premium rounded background patch
            text_obj.set_bbox(dict(facecolor="#f5f5f5", edgecolor="none", alpha=0.9, boxstyle="round,pad=0.25"))
            x_offset += 1.3  # Safe horizontal increment in data units to prevent overlapping
            
    # Add title and adjust layout
    ax_heat.set_title("OLO Hierarchical Clustering of Biological Taxa Co-occurrence\n(Regional Aquifer stable thermal springs, N = 45)", pad=15, fontsize=12, fontweight='bold')
    
    # Ensure folder exists and save
    os.makedirs("figures", exist_ok=True)
    plt.savefig("figures/Figure_7_Biological_Cooccurrence.png", dpi=300, bbox_inches="tight")
    plt.savefig("figures/Figure_7_Biological_Cooccurrence.pdf", dpi=300, bbox_inches="tight")
    plt.close()
    
    print("Successfully generated OLO Co-occurrence plot: figures/Figure_7_Biological_Cooccurrence.png and .pdf")

if __name__ == "__main__":
    main()
