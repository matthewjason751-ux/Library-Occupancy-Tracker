# charts.py

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def show_occupancy_chart(parent, occupancy_data):
    """Display capacity and current occupancy for each library zone."""

    if not occupancy_data:
        return None

    zones = list(occupancy_data.keys())

    occupied_values = [
        occupancy_data[zone]["occupied"]
        for zone in zones
    ]

    capacity_values = [
        occupancy_data[zone]["capacity"]
        for zone in zones
    ]

    figure = Figure(
        figsize=(9, 3.8),
        dpi=100
    )

    axis = figure.add_subplot(111)

    positions = list(range(len(zones)))
    bar_width = 0.35

    capacity_positions = [
        position - bar_width / 2
        for position in positions
    ]

    occupied_positions = [
        position + bar_width / 2
        for position in positions
    ]

    axis.bar(
        capacity_positions,
        capacity_values,
        width=bar_width,
        color="#d9cbb8",
        label="Capacity"
    )

    axis.bar(
        occupied_positions,
        occupied_values,
        width=bar_width,
        color="#8b0033",
        label="Current Occupancy"
    )

    axis.set_title(
        "Library Occupancy by Zone",
        fontsize=14,
        fontweight="bold",
        pad=12
    )

    axis.set_xlabel("Library Zone")
    axis.set_ylabel("Number of Students")

    axis.set_xticks(positions)

    axis.set_xticklabels(
        zones,
        ha="center"
    )

    axis.set_ylim(
        0,
        max(capacity_values, default=0) + 15
    )

    axis.legend()

    axis.grid(
        axis="y",
        linestyle="--",
        alpha=0.4
    )

    figure.tight_layout()

    figure.subplots_adjust(
        left=0.08,
        right=0.98,
        bottom=0.18,
        top=0.90
    )

    chart = FigureCanvasTkAgg(
        figure,
        master=parent
    )

    chart.draw()

    chart.get_tk_widget().pack(
        fill="both",
        expand=True
    )

    return chart