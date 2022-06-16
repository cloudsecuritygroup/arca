.. arq documentation master file, created by
   sphinx-quickstart on Sat Apr  9 23:41:06 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Arca: a collection of encrypted search algorithms
=================================================

**Arca** is an Python
package designed to allow researchers to easily and rapidly prototype systems that use encrypted
search algorithms. Originally written by Zachary Espiritu for internal use in the Cloud Security Group at Brown University, Arca provides simple cryptographic primitives (which themselves are based on those
provided by the Python cryptography package) and implementations of various structured
encryption schemes.

Arca's provided encrypted search algorithms allow researchers to easily swap out different encryption subroutines and serialization algorithms for more fine-tuned experimentation; conversely, they come with reasonable pre-defined defaults if you just want to start immediately working with the structures.

Arca has complete type annotations and passes all strict static type checks provided by the `MyPy <http://mypy-lang.org/>`_ type checker.

.. note::

   **Arca** is provided as-is for easy-to-use, rapid prototyping and
   research. Several portions of this library implement cryptographic
   primitives that have not been reviewed by a third-party and are not
   recommended for use in a production environment.


Implementations
---------------

Several different classes of encrypted search algorithms have been implemented in the Arca library:

- **Encrypted multimaps.** Arca provides several implementations of encrypted multimap schemes in the ``arca.ste.emm`` module:

   - :class:`~arca.ste.emm.PiBaseEMM`, based on :math:`\Pi_\mathrm{bas}` from [`CJJJKRS14 <https://eprint.iacr.org/2014/853.pdf>`_]
   - :class:`~arca.ste.emm.Pi2LevEMM`, based on :math:`\Pi_\mathrm{2lev}` from [`CJJJKRS14 <https://eprint.iacr.org/2014/853.pdf>`_]

- **Encrypted dictionaries.** Arca provides a simple encrypted dictionary scheme in the in the ``arca.ste.edx`` module:

   - :class:`~arca.ste.edx.SimpleEDX`

- **Encrypted aggregate range query indexes.** Arca provides several encrypted indexes for aggregate range queries via an implementation of the **ARQ** framework from [`EMT22 <#>`_]. Using **ARQ**, structures from the plaintext data management community may be easily unified with existing *structured encryption* primitives to produce schemes with provable leakage profiles and security guarantees. The following schemes are provided in the ``arca.arq`` module:

   - **ARQ-LinearMin** [[EMT22][EMT22]]

   - **ARQ-1/2-ApproxMode** [[EMT22][EMT22]]

   - **ARQ-alpha-ApproxMedian** [[EMT22][EMT22]]

   - **DPPDGP-Sum** [[DPPDGP18][DPPDGP18]]

   - **DPPDGP-Min1** [[DPPDGP18][DPPDGP18]]

   - **DPPDGP-Min2** [[DPPDGP18][DPPDGP18]]

- **Encrypted range structures.** Arca provides several implementations of *record-reporting* encrypted range structures (meaning that the index returns the set of records that fall in the queried range) for variable domain dimensions. The following schemes are provided in the ``arca.erq`` module:

   - **ERMD-Linear** [FMET22]
   - **ERMD-Quadratic** [FMET22]
   - **ERMD-LogTree** [FMET22]
   - **ERMD-QuadTree** [FMET22]
   - **DPPDGP-Linear** [DPPDGP16]




**ARQ** is an easy-to-use Python library for creating cryptographic schemes
that handle aggregate range queries (sum, minimum, median, and mode) over
encrypted datasets.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules

Testing
-------

The vast majority of tests in Arca rely on `Hypothesis <https://hypothesis.works/>`_ for property-based testing. Our Hypothesis-based tests define a particular property that we expect our code to have. Then, Hypothesis generates arbitrary data matching a particular specification and checks to see if the generated data breaks our defined property.

We find that Hypothesis works really well for our library since Arca implements many algorithms that follow a "round-trip" process: they consume an initial input, transform it in some way (i.e. encrypt it), and then undo that transformation (i.e. decrypt it).

Citing
------

If you use this library (and/or its associated documentation) in your research work,
please cite the following paper:

.. code-block:: bibtex

   @misc{Espiritu2022,
       author = {Zachary Espiritu and
                 Evangelia Anna Markatou and
                 Roberto Tamassia},
       title  = {Time- and Space-Efficient Aggregate Range Queries on Encrypted Databases},
       year   = {2022},
   }

If you want a citation specifically to our software, you can use the following citations (but we
request that you still cite the above paper):

.. code-block:: bibtex

   @software{Arca,
      author  = {Zachary Espiritu},
      license = {Apache-2.0},
      title   = {Arca},
      url     = {https://github.com/cloudsecuritygroup/arca},
   }

License
-------

The Arca code base (e.g. on `Github <#>`_) is licensed under the `Apache License 2.0 <#>`_.
The Arca documentation (this site) is licensed under `CC-SA 4.0 <https://creativecommons.org/licenses/by-sa/4.0/legalcode>`_. Unless otherwise stated, any source code examples embedded within the Arca documentation are licensed under `CC0 1.0 <https://creativecommons.org/publicdomain/zero/1.0/>`_.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
