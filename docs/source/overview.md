# Overview

This project explores privacy-preserving analytics for retail using Homomorphic Encryption (HE).
It accompanies the written thesis and provides reproducible build and experiment notes.

- **Goal:** Evaluate feasibility and trade-offs (accuracy, runtime, memory, cost) of encrypted analytics for realistic retail tasks.
- **Scope:** CKKS-based schemes; secure aggregation; encrypted inference for basic models; multiparty key flows.

## Graphviz example

```{graphviz}
:align: center
:caption: High-level thesis flow

digraph {
  rankdir=LR;
  node [shape=box];
  "Intro" -> "Lit Review" -> "Methodology" -> "Implementation" -> "Results" -> "Discussion" -> "Conclusion";
}
```

## Mermaid example

```{mermaid}
flowchart LR
  A[Intro] --> B[Lit Review] --> C[Methodology] --> D[Implementation] --> E[Results] --> F[Discussion] --> G[Conclusion]
```

## Repository layout (suggested)

```
docs/
  source/
    index.rst
    overview.md
    setup.md
    datasets.md
    experiments.md
    methodology.md
    implementation.md
    results.md
    discussion.md
    conclusion.md
    appendix.md
```

Build with:

```bash
python -m sphinx -b html docs/source docs/build/html
# live-reload during writing
sphinx-autobuild docs/source docs/build/html
```
