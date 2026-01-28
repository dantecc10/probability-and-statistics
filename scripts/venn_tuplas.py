import matplotlib.pyplot as plt
from matplotlib_venn import venn3

# Define the sets with tuples
set_a = {(3, 6), (4, 5), (4, 6), (5, 4), (5, 5), (5, 6), (6, 3), (6, 4), (6, 5), (6, 6)}
set_b = {(1, 2), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (3, 2), (4, 2), (5, 2), (6, 2)}
set_c = {(5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6)}

# Generate the Venn diagram
venn = venn3([set_a, set_b, set_c], set_labels=('A', 'B', 'C'))

# Dictionary mapping subset identifiers to their elements
subsets_map = {
    '100': set_a - set_b - set_c,
    '010': set_b - set_a - set_c,
    '001': set_c - set_a - set_b,
    '110': (set_a & set_b) - set_c,
    '101': (set_a & set_c) - set_b,
    '011': (set_b & set_c) - set_a,
    '111': set_a & set_b & set_c,
}

# Update labels to show elements instead of counts
for subset_id, elements in subsets_map.items():
    if venn.get_label_by_id(subset_id):
        # Format tuples as strings
        label_text = '\n'.join(str(elem) for elem in sorted(elements)) if elements else ''
        venn.get_label_by_id(subset_id).set_text(label_text)

# Add a title
plt.title('Venn Diagram of Sets A, B, C')

# Display the plot
plt.show()
