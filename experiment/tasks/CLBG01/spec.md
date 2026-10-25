Simulate the orbits of the Sun and the four Jovian planets (Jupiter, Saturn, Uranus,
Neptune) as a gravitational n-body system and report the total energy of the system
before and after the simulation.

**Constants**

- `PI = 3.141592653589793`
- `SOLAR_MASS = 4 * PI * PI`
- `DAYS_PER_YEAR = 365.24`

**Initial state** (position `x, y, z`; velocity `vx, vy, vz`; `mass`). Velocities are
multiplied by `DAYS_PER_YEAR` and masses by `SOLAR_MASS`:

| Body | x | y | z | vx | vy | vz | mass |
|---|---|---|---|---|---|---|---|
| Sun | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| Jupiter | 4.84143144246472090e+00 | -1.16032004402742839e+00 | -1.03622044471123109e-01 | 1.66007664274403694e-03 | 7.69901118419740425e-03 | -6.90460016972063023e-05 | 9.54791938424326609e-04 |
| Saturn | 8.34336671824457987e+00 | 4.12479856412430479e+00 | -4.03523417114321381e-01 | -2.76742510726862411e-03 | 4.99852801234917238e-03 | 2.30417297573763929e-05 | 2.85885980666130812e-04 |
| Uranus | 1.28943695621391310e+01 | -1.51111514016986312e+01 | -2.23307578892655734e-01 | 2.96460137564761618e-03 | 2.37847173959480950e-03 | -2.96589568540237556e-05 | 4.36624404335156298e-05 |
| Neptune | 1.53796971148509165e+01 | -2.59193146099879641e+01 | 1.79258772950371181e-01 | 2.68067772490389322e-03 | 1.62824170038242295e-03 | -9.51592254519715870e-05 | 5.15138902046611451e-05 |

**Procedure**

1. Offset the momentum: compute the total momentum `p = sum(v_i * mass_i)` over all bodies
   and set the Sun's velocity to `-p / SOLAR_MASS`.
2. Print the total energy (see below).
3. Advance the system `N` times with time step `dt = 0.01`. One step:
   - For every pair of bodies `(i, j)` with `i < j`: let `d = position_i - position_j`,
     `dist = |d|`, `mag = dt / dist^3`; then
     `v_i -= d * mass_j * mag` and `v_j += d * mass_i * mag`.
   - Then, for every body: `position += dt * v`.
4. Print the total energy again.

**Total energy** = sum over bodies of `0.5 * mass * |v|^2`, minus, for every pair `(i, j)`
with `i < j`, `mass_i * mass_j / |position_i - position_j|`.

Use double-precision (64-bit) floating point. Print each energy on its own line with
exactly 9 digits after the decimal point.

**Example:** for `N = 1000` the output is

```
-0.169075164
-0.169087605
```
