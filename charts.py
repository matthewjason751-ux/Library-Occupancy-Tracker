#charts.py
#charts.py
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def show_occupancy_chart(parent, occupancy_data):
    """
    Displays a bar chart showing current occupancy
    for each library zone.

    occupancy_data format:

    {
        "Silent": {
            "capacity": 50,
            "occupied": 42
        },
        "General": {
            "capacity": 100,
            "occupied": 65
        },
        "Discussion": {
            "capacity": 30,
            "occupied": 12
        },
        "Computer": {
            "capacity": 40,
            "occupied": 38
        }
    }
    """

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

    x_positions = list(range(len(zones)))
    bar_width = 0.35

    capacity_positions = [
        position - bar_width / 2
        for position in x_positions
    ]

    occupied_positions = [
        position + bar_width / 2
        for position in x_positions
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

    axis.set_xticks(x_positions)
    axis.set_xticklabels(zones)

    axis.set_ylim(0, max(capacity_values) + 15)

    axis.legend()
    axis.grid(
        axis="y",
        linestyle="--",
        alpha=0.4
    )

    figure.tight_layout(
        rect=(0, 0.08, 1, 0.92)
    )

    chart = FigureCanvasTkAgg(
        figure,
        master=parent
    )

    chart.draw()

    chart_widget = chart.get_tk_widget()

    chart_widget.pack(
        fill="both",
        expand=True
    )

    return chart
