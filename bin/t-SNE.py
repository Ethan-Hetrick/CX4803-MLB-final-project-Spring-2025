import os
import numpy as np
import cupy as cp
import pandas as pd
from sklearn.manifold import TSNE
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# Load O-antigen training data (NEW FILE)
# ---------------------------------------------------------

o_antigen_df = pd.read_csv("./assets/o_antigen_1000_per_group.csv", header=None)
o_antigen_df.columns = ["sample_id", "o_antigen"]

print("O-antigen CSV preview:")
print(o_antigen_df.head())

# ---------------------------------------------------------
# Load k-mer arrays (with normalization)
# ---------------------------------------------------------

kmc7_arrays = os.path.expanduser("~/PROJECTS/GaTech/FCGR_classifier/salmonella_kmc7_arrays/")

def load_kmer_arrays(df, array_dir, suffix):
    arrays = []
    labels = []
    for idx, row in df.iterrows():

        sample_id = row["sample_id"]
        label = row["o_antigen"]    # <-- UPDATED LABEL

        array_path = os.path.join(array_dir, f"{sample_id}{suffix}.npy")

        if os.path.exists(array_path):
            array = np.load(array_path).flatten()

            # Normalize array to [0, 1]
            max_val = array.max()
            if max_val > 0:
                array = array / max_val

            arrays.append(array)
            labels.append(label)
        else:
            print(f"Warning: Array file {array_path} not found.")

    return np.array(arrays), np.array(labels)

X_np, y_str = load_kmer_arrays(o_antigen_df, kmc7_arrays, "_k7_k7")

# ---------------------------------------------------------
# Move through CuPy → back to NumPy
# ---------------------------------------------------------

X_cp = cp.asarray(X_np)
X_for_tsne = cp.asnumpy(X_cp)

# ---------------------------------------------------------
# Compute t-SNE (PERPLEXITY = 99)
# ---------------------------------------------------------

tsne = TSNE(
    n_components=2,
    perplexity=999,
    learning_rate=1000,     # recommended for large perplexity
    init="pca",
    metric="cosine",
    random_state=42,
    early_exaggeration=200, # larger exaggeration helps clusters separate
    max_iter=5000,          
)


print("Running t-SNE… this may take a while.")
X_embedded = tsne.fit_transform(X_for_tsne)

# ---------------------------------------------------------
# Encode O-antigen strings to integers
# ---------------------------------------------------------

le = LabelEncoder()
y_numeric = le.fit_transform(y_str)
class_names = le.classes_
num_classes = len(class_names)

# ---------------------------------------------------------
# UNIQUE COLORS for every class (HSV)
# ---------------------------------------------------------

colors = plt.cm.hsv(np.linspace(0, 1, num_classes))

# ---------------------------------------------------------
# Plotting
# ---------------------------------------------------------

plt.figure(figsize=(14, 12))

scatter = plt.scatter(
    X_embedded[:, 0],
    X_embedded[:, 1],
    c=colors[y_numeric],   # <-- unique color per O-antigen group
    s=10,
    alpha=0.8
)

plt.title("t-SNE Projection of Salmonella k-mer Data (O-antigen Coloring)", fontsize=18)
plt.xlabel("t-SNE 1", fontsize=14)
plt.ylabel("t-SNE 2", fontsize=14)

# ---------------------------------------------------------
# Full legend with ALL O-antigen groups
# ---------------------------------------------------------

legend_handles = [
    plt.Line2D(
        [0], [0], marker="o",
        color=colors[i],
        linestyle="",
        markersize=6
    ) for i in range(num_classes)
]

plt.legend(
    legend_handles,
    class_names,
    title="O-antigen",
    bbox_to_anchor=(1.05, 1),
    loc="upper left",
    ncol=2,       # change to 3–4 if long legend
    fontsize=8
)

# ---------------------------------------------------------
# Save plot
# ---------------------------------------------------------

output_path = "tsne_o_antigen_full_legend.png"
plt.savefig(output_path, dpi=300, bbox_inches="tight")
plt.close()

print(f"t-SNE plot saved as: {output_path}")

