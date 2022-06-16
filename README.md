# Arca: a collection of encrypted search algorithms

**Arca** is an Python package designed to allow researchers to easily and
rapidly prototype systems that use encrypted search algorithms.
Arca provides simple cryptographic primitives
(which themselves are based on those provided by the Python `cryptography`
package) and implementations of various structured encryption schemes.

Arca's provided encrypted search algorithms allow researchers to easily swap
out different encryption subroutines and serialization algorithms for more
fine-tuned experimentation; conversely, they come with reasonable pre-defined
defaults if you just want to start immediately working with the structures.

Arca has complete type annotations and passes all strict static type checks
provided by the [MyPy](http://mypy-lang.org/) type checker.

**Note:** Arca is provided as-is for easy-to-use, rapid prototyping and
research. Several portions of this library implement cryptographic
primitives that have not been reviewed by a third-party and are not
recommended for use in a production environment.

## Implementations

Several different classes of encrypted search algorithms have been implemented in the Arca library:

- **Encrypted multimaps.** Arca provides several response-revealing and response-hiding implementations of basic encrypted multimap schemes [[CJJJKRS14][CJJJKRS14]] in the `arca.ste.emm` module.

- **Encrypted dictionaries.** Arca provides a simple encrypted dictionary scheme in the `arca.ste.edx` module.

- **Encrypted aggregate range query indexes.** Arca provides several schemes for computing encrypted aggregate range query indexes via an implementation of the **ARQ** framework from [[EMT22][EMT22]]. Using **ARQ**, structures from the plaintext data management community may be easily unified with existing *structured encryption* primitives to produce schemes with provable leakage profiles and security guarantees. The **ARQ** framework may also be used to derive equivalent schemes to those presented in [[DPPDGP18][DPPDGP18]].

More details about the above schemes are provided in the documentation (to be released).

## Citing

If you use this library (and/or its associated documentation) in your research work,
please cite the following paper:

```bibtex
@article{EMT22,
  author  = {Zachary Espiritu and
             Evangelia Anna Markatou and
             Roberto Tamassia},
  title   = {Time- and Space-Efficient Aggregate Range Queries over Encrypted Databases},
  journal = {Proceedings on Privacy Enhancing Technologies},
  number  = {2022.4},
  volume  = {2022},
  year    = {2022},
  note    = {To appear},
}
```

If you want a citation specifically to our software, you can use the following citations (but we
request that you still cite the above paper):

```bibtex
@software{Arca,
  author  = {Zachary Espiritu},
  license = {Apache-2.0},
  title   = {Arca},
  url     = {https://github.com/cloudsecuritygroup/arca},
}
```

## License

All code in this repository is provided as-is under the *Apache License 2.0*. See
[`LICENSE`](/LICENSE) for full
license text.

[EMT22]: https://cs.brown.edu/research/pubs/theses/ugrad/2022/espiritu.zachary.pdf

[DPPDGP18]: https://dl.acm.org/doi/10.1145/3167971

[CJJJKRS14]: https://dx.doi.org/10.14722/ndss.2014.23264
