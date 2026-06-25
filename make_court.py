import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.patches as patches

print("Building court diagram...")

# ---- Real-world half-court dimensions (in feet), matching the dataset's
# coordinate system: x = 0 to 20 (sideline to sideline),
# y = 0 (net) to 22 (baseline)
COURT_WIDTH = 20      # sideline to sideline
COURT_DEPTH = 22      # net to baseline (one half of the full 44 ft court)
KITCHEN_DEPTH = 7     # net to kitchen (NVZ) line
CENTERLINE_X = 10     # divides the two service boxes, only drawn from
                      # the kitchen line back to the baseline

# Add a small out-of-bounds buffer around the court so the background
# image has some breathing room, matching the -5 to 25 crop you used
# for the x-axis and the 0 to 25 crop for the y-axis in your heatmap.
BUFFER_LEFT = 5
BUFFER_RIGHT = 5
BUFFER_TOP = 0      # nothing above the net, since loc_y starts at 0 there
BUFFER_BOTTOM = 3   # a little room past the baseline

fig_width_ft = COURT_WIDTH + BUFFER_LEFT + BUFFER_RIGHT
fig_height_ft = COURT_DEPTH + BUFFER_TOP + BUFFER_BOTTOM

# Use a figure size proportional to real feet so nothing gets stretched
fig, ax = plt.subplots(figsize=(fig_width_ft / 2, fig_height_ft / 2))

# Full plotted area, including out-of-bounds buffer
x_min = -BUFFER_LEFT
x_max = COURT_WIDTH + BUFFER_RIGHT
y_min = -BUFFER_TOP
y_max = COURT_DEPTH + BUFFER_BOTTOM

# ---- Background (out-of-bounds) area: gray
ax.add_patch(patches.Rectangle(
    (x_min, y_min), x_max - x_min, y_max - y_min,
    facecolor="#9c9c9c", zorder=0
))

# ---- Full court (net to baseline): blue
ax.add_patch(patches.Rectangle(
    (0, 0), COURT_WIDTH, COURT_DEPTH,
    facecolor="#1f6fb2", edgecolor="white", linewidth=2, zorder=1
))

# ---- Kitchen / Non-Volley Zone (net to 7ft line): green
ax.add_patch(patches.Rectangle(
    (0, 0), COURT_WIDTH, KITCHEN_DEPTH,
    facecolor="#2e9e4f", edgecolor="white", linewidth=2, zorder=2
))

# ---- Net line (y = 0), drawn as a bold dark line right at the court edge
ax.plot([0, COURT_WIDTH], [0, 0], color="black", linewidth=4, zorder=3)

# ---- Centerline, only from the kitchen line back to the baseline
# (there is no centerline inside the kitchen in real pickleball courts)
ax.plot([CENTERLINE_X, CENTERLINE_X], [KITCHEN_DEPTH, COURT_DEPTH],
         color="white", linewidth=2, zorder=3)

# ---- Baseline (already drawn as the rectangle edge, but reinforce it)
ax.plot([0, COURT_WIDTH], [COURT_DEPTH, COURT_DEPTH],
         color="white", linewidth=2, zorder=3)

# Set exact axis limits to match the buffer area, so the saved image's
# pixel dimensions correspond precisely to the feet-based coordinate range
ax.set_xlim(x_min, x_max)
ax.set_ylim(y_max, y_min)  # inverted: y=0 (net) at top, baseline at bottom

ax.set_aspect("equal")
ax.axis("off")

plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

output_path = "court_diagram.png"
plt.savefig(output_path, dpi=150, facecolor="#9c9c9c")
print(f"Saved {output_path}")
print(f"Image represents x: {x_min} to {x_max}, y: {y_min} to {y_max} (feet)")
print("Remember this exact range when setting up the background image in Tableau.")
