import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.cluster.hierarchy import linkage, optimal_leaf_ordering, dendrogram
from scipy.spatial.distance import squareform

def main():
    df = pd.read_excel('Data_Table_S5.xlsx', header=[0, 1])
    df.columns = df.columns.get_level_values(0)
    reg = df[df['Aquifer Type'] == 'Regional Aq']
    biological_vars = ['Endemics', 'Crenophilies', 'Springsnails', 'Non Natives', 'Native Fish']
    label_mapping = {
        'Endemics': 'Endemic Richness',
        'Crenophilies': 'Crenophile Richness',
        'Springsnails': 'Springsnail Richness',
        'Non Natives': 'Non-Native Richness',
        'Native Fish': 'Native Fish Richness'
    }
    corr = reg[biological_vars].corr(method='spearman')
    dist = 1.0 - corr
    condensed = squareform(dist.values - np.diag(np.diag(dist.values)))
    Z = linkage(condensed, method='average')
    Z_ordered = optimal_leaf_ordering(Z, condensed)
    
    dend = dendrogram(Z_ordered, no_plot=True)
    leaves = dend['leaves']
    ordered_taxa = [biological_vars[i] for i in leaves]
    ordered_corr = corr.loc[ordered_taxa, ordered_taxa]
    ordered_labels = [label_mapping[t] for t in ordered_taxa]
    
    fig = plt.figure(figsize=(13.5, 7.5))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 5.5], wspace=0.35)
    
    ax_heat = fig.add_subplot(gs[1])
    ax_dend = fig.add_subplot(gs[0], sharey=ax_heat)
    
    dend_plot = dendrogram(
        Z_ordered,
        orientation='left',
        labels=ordered_labels,
        ax=ax_dend,
        color_threshold=0,
        above_threshold_color='darkblue'
    )
    
    print(f"Number of collections: {len(ax_dend.collections)}")
    print(f"Number of lines: {len(ax_dend.lines)}")
    
    # Scale both lines and collections
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
        
    # Heatmap
    sns.heatmap(
        ordered_corr,
        annot=True,
        cmap="Blues",
        vmin=0,
        vmax=1.0,
        fmt=".3f",
        cbar_kws={"label": "Spearman Correlation ($r_s$)", "orientation": "horizontal", "pad": 0.18, "shrink": 0.6},
        ax=ax_heat,
        square=True,
        cbar=True,
        linewidths=1.5,
        linecolor="white"
    )
    
    # y-limits running from 5.0 to 0.0 (top-to-bottom)
    ax_heat.set_ylim(5.0, 0.0)
    
    # Remove ticks and spines
    ax_dend.set_axis_off()
    
    # Adjust ax_dend position to match ax_heat height and vertical position
    fig.canvas.draw()
    pos_heat = ax_heat.get_position()
    pos_dend = ax_dend.get_position()
    ax_dend.set_position([pos_dend.x0, pos_heat.y0, pos_dend.width, pos_heat.height])
    
    # Set the x-limit of dendrogram to show the branches correctly (distance ranges from 0 to about 1.0)
    # The default distance runs from max distance down to 0 at the leaves.
    # Since orientation='left', leaves are at x=0 (right side of ax_dend) and the root is on the left.
    # SciPy dendrogram orientation='left' places leaves at x=0 and branches extend in positive x direction.
    # Wait, let's verify where leaves are.
    # Let's inspect coordinates of segments.
    for i, col in enumerate(ax_dend.collections):
        segs = col.get_segments()
        if len(segs) > 0:
            print(f"Collection {i} x-range: {np.min([np.min(s[:, 0]) for s in segs])} to {np.max([np.max(s[:, 0]) for s in segs])}")
            
    plt.savefig("scratch/test_cooccurrence_aligned.png", dpi=300, bbox_inches="tight")
    print("Saved test plot to scratch/test_cooccurrence_aligned.png")

if __name__ == "__main__":
    main()
