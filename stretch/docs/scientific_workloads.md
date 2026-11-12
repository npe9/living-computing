# Scientific workloads on the model: a plan

Added 2026-11-12 at the owner's request, from a proposal the owner supplied
(the text in §2-§5 below is that proposal, kept close to its own words).
§1 places it in the project: when it can start, what it depends on, and the
project rules it has to follow. NEXT.md carries the pointer.

## 1. Where this sits in the project

**When.** After FORTRAN IV. The standing order is: SMAC I and STRAP II,
then FORTRAN IV, then this work. Level 3 below (§4) is the project's own
goal, a FORTRAN job compiled and run under MCP on the cycle-accurate model.
Nothing here starts until a FORTRAN deck compiles. Until then, at most
§1's searches and the gfortran oracles (level 1) can be prepared.

**Dependencies, as of 2026-11-12:**
- *The compiler.* The FORTRAN IV manual (C22-6751, May 1963, 37 pp.) is in
  docs/. No compiler listing has been found (archival_inventory.md,
  the C22-6751 entry and its search notes). Without it, level 3 waits on
  either a find or a labelled RECONSTRUCTION.
- *Loader and runtime.* The relocatable path exists today. MCP's loader runs
  a STRAP II FORTRAN deck as a BSS job (NEXT.md, "BSS on MCP's loader"). The
  FORTRAN library (I/O, the math routines) is not in hand.
- *Timing.* An execution-time estimate needs G1's documented instruction
  timings (microarchitecture_plan.md). Until the model is cycle-accurate, a
  model cycle count is not a 7030 time.

**Rules this work follows (AGENTS.md, the fidelity goal):**
- *IBM's and the laboratories' programs first.* Before writing any of the six
  programs, search for surviving 7030 FORTRAN or STRAP programs from LASL,
  LRL Livermore, AWRE Aldermaston, NSA (Harvest), MITRE, the Weather Bureau,
  Dahlgren and Rice, and record each search in archival_inventory.md. A
  recovered program outranks a new one. A new one is labelled as such:
  "representative of the workload class, not recovered from a Stretch
  installation" (the proposal's own caveat).
- *gfortran is scaffolding.* Level 1 gives oracles and expected results. It
  is never the target.
- *Other machines.* The 704 / STAR-100 / Cray-1 comparison (§5) is research
  only: citations and numbers in stretch/docs/, no code in a sibling
  directory, and only after Stretch is finished.
- *Verification.* Every workload gets a check in tests/run_tests.sh with a
  measured injection, like everything else here.

## 2. Six workloads

These are historically representative workload classes. The example
programs were not recovered from Stretch installations.

| Workload | Historical relevance | Computational characteristics | Difficulty |
|---|---|---|---|
| 1D shock-wave simulation | Nuclear weapons hydrodynamics | Arrays, finite differences, time stepping | Medium |
| Neutron diffusion | Reactor and weapons physics | Stencils, iterative solvers | Medium |
| Monte Carlo particle transport | Radiation physics | Random numbers, branching, statistics | Medium |
| Equation-of-state tables | High-pressure material physics | Interpolation, numerical integration | Easy |
| N-body gravitational simulation | Astronomy and orbital mechanics | Floating-point arithmetic, nested loops | Easy |
| Matrix inversion / linear systems | General scientific computing | Dense linear algebra, memory access | Easy-Medium |

### 2.1 Hydrodynamics: a 1D shock tube

A tube holds gas at two pressures, separated by a diaphragm. The diaphragm is
removed and a shock travels down the tube. The Euler equations:

    d(rho)/dt     + d(rho u)/dx         = 0
    d(rho u)/dt   + d(rho u^2 + p)/dx   = 0
    dE/dt         + d(u (E + p))/dx     = 0

A period-style fragment (a continuity update only, not a stable solver):

          DIMENSION RHO(200),VEL(200),PRS(200)
          DIMENSION RN(200),UN(200),PN(200)
          DO 100 I=2,199
             RN(I)=RHO(I)-DT*(RHO(I+1)*VEL(I+1)
         1                   -RHO(I-1)*VEL(I-1))/(2.0*DX)
      100 CONTINUE

Experiments:
- mesh 50 to 200 cells;
- methods and stability;
- time per step;
- floating-point sensitivity;
- single against double precision.

The architectural question: does look-ahead keep the arithmetic units busy
through repeated array operations? On the model this is answerable from
G1's cycle-accurate pipeline (microarchitecture_plan.md §1a).

### 2.2 Neutron diffusion

The steady-state equation is -D lap(phi) + Sigma_a phi = S. It is solved in 2D
by Jacobi or Gauss-Seidel iteration:

          DIMENSION PHI(100,100),NEW(100,100)
          DO 200 J=2,99
             DO 100 I=2,99
                NEW(I,J)=0.25*(PHI(I-1,J)+PHI(I+1,J)
         1                    +PHI(I,J-1)+PHI(I,J+1))
      100    CONTINUE
      200 CONTINUE

This fragment is the Laplace stencil only; the full update adds source and
absorption. Note that NEW is implicitly INTEGER by the naming rule; a real
program would declare it or rename it.

Experiments:
- Jacobi against Gauss-Seidel against SOR;
- grid sizes;
- iteration count against precision;
- traversal order, since storage is column-major.

### 2.3 Monte Carlo particle transport

A non-multiplying, educational slab-transmission model. The free path is
l = -ln(U) / Sigma_t. Its interest:
- the random-number generator;
- floating-point accuracy;
- branching;
- statistical convergence.

It is also a natural batch job: run thousands of histories, change a
parameter, resubmit.

### 2.4 Equation-of-state tables

P = P(rho, T), read from an input table and bilinearly interpolated. It is the
easiest workload, and it exercises:
- sequential I/O;
- table storage;
- the floating-point representation;
- interpolation accuracy.

### 2.5 N-body

a_i = G sum_{j != i} m_j (r_j - r_i) / |r_j - r_i|^3, advanced by a simple
integrator in fixed arrays. It measures the cost of divide and square root,
and the accumulated error.

### 2.6 Dense linear algebra

Gaussian elimination with partial pivoting, about (2/3) N^3 floating-point
operations. A well-defined workload for comparing machines.

## 3. Structure: a small benchmark suite

Each workload has:
- a FORTRAN source;
- an input dataset (on cards, as a deck);
- expected results;
- a check script that verifies correctness and records time.

Start with two: the shock tube and the 2D diffusion solver. Between them
they cover time stepping, stencils, iterative convergence and array access.

## 4. Three levels of fidelity

| Level | Environment | What we learn |
|---|---|---|
| 1 | Modern gfortran, fixed-form FORTRAN | The algorithms and the period style; the oracles |
| 2 | The 7030 FORTRAN IV dialect as C22-6751 defines it, no later features | The programming constraints |
| 3 | The 7030 compiler (found, or RECONSTRUCTION) under MCP on this model | Machine behavior, instruction costs, the batch workflow |

Level 3's "which emulators and compilers exist" is already answered for this
project: the emulator is this model, and the compiler is the open item in §1.

## 5. The ambitious form: a 1962 job, end to end

1. Define the physical problem and its discretization.
2. Punch the FORTRAN source and the numerical input.
3. Compile and submit the job (MCP, a batch deck).
4. Run the time steps.
5. Write snapshots of the solution.
6. Check conservation of mass and energy.
7. Plot the results separately, off the machine, as was done then.
8. Change the mesh resolution and rerun.

Performance can then be counted. Count the arithmetic operations and memory
references, and price them with the published 7030 timings: a model of
historical performance, not a measurement. Once G1 is done, the model's own
cycle count is the second, independent number.

Later, research only (§1): the same workloads on a 704-style machine, on
Stretch and on a vector machine (STAR-100, Cray-1). That comparison shows why
scientific computing moved from look-ahead to vector processing.
