# Resources

## Web applications

### Twisted Multilayer Builder

[**Open the Twisted Multilayer Builder →**](https://qiminyan-twisted-builder.hf.space){.btn}

An interactive web application for constructing and analyzing twisted multilayer (three or more layers) two-dimensional
structures. Stacks can use one material throughout (alternating-twist trilayers, helical multilayers, twisted double bilayers)
or mix materials, with layers drawn from tens of thousands of DFT-relaxed monolayers in public 2D materials databases or
imported from structure files.

- Commensurate supercells with minimal strain for any stacking and twist pattern, with the moiré period and per-layer strain
- Interactive 3D, top (moiré pattern), and side views, with figure export (PNG, SVG)
- Symmetry analysis of every stack (point and space group, chirality, polarity) and the symmetry-allowed second-harmonic
  generation (χ⁽²⁾) and circular-dichroism (gyration) tensor components
- Structure export: POSCAR, CIF, XSF, extended XYZ, and metadata

*Hosted on Hugging Face Spaces. If the app has been idle, the first visit can take up to a minute to start.*

**Where the 2D materials come from.** The builder's catalog of 29,855 monolayers is a snapshot of four public databases
(monolayers with at most 60 atoms per cell that form a single slab). Every exported structure records its source,
license, and citation.

| Database | Monolayers | License | Reference |
|---|---|---|---|
| [JARVIS-DFT 2D](https://jarvis.nist.gov/) (NIST) | 1,102 | CC BY 4.0 | K. Choudhary et al., *npj Comput. Mater.* **6**, 173 (2020) |
| [2DMatPedia](http://www.2dmatpedia.org/) | 6,345 | open, citation requested | J. Zhou et al., *Sci. Data* **6**, 86 (2019) |
| [Materials Cloud MC2D](https://www.materialscloud.org/discover/mc2d) (EPFL) | 2,730 | CC BY 4.0 | D. Campi et al., Materials Cloud Archive 2022.84 (2022) |
| [Alexandria 2D](https://alexandria.icams.rub.de/) (PBE; E<sub>hull</sub> ≤ 0.10 eV/atom) | 19,678 | CC BY 4.0 | J. Schmidt et al., *2D Mater.* **10**, 035009 (2023) |

Users can also import their own structures (POSCAR, CIF, XSF, XYZ, Quantum ESPRESSO, ASE JSON), including individual
structures downloaded from C2DB or the Materials Project.

## Datasets

- **Tensorial optical and transport properties of materials from the Wannier function method.** Frequency-dependent optical
  and transport tensors for 7,301 materials from automated Wannierization.
  Data: [doi:10.6084/m9.figshare.28689059](https://doi.org/10.6084/m9.figshare.28689059) ·
  Paper: [Scientific Data 12, 1092 (2025)](https://doi.org/10.1038/s41597-025-05396-9)
- **TSENN models and dataset.** Frequency-dependent dielectric tensors and pretrained equivariant models.
  Data: [doi:10.6084/m9.figshare.31180054](https://doi.org/10.6084/m9.figshare.31180054) ·
  Paper: [Nature Communications (2026)](https://doi.org/10.1038/s41467-026-69159-9) ·
  Code: [TSENN](https://github.com/qmatyanlab/TSENN)
- **Band structure dataset for Bandformer.** Electronic band structures of about 27,000 materials from the Materials Project,
  prepared for end-to-end band-structure learning.
  Data: [doi:10.6084/m9.figshare.30502967](https://doi.org/10.6084/m9.figshare.30502967) ·
  Paper: [arXiv:2411.16483](https://arxiv.org/abs/2411.16483) ·
  Code: [Bandformer](https://github.com/qmatyanlab/Bandformer)

## Software

Open-source codes for our machine learning models and workflows are listed on the [Code](code.html) page and on
[GitHub](https://github.com/qmatyanlab).
