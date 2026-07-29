# Sprint 31: Scientific Network Resolution Validation

Validation date: 2026-07-17
Target: BIDS ecosystem
Method: network-neighborhood clustering instead of artifact similarity

---

## Input

- Total artifacts: 80
- Programs resolved: 12
- Network nodes: 808
- Network edges: 1011

## Inferred Programs

### bids-examples

- Program ID: `bids-standard/bids-examples`
- Description: The Brain Imaging Data Structure (BIDS) Specification
- Contributors: 697
- Workstreams: 9
- Software releases: 3
- Papers: 19
- Datasets: 20

**Comprehension Summary:**

bids-examples is a distributed scientific program spanning 3 repositories. It includes 3 software releases, 19 papers, and 20 datasets. Primary workstreams: ica, bids, eeg, graph, neuroimaging. Active since 1985.

### bids-specification

- Program ID: `bids-standard/bids-specification`
- Description: Realized Variance and Market Microstructure Noise
- Contributors: 2
- Workstreams: 0
- Software releases: 0
- Papers: 1
- Datasets: 0

**Comprehension Summary:**

bids-specification is a distributed scientific program spanning 1 repositories. It includes 0 software releases, 1 papers, and 0 datasets. Primary workstreams: . Active since 2006.

### pybids

- Program ID: `bids-standard/pybids`
- Description: The OpenNeuro resource for sharing of neuroscience data
- Contributors: 12
- Workstreams: 0
- Software releases: 0
- Papers: 1
- Datasets: 0

**Comprehension Summary:**

pybids is a distributed scientific program spanning 1 repositories. It includes 0 software releases, 1 papers, and 0 datasets. Primary workstreams: . Active since 2021.

### program-3

- Program ID: `program-3`
- Description: UFuncs and DTypes: new possibilities in NumPy
- Contributors: 2
- Workstreams: 0
- Software releases: 0
- Papers: 0
- Datasets: 1

**Comprehension Summary:**

program-3 is a distributed scientific program spanning 0 repositories. It includes 0 software releases, 0 papers, and 1 datasets. Primary workstreams: . Active since 2022.

### program-4

- Program ID: `program-4`
- Description: Data and analysis code for "Garbage In, Garbage Out?" paper in Proc ACM FAT* 2020
- Contributors: 1
- Workstreams: 0
- Software releases: 0
- Papers: 0
- Datasets: 1

**Comprehension Summary:**

program-4 is a distributed scientific program spanning 0 repositories. It includes 0 software releases, 0 papers, and 1 datasets. Primary workstreams: . Active since 2019.

### program-5

- Program ID: `program-5`
- Description: Code and data for "The Rise and Fall of the Note" (PACMHCI, CSCW 2019)
- Contributors: 1
- Workstreams: 0
- Software releases: 0
- Papers: 0
- Datasets: 1

**Comprehension Summary:**

program-5 is a distributed scientific program spanning 0 repositories. It includes 0 software releases, 0 papers, and 1 datasets. Primary workstreams: . Active since 2019.

### bids-examples

- Program ID: `bids-standard/bids-examples`
- Description: Bid, a Bcl2 Interacting Protein, Mediates Cytochrome c Release from Mitochondria in Response to Activation of Cell Surface Death Receptors
- Contributors: 5
- Workstreams: 0
- Software releases: 0
- Papers: 1
- Datasets: 0

**Comprehension Summary:**

bids-examples is a distributed scientific program spanning 1 repositories. It includes 0 software releases, 1 papers, and 0 datasets. Primary workstreams: . Active since 1998.

### bids-examples

- Program ID: `bids-standard/bids-examples`
- Description: Bid/no-bid decision-making – a fuzzy linguistic approach
- Contributors: 2
- Workstreams: 0
- Software releases: 0
- Papers: 1
- Datasets: 0

**Comprehension Summary:**

bids-examples is a distributed scientific program spanning 1 repositories. It includes 0 software releases, 1 papers, and 0 datasets. Primary workstreams: . Active since 2004.

### bids-examples

- Program ID: `bids-standard/bids-examples`
- Description: Combinatorial Auctions: A Survey
- Contributors: 2
- Workstreams: 0
- Software releases: 0
- Papers: 1
- Datasets: 0

**Comprehension Summary:**

bids-examples is a distributed scientific program spanning 1 repositories. It includes 0 software releases, 1 papers, and 0 datasets. Primary workstreams: . Active since 2003.

### bids-examples

- Program ID: `bids-standard/bids-examples`
- Description: Auctions and Bidding: A Primer
- Contributors: 1
- Workstreams: 1
- Software releases: 0
- Papers: 2
- Datasets: 0

**Comprehension Summary:**

bids-examples is a distributed scientific program spanning 1 repositories. It includes 0 software releases, 2 papers, and 0 datasets. Primary workstreams: forward. Active since 1989.

### bids-examples

- Program ID: `bids-standard/bids-examples`
- Description: Demand Reduction and Inefficiency in Multi-Unit Auctions
- Contributors: 5
- Workstreams: 0
- Software releases: 0
- Papers: 1
- Datasets: 0

**Comprehension Summary:**

bids-examples is a distributed scientific program spanning 1 repositories. It includes 0 software releases, 1 papers, and 0 datasets. Primary workstreams: . Active since 2014.

### bids-examples

- Program ID: `bids-standard/bids-examples`
- Description: Regret and Feedback Information in First-Price Sealed-Bid Auctions
- Contributors: 2
- Workstreams: 0
- Software releases: 0
- Papers: 1
- Datasets: 0

**Comprehension Summary:**

bids-examples is a distributed scientific program spanning 1 repositories. It includes 0 software releases, 1 papers, and 0 datasets. Primary workstreams: . Active since 2008.

## Evaluation

- Did the resolver group BIDS repos together? - pending manual review
- Did network neighborhoods produce coherent programs? - pending manual review
- Is this better than artifact-similarity grouping? - to be compared with Sprint 30

## Precision / Recall / Compression / Priority Coverage

- Precision: not measured (manual verificaiton pending)
- Recall: not measured (manual verificaiton pending)
- Compression: to be measured
- Priority coverage: pending DOI traceability to priority ledger

## Next Steps

1. Manual expert review of inferred BIDS program.
2. Compare network-resolution results with artifact-similarity results.
3. If valid, extend to OpenNeuro and AllenSDK.
