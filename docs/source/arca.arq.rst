arca.arq package
================

**ARQ** is a framework for creating cryptographic schemes
that handle aggregate range queries (sum, minimum, median, and mode) over
encrypted datasets. Using **ARQ**, structures from the plaintext data
management community may be easily unified with existing
*structured encryption* primitives to produce schemes with defined, provable
leakage profiles and security guarantees.

Arca includes several constructions that handle various types
of encrypted aggregate range queries. Most of the implemented schemes
have *constant* asympototic query complexity in the worst-case.

The **ARQ** framework and associated schemes are described in more detail
(with formal security definitions and proofs) in the paper "Time- and
Space-Efficient Range Aggregate Queries on Encrypted Databases" by Zachary
Espiritu, Evangelia Anna Markatou, and Roberto Tamassia. Our paper provides
more details on the benefits of the **ARQ** framework in comparison to prior
work, as well as formal leakage definitions and adaptive security proofs.

Example
-------

.. code-block:: python3

   from arca.arq import ARQ, Table, RangeQuery
   from arca.arq.plaintext_schemes.sum import SumPrefix
   from arca.ste.edx import SimpleEDX
   from arca.ste.serializers import IntSerializer

   # Make a Table:
   table = Table.make([(0, 0), (1, 1), (2, 2), (3, 3)])

   # Choose your aggregate scheme:
   aggregate_scheme = SumPrefix()

   # Choose an appropiate structured encryption scheme for the data
   # structure output by your chosen aggregate scheme. SumPrefix
   # outputs a Dict[int, int], so we can use the SimpleEDX scheme to
   # encrypt the dictionary. Since the keys and values of the
   # dictionary are integers, we can also set the serializers used by
   # SimpleEDX to IntSerializer for both the keys and values:
   eds_scheme = SimpleEDX(
      dx_key_serializer=IntSerializer(),
      dx_value_serializer=IntSerializer(),
   )

   # Instantiate the ARQ framework with your chosen aggregate scheme
   # and structured encryption scheme:
   arq_scheme = ARQ(
      aggregate_scheme=aggregate_scheme,
      eds_scheme=eds_scheme,
   )

   # In the setup phase (run on the client), generate a key and encrypt
   # the table with the scheme:
   key = arq_scheme.generate_key()
   eds_serialized = arq_scheme.setup(key, table)

   # Send the serialized encrypted index to the server, then unserialize
   # it on the server-side:
   eds = arq_scheme.load_eds(eds_serialized)

   # In the query phase, the client makes a query (example: [0, 4)) and
   # retrieves the result:
   range_query = RangeQuery(start=0, end=4)
   result = arq_scheme.query(key, table.domain, range_query, eds)
   assert result == 6

Subpackages
-----------

.. toctree::
   :maxdepth: 4

   arca.arq.plaintext_schemes

Submodules
----------

arca.arq.arq module
------------------

.. automodule:: arca.arq.arq
   :members:
   :undoc-members:
   :show-inheritance:

arca.arq.domain module
---------------------

.. automodule:: arca.arq.domain
   :members:
   :undoc-members:
   :show-inheritance:

arca.arq.range\_aggregate\_querier module
----------------------------------------

.. automodule:: arca.arq.range_aggregate_querier
   :members:
   :undoc-members:
   :show-inheritance:

arca.arq.range\_aggregate\_scheme module
---------------------------------------

.. automodule:: arca.arq.range_aggregate_scheme
   :members:
   :undoc-members:
   :show-inheritance:

arca.arq.range\_query module
---------------------------

.. automodule:: arca.arq.range_query
   :members:
   :undoc-members:
   :show-inheritance:

arca.arq.table module
--------------------

.. automodule:: arca.arq.table
   :members:
   :undoc-members:
   :show-inheritance:

Module contents
---------------

.. automodule:: arca.arq
   :members:
   :undoc-members:
   :show-inheritance:
