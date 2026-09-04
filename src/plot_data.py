import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

DATA = Path(__file__).parent.parent / "data"
SOURCE = Path(__file__).with_name("step11.cpp")


def read_cpp_parameter(name):
    source = SOURCE.read_text()
    match = re.search(rf"double\s+{name}\s*=\s*([0-9.eE+-]+)\s*;", source)
    if match is None:
        raise ValueError(f"Could not find {name} in {SOURCE}")
    return float(match.group(1))


# rho = read_cpp_parameter("rho")
nu = read_cpp_parameter("nu")
u_bc = read_cpp_parameter("u_bc")
reynolds_number = (1.0 * u_bc ) / nu


def load_field(name):
    values = np.loadtxt(DATA / f"{name}.csv", delimiter=",", skiprows=1)
    rows = values[:, 0].astype(int)
    columns = values[:, 1].astype(int)
    field = np.zeros((rows.max() + 1, columns.max() + 1))
    field[rows, columns] = values[:, 2]
    return field


fig, axes = plt.subplots(1, 3, figsize=(12, 4))
u = load_field("u")
v = load_field("v")
p = load_field("p")
X, Y = np.meshgrid(np.arange(u.shape[1]), np.arange(u.shape[0]))

for axis, name in zip(axes, ("u", "v", "p")):
    field = {"u": u, "v": v, "p": p}[name]
    # Add filled contours and contour lines
    y_coords = np.linspace(0, 1, field.shape[0])
    x_coords = np.linspace(0, 1, field.shape[1])
    contour_levels = 15
    cf = axis.contourf(x_coords, y_coords, field, levels=contour_levels, cmap="turbo")
    axis.contour(x_coords, y_coords, field, colors="black", levels=contour_levels, linewidths=0.5)
    axis.set_title(name)
    axis.set_xlabel("x")
    axis.set_ylabel("y")
    axis.set_aspect("equal", adjustable="box")
    axis.set_xticks(np.linspace(0, 1, 5))
    axis.set_yticks(np.linspace(0, 1, 5))
    fig.colorbar(cf, ax=axis)

# axes[0].quiver(
#     X[::2, ::2], Y[::2, ::2], u[::2, ::2], v[::2, ::2],
#     color="white", edgecolor="black", linewidth=0.5
# )

fig.suptitle(f"2D Lid-Driven Cavity (Re = {reynolds_number:g})")
plt.tight_layout(rect=(0, 0, 1, 0.95))
plt.savefig(Path(__file__).parent.parent/"img"/f"output_Re_{reynolds_number}.png")
plt.show()
