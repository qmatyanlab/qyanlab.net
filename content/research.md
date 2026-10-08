# Research

## 1. Symmetry-aware AI for solid-state quantum materials
We develop machine learning frameworks that build physical principles (point-group symmetry, equivariance, local bonding
motifs, and exact physical constraints) into the network itself rather than learning them from data, for accurate,
data-efficient and interpretable prediction for quantum materials.
- Equivariant networks for tensorial and spectral properties: TSENN predicts full frequency-dependent dielectric tensors about
  1,000× faster than DFT (Nat. Commun. 2026); equivariant GNNs for tensor properties of crystals (arXiv:2406.03563).
- Point-group equivariant graph neural networks for materials (arXiv:2607.16871).
- Beyond-atom representations: motif-centric learning (AMDNet, Sci. Adv. 2021), crystal hypergraph convolutional networks
  (npj Comput. Mater. 2025), and material–motif heterogeneous graphs (Adv. Intell. Discov. 2026).

## 2. AI-driven inverse design of functional and quantum materials
Moving from property prediction to design: symmetry-respecting, property-steered generative models coupled with
first-principles validation in a closed loop.
- Symmetry- and property-aware crystal generation with reinforcement learning (SPARC, arXiv:2609.13468), which avoids the
  low-symmetry "reward-hacking" structures of surrogate-guided generators.
- Targets include altermagnets, low-damping magnets, nonlinear-optical and Berry-curvature-dipole materials.
- Toward foundation models and agentic workflows that combine equivariant models, generative design, high-throughput
  first-principles computation, and AI agents.

## 3. Machine learning for electronic structure across scales
End-to-end and Hamiltonian-based learning of electronic structure, from simple crystals to large twisted and disordered systems.
- WANDER bridges deep-learning force fields and Wannier Hamiltonians, reaching twisted bilayers with more than 1,000 atoms at
  10³–10⁴× the speed of DFT (npj Comput. Mater. 2025).
- Bandformer, a graph Transformer for end-to-end band-structure prediction (arXiv:2411.16483).
- Open data: tensorial optical and transport properties of 7,301 materials from automated Wannierization (Sci. Data 2025);
  physics-constrained density functionals via contrastive learning (Digital Discovery 2023).

## 4. Multilayer twisted quantum materials
Twisting stacks of three or more two-dimensional layers opens a vast design space of moiré superlattices whose flat bands,
topology, chirality, and nonlinear optical responses are absent in the individual layers. We aim to make this space computable
and designable.
- A universal machine-learning Hamiltonian for twisted multilayers: equivariant models evaluate each layer in its own frame,
  and a twist-equivariant network learns the interlayer coupling. Trained on large-scale first-principles data spanning
  thousands of 2D materials, it targets the electronic structure and optical response of moiré cells far beyond the reach of DFT.
- Symmetry analysis of arbitrary twisted stacks (point and space groups, chirality, polarity) to identify allowed
  second-harmonic generation and circular-dichroism responses, guiding the design of chiral and nonlinear-optical moiré materials. Explore twisted stacks in our
  [Twisted Multilayer Builder](https://qiminyan-twisted-builder.hf.space) (see [Resources](resources.html)).
- Deep-learning-guided twistronics for self-assembled quantum optoelectronics (NSF DMREF), and ideal topological flat bands in
  moiré heterostructures with type-II band alignment (arXiv:2507.06168).

## 5. Data-driven design of quantum defects in 2D materials
Symmetry-guided, high-throughput discovery of point defects for qubits, single-photon emitters, and quantum sensors in
atomically thin materials.
- A local-symmetry design principle identified antisite defect qubits in transition metal dichalcogenides (Nat. Commun. 2022;
  patent) and more than 40 quantum-defect candidates across binary 2D hosts (arXiv:2405.11379).
- Machine learning for defects with persistent-homology features (Chem. Mater. 2025).
- The Defect Genome Initiative (Adv. Mater. 2024) and the Roadmap on 2D Materials for Quantum Technologies (2D Mater., guest editor).

## 6. Disorder, alloys, and complex materials
Machine learning frameworks for configurational, chemical, and spin disorder in multicomponent alloys.
- GNN-accelerated Monte Carlo for order–disorder transitions and configurational entropy (npj Comput. Mater. 2024), and ensemble
  properties of atomically disordered materials (ACS Nano 2025).
- A multi-scale framework for coupled chemical, spin, and structural disorder in alloys (arXiv:2607.07456).
