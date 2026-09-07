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
reynolds_number = (1.0 * u_bc ) / nu # Re=Dv/nu, D=1.0, nu=0.1, v from bc setting


def load_field(name):
    values = np.loadtxt(DATA / f"{name}.csv", delimiter=",", skiprows=1)
    rows = values[:, 0].astype(int)
    columns = values[:, 1].astype(int)
    field = np.zeros((rows.max() + 1, columns.max() + 1))
    field[rows, columns] = values[:, 2]
    return field


def load_residual_norms(name):
    # Read one row per timestep: timestep, L2 norm, infinity norm.
    values = np.loadtxt(DATA / f"{name}.csv", delimiter=",", skiprows=1)
    values = np.atleast_2d(values)
    return values[:, 0], values[:, 1], values[:, 2]


# Load and plot the final velocity and pressure fields.
fig, axes = plt.subplots(1, 3, figsize=(12, 4))
u = load_field("u")
v = load_field("v")
p = load_field("p")
X, Y = np.meshgrid(np.arange(u.shape[1]), np.arange(u.shape[0]))

for axis, name in zip(axes, ("u", "v", "p")):
    field = {"u": u, "v": v, "p": p}[name]
    # Use filled contours and contour lines to show each field.
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

# Optional velocity-vector overlay:
# axes[0].quiver(
#     X[::2, ::2], Y[::2, ::2], u[::2, ::2], v[::2, ::2],
#     color="white", edgecolor="black", linewidth=0.5
# )

fig.suptitle(f"2D Lid-Driven Cavity (Re = {reynolds_number:g})")
plt.tight_layout(rect=(0, 0, 1, 0.95))
plt.savefig(Path(__file__).parent.parent/"img"/f"output_Re_{reynolds_number}.png")
plt.show()

# Plot velocity magnitude separately from the component fields.
u_magnitude = np.sqrt(u**2 + v**2)
magnitude_fig, magnitude_axis = plt.subplots(figsize=(6, 5))
magnitude_levels = 15
magnitude_contours = magnitude_axis.contourf(
    x_coords, y_coords, u_magnitude, levels=magnitude_levels, cmap="turbo"
)
magnitude_axis.contour(
    x_coords, y_coords, u_magnitude,
    levels=magnitude_levels, colors="black", linewidths=0.5,
)
magnitude_axis.set_title("Velocity magnitude")
magnitude_axis.set_xlabel("x")
magnitude_axis.set_ylabel("y")
magnitude_axis.set_aspect("equal", adjustable="box")
magnitude_fig.colorbar(magnitude_contours, ax=magnitude_axis, label="|U|")
magnitude_fig.tight_layout()
magnitude_fig.savefig(Path(__file__).parent.parent / "img" / f"u_magnitude_re{reynolds_number}.png")
plt.show()

# Load timestep-indexed residual norms for both velocity components.
u_timesteps, u_l2, u_infinity = load_residual_norms("u_residual_norms")
v_timesteps, v_l2, v_infinity = load_residual_norms("v_residual_norms")

# Plot both norms for u and v on one logarithmic axis.
# Color identifies the component; line style identifies the norm.
residual_fig, residual_axis = plt.subplots(figsize=(10, 6))
residual_series = (
    (u_timesteps, u_l2, "u L2 norm", "C0", "-"),
    (u_timesteps, u_infinity, "u infinity norm", "C0", "--"),
    (v_timesteps, v_l2, "v L2 norm", "C1", "-"),
    (v_timesteps, v_infinity, "v infinity norm", "C1", "--"),
)

for timesteps, norms, label, color, linestyle in residual_series:
    # Stop the plotted curve before overflow values such as inf.
    finite_values = np.isfinite(norms)
    residual_axis.plot(
        timesteps[finite_values], norms[finite_values],
        label=label, color=color, linestyle=linestyle,
    )

residual_axis.set_yscale("log")
residual_axis.set_xlabel("timestep")
residual_axis.set_ylabel("norm")
residual_axis.set_title("Velocity residual norms")
residual_axis.grid(True, which="both", alpha=0.3)
residual_axis.legend()
residual_fig.tight_layout()
# Save residual history separately from the final-field figure.
residual_fig.savefig(Path(__file__).parent.parent / "img" / "residual_norms.png")
plt.show()

