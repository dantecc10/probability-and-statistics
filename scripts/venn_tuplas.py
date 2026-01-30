import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Use mathtext rendering instead of full LaTeX
plt.rcParams['text.usetex'] = False
plt.rcParams['mathtext.fontset'] = 'dejavusans'

# Define the sets with tuples
set_a = {(3, 6), (4, 5), (4, 6), (5, 4), (5, 5), (5, 6), (6, 3), (6, 4), (6, 5), (6, 6)}
set_b = {(1, 2), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (3, 2), (4, 2), (5, 2), (6, 2)}
set_c = {(5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6)}

# Create figure and axis
fig, ax = plt.subplots(figsize=(14, 12), dpi=100)
ax.set_xlim(-2, 2)
ax.set_ylim(-2, 2)
ax.set_aspect('equal')
ax.axis('off')

# Calculate positions of circles at 120° intervals
radius = 1.2
center_x, center_y = 0, 0
angles = [90, 210, 330]  # degrees
circle_distance = 0.7

centers = []
for angle in angles:
    rad = np.radians(angle)
    x = center_x + circle_distance * np.cos(rad)
    y = center_y + circle_distance * np.sin(rad)
    centers.append((x, y))

# Draw circles
circle_radius = 0.9
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
alphas = [0.2, 0.2, 0.2]

for i, (center, color, alpha) in enumerate(zip(centers, colors, alphas)):
    circle = patches.Circle(center, circle_radius, fill=True, 
                           facecolor=color, edgecolor='black', 
                           linewidth=2, alpha=alpha, zorder=1)
    ax.add_patch(circle)

# Calculate regions
subsets_map = {
    '100': set_a - set_b - set_c,  # Only A
    '010': set_b - set_a - set_c,  # Only B
    '001': set_c - set_a - set_b,  # Only C
    '110': (set_a & set_b) - set_c,  # A and B, not C
    '101': (set_a & set_c) - set_b,  # A and C, not B
    '011': (set_b & set_c) - set_a,  # B and C, not A
    '111': set_a & set_b & set_c,  # All three
}

# Positions for text in each region
# Adjusted for symmetrical placement
text_positions = {
    '100': (centers[0][0] - 0.35, centers[0][1]),  # Top-left
    '010': (centers[1][0] + 0.35, centers[1][1]),  # Bottom-left
    '001': (centers[2][0] + 0.35, centers[2][1]),  # Bottom-right
    '110': (centers[0][0] * 0.5 + centers[1][0] * 0.5, 
            centers[0][1] * 0.5 + centers[1][1] * 0.5),  # Between A and B
    '101': (centers[0][0] * 0.5 + centers[2][0] * 0.5, 
            centers[0][1] * 0.5 + centers[2][1] * 0.5),  # Between A and C
    '011': (centers[1][0] * 0.5 + centers[2][0] * 0.5, 
            centers[1][1] * 0.5 + centers[2][1] * 0.5),  # Between B and C
    '111': (center_x, center_y),  # Center
}

# Label positions
label_positions = {
    '100': (centers[0][0] - 0.55, centers[0][1] + 0.55),
    '010': (centers[1][0] - 0.55, centers[1][1] - 0.55),
    '001': (centers[2][0] + 0.55, centers[2][1] - 0.55),
}

labels = ['A', 'B', 'C']
for i, (label, pos) in enumerate(zip(labels, label_positions.values())):
    ax.text(pos[0], pos[1], label, fontsize=16, fontweight='bold', zorder=10)

# Add text for each region
for subset_id, elements in subsets_map.items():
    pos = text_positions[subset_id]
    if elements:
        # Format as mathtext
        elements_str = ', '.join(f'({e[0]}, {e[1]})' for e in sorted(elements))
        label_text = f'$\\{{{elements_str}\\}}$'
    else:
        label_text = '$\emptyset$'
    ax.text(pos[0], pos[1], label_text, fontsize=7, ha='center', va='center', 
           zorder=5)

# Add title
plt.title('Venn Diagram of Sets A, B, C', fontsize=16, fontweight='bold', pad=20)

# Adjust layout to prevent label cutoff
plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)

# Display the plot
plt.show()
