import matplotlib.pyplot as plt
from matplotlib_venn import venn3

# Sample data
set_a = set(['John', 'Amy', 'Howard', 'Alice', 'George', 'Jacob'])
set_b = set(['Arthur', 'Alice', 'Ron', 'Penny', 'Sheldon', 'John'])
set_c = set(['Amy', 'Leo', 'Ash', 'Brandon', 'Alice', 'Ron'])

# Generate the Venn diagram
venn = venn3([set_a, set_b, set_c], set_labels=('Set A', 'Set B', 'Set C'))

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
        label_text = '\n'.join(sorted(elements)) if elements else ''
        venn.get_label_by_id(subset_id).set_text(label_text)

# Add a title
plt.title('Venn Diagram of Three Sets')

# Display the plot
plt.show()
