
# Step 11: Pressure and Source-Term Equations

The velocity field is defined on a two-dimensional grid. Let $i$ denote the
coordinate in the $x$ direction and $j$ the coordinate in the $y$ direction.
The grid spacings are $\Delta x$ and $\Delta y$, and the time step is
$\Delta t$.

## Source term $b$

The code constructs the source term from the continuity equation and the
velocity derivatives:

$$
b_{j,i} = \rho \left[
\frac{1}{\Delta t}
\left(\frac{\partial u}{\partial x}+
\frac{\partial v}{\partial y}\right)
- \left(\frac{\partial u}{\partial x}\right)^2
- 2\frac{\partial u}{\partial y}\frac{\partial v}{\partial x}
- \left(\frac{\partial v}{\partial y}\right)^2
\right]_{j,i}.
$$

The first derivatives use central differences:

$$
\left(\frac{\partial u}{\partial x}\right)_{j,i}
\approx \frac{u_{j,i+1}-u_{j,i-1}}{2\Delta x},
\qquad
\left(\frac{\partial u}{\partial y}\right)_{j,i}
\approx \frac{u_{j+1,i}-u_{j-1,i}}{2\Delta y},
$$

$$
\left(\frac{\partial v}{\partial x}\right)_{j,i}
\approx \frac{v_{j,i+1}-v_{j,i-1}}{2\Delta x},
\qquad
\left(\frac{\partial v}{\partial y}\right)_{j,i}
\approx \frac{v_{j+1,i}-v_{j-1,i}}{2\Delta y}.
$$

## Pressure Poisson equation

The usual pressure equation is

$$
\frac{\partial^2 p}{\partial x^2}
+ \frac{\partial^2 p}{\partial y^2}
= b.
$$

Using second-order central differences gives

$$
\frac{p_{j,i+1}-2p_{j,i}+p_{j,i-1}}{\Delta x^2}
+
\frac{p_{j+1,i}-2p_{j,i}+p_{j-1,i}}{\Delta y^2}
= b_{j,i},
$$

The implementation's `b` already contains the factor $\rho$:

$$
p_{j,i} =
\frac{\Delta x^2\Delta y^2}{2(\Delta x^2+\Delta y^2)}
\left[
\frac{p_{j,i+1}+p_{j,i-1}}{\Delta x^2}
+\frac{p_{j+1,i}+p_{j-1,i}}{\Delta y^2}
-\rho b_{j,i}
\right].
$$

This update is repeated `nit` times. Since the code updates `p` in place, each
iteration uses newly updated neighboring values when they are available.

## Pressure boundary conditions

After every pressure iteration, the following boundary conditions are applied:

$$
\left.\frac{\partial p}{\partial x}\right|_{x=0}=0,
\qquad
\left.\frac{\partial p}{\partial x}\right|_{x=2}=0,
$$

$$
\left.\frac{\partial p}{\partial y}\right|_{y=0}=0,
\qquad
p\big|_{y=2}=0.
$$

The zero-gradient conditions are implemented by copying the adjacent interior
row or column. The top boundary pressure is set to zero.

## Velocity update

After calculating the pressure, the code advances the velocity fields by one
time step using the incompressible Navier--Stokes equations:

$$
u_{j,i}^{n+1} = u_{j,i}^{n} + \Delta t
\left[
-u\frac{\partial u}{\partial x}
-v\frac{\partial u}{\partial y}
-\frac{1}{\rho}\frac{\partial p}{\partial x}
+\nu\left(\frac{\partial^2u}{\partial x^2}
+\frac{\partial^2u}{\partial y^2}\right)
\right]_{j,i},
$$

$$
v_{j,i}^{n+1} = v_{j,i}^{n} + \Delta t
\left[
-u\frac{\partial v}{\partial x}
-v\frac{\partial v}{\partial y}
-\frac{1}{\rho}\frac{\partial p}{\partial y}
+\nu\left(\frac{\partial^2v}{\partial x^2}
+\frac{\partial^2v}{\partial y^2}\right)
\right]_{j,i}.
$$

The convective first derivatives use backward differences, while pressure
gradients use central differences:

$$
\frac{\partial u}{\partial x}\approx
\frac{u_{j,i}-u_{j,i-1}}{\Delta x},
\qquad
\frac{\partial u}{\partial y}\approx
\frac{u_{j,i}-u_{j-1,i}}{\Delta y},
$$

with the same pattern for $v$. The second derivatives use central differences:

$$
\frac{\partial^2u}{\partial x^2}\approx
\frac{u_{j,i+1}-2u_{j,i}+u_{j,i-1}}{\Delta x^2},
\qquad
\frac{\partial^2u}{\partial y^2}\approx
\frac{u_{j+1,i}-2u_{j,i}+u_{j-1,i}}{\Delta y^2},
$$

and identically for $v$.

Next up, to verify with ghia et al