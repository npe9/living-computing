# Third-party Stretch software: documentation located (2026-09-03)

Beyond IBM's own 7030 software (all on bitsavers, held in `../`), the
archival research named third-party languages and systems built for
Stretch installations. Unlike the IBM material, these survive mainly as
conference papers and historical articles -- **no source code for any of
them is known to survive**, and most primary papers are paywalled or
behind bot protection. This file records what documentation exists, its
access status, and what was retrieved, so the trail is durable.

## LASL's IVY (and COLASL) -- Los Alamos algebraic languages
- Grouped in the literature as "COLASL and IVY" (Wikipedia, IBM 7030
  Stretch, refs 20-21). COLASL and IVY were algebraic coding systems at
  Los Alamos Scientific Laboratory, where the first Stretch ran (1961).
- **Primary/most-detailed documentation**:
  - Roger B. Lazarus et al., *Computing at LASL in the 1940s and 1950s*,
    LA-6943-H, Los Alamos / US DOE, May 1978 (surveys LASL's languages
    including IVY). Accessible at `https://sgp.fas.org/othergov/doe/lanl/
    docs1/LA-6943-H.pdf` (FAS) and OSTI, but both serve a bot-challenge
    to `curl` (HTTP 202/403); fetch via a browser. NOT retrieved here.
  - *The COLASL automatic coding system*, Proc. 1962 ACM National
    Conference, pp.44-45, doi:10.1145/800198.806099 (ACM DL, paywalled).
- **Source code**: none known to survive.

## AWRE's S1 / S2 FORTRAN -- Aldermaston Stretch FORTRAN
- Alick Glennie of AWRE (Atomic Weapons Research Establishment,
  Aldermaston) wrote "probably the first major UK FORTRAN compiler" for
  the IBM 7030 Stretch -- the S1 and S2 compilers (S2 the more complete,
  cited as the first to add dynamic arrays; the later Atlas-2 S3 was
  "essentially language compatible with the S2 Stretch compiler").
- **Documentation**: Ron Bell (AWE), "Some Early UK FORTRAN Compilers",
  BCS Fortran Specialist Group, "Fifty Years of Fortran" jubilee, 2007:
  `https://fortran.bcs.org/2007/jubilee/earlyukcompilers.php` and the
  contributions page `.../contributions.php?pglb=FI`. Historical
  recollections, not a manual. The Wikipedia 7030 article cites this
  (ref 4) for the S2/dynamic-arrays claim.
- **Source code / manuals**: none known to survive.

## MITRE's Stretch LISP 1.5 and MATHLAB
- MITRE (spun out of MIT Lincoln Labs, 1958) took delivery of a 7030 in
  Dec 1962. Carl Engelman (1929-1983) created MATHLAB there starting
  1964 -- the first on-line symbolic-mathematics system -- written in
  LISP (a LISP 1.5 on the MITRE machine).
- **Documentation**:
  - Carl Engelman, *MATHLAB: A Program for On-Line Machine Assistance in
    Symbolic Computations*, Proc. Fall Joint Computer Conference, Nov
    30-Dec 1 1965, part II, pp.117-126, doi:10.1145/1463891.1463938 (ACM
    DL, paywalled -- the primary source; would confirm the Stretch
    platform of the original MATHLAB).
  - Secondary survey (retrieved, this folder): *Symbolic Mathematical
    Computation 1965-1975: The emergence of a discipline* (arXiv
    2501.16457, 2025) -- documents MATHLAB's MITRE origin and Engelman;
    does NOT itself state the Stretch platform.
  - Wikipedia: *MATHLAB*, *Carl Engelman*.
- **Note**: widely-available secondary sources place MATHLAB at MITRE in
  the mid-1960s but do not explicitly name Stretch as its host; the
  Stretch/LISP-1.5 attribution comes from the project's own archival
  research and would be confirmed by the paywalled 1965 primary paper.
- **Source code**: none known to survive.

## Retrieved into this folder
- `Kaltofen_SymbolicMathComputation_1965-1975_arxiv2501.16457.pdf` --
  the symbolic-math retrospective (MATHLAB history), freely downloadable.
- `AWRE_UKfortran_earlyukcompilers.txt` -- Brian Chapman's "Some Early
  UK FORTRAN Compilers" (text extraction of the BCS Fortran-jubilee
  page), describing Alick Glennie's S2 Stretch FORTRAN and the S3
  follow-on.
- `AWRE_UKfortran_contributions_php_pglb_FI.txt` -- the jubilee
  contributions index (bibliography and further reading).

## Opened in the browser for manual saving (script-blocked)
These serve a bot challenge or paywall to `curl`; opened via `open` in
the default browser so they can be saved into this folder by hand:
- **LA-6943-H** (Lazarus, *Computing at LASL*, IVY/COLASL):
  `https://sgp.fas.org/othergov/doe/lanl/docs1/LA-6943-H.pdf`
- **MATHLAB** primary (Engelman 1965 FJCC):
  `https://dl.acm.org/doi/10.1145/1463891.1463938`
- **COLASL** (1962 ACM National Conference):
  `https://dl.acm.org/doi/10.1145/800198.806099`

Everything not retrieved above is a citation/URL: the primary documents
are paywalled (ACM) or bot-protected (FAS/OSTI), and no source code for
any of these systems is known to survive.
