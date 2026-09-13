peclet check code
```cpp

    int nx = nx_user;
    double dx = 1.0 / (nx - 1.0);
    int ny = nx;
    double dy = dx;

    double dx_needed = 2.0 * nu / u_bc;
    if (dx > dx_needed)
    {
        int nx_needed = static_cast<int>(std::ceil(1.0 / dx_needed)) + 1;
        std::cout << "dx is too big. Currently " << dx
                << ", needs to be " << dx_needed
                << " with " << nx_needed
                << " cells to satisfy the Peclet condition for central difference, "
                << "and to maintain even spacing. Use upwind differencing or refine the grid.\n"
                << "Solution will blow up if you proceed with current grid and central diff, so stopping calc\n";
        return 0;
    }

```

python checkerboard plot

```python
pressure_checkerboard, checkerboard_coefficient = pressure_checkerboard_component(p)
pressure_without_checkerboard = p - pressure_checkerboard
pressure_scale = np.max(np.abs(p))
relative_checkerboard = (
    np.max(np.abs(pressure_checkerboard)) / pressure_scale
    if pressure_scale > 0 else 0.0
)
print(
    f"Pressure checkerboard coefficient: {checkerboard_coefficient:.6e} "
    f"({relative_checkerboard:.3%} of max pressure)"
)

checkerboard_fig, checkerboard_axes = plt.subplots(1, 2, figsize=(10, 4))
checkerboard_data = (
    (pressure_checkerboard, "Extracted checkerboard mode"),
    (pressure_without_checkerboard, "Pressure without checkerboard mode"),
)
for axis, (field, title) in zip(checkerboard_axes, checkerboard_data):
    image = axis.imshow(field, origin="lower", cmap="bwr", aspect="equal")
    axis.set_title(title)
    axis.set_xlabel("x index")
    axis.set_ylabel("y index")
    checkerboard_fig.colorbar(image, ax=axis)

checkerboard_fig.suptitle("Pressure checkerboard diagnostic")
checkerboard_fig.tight_layout(rect=(0, 0, 1, 0.95))
checkerboard_fig.savefig(Path(__file__).parent.parent / "img" / f"pressure_checkerboard_re{reynolds_number}.png")
plt.show()


```

## TODO
- [x] modify the discret functions to use the matrices directly, this way you wont need to change the loop indices manualy
    - The matrix approach is way too confusing
- [x] Add validation 
- [] optimze speed?
- [] simplify plot script
- [] rename files from step11 to something more appropriate
- [] Add divergence and convergence checks
- [] Residual calculations