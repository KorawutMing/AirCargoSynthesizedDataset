import json
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd

def visualize_refinement(results_path="Forecasting/spatial_refinement_results.json"):
    with open(results_path, "r") as f:
        results = json.load(f)

    # Flatten results for plotting
    data = []
    for model, horizons in results.items():
        for h, metrics in horizons.items():
            # MAE Comparison
            orig_mae, ref_mae, imp_mae = metrics["MAE"]
            data.append({"Model": model, "Horizon": f"H={h}", "Type": "Original", "MAE": orig_mae})
            data.append({"Model": model, "Horizon": f"H={h}", "Type": "Spatial-Refined", "MAE": ref_mae})

    df = pd.DataFrame(data)
    
    # Create the plot
    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=False)
    horizons = ["H=1", "H=7", "H=30"]

    for i, h in enumerate(horizons):
        subset = df[df["Horizon"] == h]
        sns.barplot(data=subset, x="Model", y="MAE", hue="Type", ax=axes[i], palette="muted")
        axes[i].set_title(f"Forecasting Performance: {h}", fontsize=14, fontweight='bold')
        axes[i].set_ylabel("MAE (kg)")
        axes[i].set_xlabel("")
        axes[i].tick_params(axis='x', rotation=45)
        
        # Add improvement annotations
        for j, model in enumerate(sorted(results.keys())):
            h_num = h.split('=')[1]
            if h_num in results[model]:
                _, _, imp = results[model][h_num]["MAE"]
                color = "green" if imp > 0 else "red"
                axes[i].text(j, subset[subset["Model"] == model]["MAE"].max() * 1.05, 
                             f"{imp:+.1f}%", ha='center', color=color, fontweight='bold', fontsize=10)

    plt.tight_layout()
    output_path = "Forecasting/spatial_refinement_comparison.png"
    plt.savefig(output_path, dpi=300)
    print(f"Visualization saved to {output_path}")

if __name__ == "__main__":
    visualize_refinement()
