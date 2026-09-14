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

## TODO
- [x] modify the discret functions to use the matrices directly, this way you wont need to change the loop indices manualy
    - The matrix approach is way too confusing
- [x] Add validation 
- [x] optimze speed?
    - Not the biggest concern
- [x] rename files from step11 to something more appropriate
- [x] Error reduction methods
    - Implement central diff for the velocity terms instead of upwind scheme. This will also require a check on Peclet number, for which use the code above
    - Not implementing, just noting