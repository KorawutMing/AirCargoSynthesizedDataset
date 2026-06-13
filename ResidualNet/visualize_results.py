import json
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd

def visualize_refinement(results_path="ResidualNet/results/spatial_refinement_results.json"):
    with open(results_path, "r") as f:
        results = json.load(f)

    data = []
    for model, horizons in results.items():
        for h, metrics in horizons.items():
            r_o, r_r, r_i = metrics["RMSE"]
            data.append({"Model": model, "Horizon": f"H={h}", "Type": "Original", "RMSE": r_o, "Imp": r_i})
            data.append({"Model": model, "Horizon": f"H={h}", "Type": "Refined", "RMSE": r_r, "Imp": r_i})

    df = pd.DataFrame(data)
    if df.empty:
        print("No results to visualize.")
        return

    sns.set_theme(style="whitegrid")
    horizons = sorted(df["Horizon"].unique(), key=lambda x: int(x.split('=')[1]))
    fig, axes = plt.subplots(1, len(horizons), figsize=(7 * len(horizons), 7))
    if len(horizons) == 1: axes = [axes]

    for i, h in enumerate(horizons):
        subset = df[df["Horizon"] == h]
        sns.barplot(data=subset, x="Model", y="RMSE", hue="Type", ax=axes[i], palette=["#808080", "#2ecc71"])
        axes[i].set_title(f"RMSE Performance: {h}", fontsize=15, fontweight='bold')
        axes[i].set_ylabel("RMSE (kg)")
        axes[i].tick_params(axis='x', rotation=45)
        
        # Add labels
        models_in_h = sorted(subset["Model"].unique())
        for j, model in enumerate(models_in_h):
            h_num = h.split('=')[1]
            if model in results and h_num in results[model]:
                imp = results[model][h_num]["RMSE"][2]
                color = "green" if imp > 0 else "black"
                y_pos = subset[subset["Model"] == model]["RMSE"].max() * 1.02
                axes[i].text(j, y_pos, f"{imp:+.1f}%", ha='center', color=color, fontweight='bold', fontsize=11)

    plt.tight_layout()
    plt.savefig("ResidualNet/results/spatial_refinement_comparison.png", dpi=300)
    print("Visualization updated: ResidualNet/results/spatial_refinement_comparison.png")

if __name__ == "__main__":
    visualize_refinement()
