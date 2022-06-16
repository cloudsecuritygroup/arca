##
## Copyright 2022 Zachary Espiritu
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##    http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
##

from .range_query import RangeQuery
from .range_aggregate_querier import RangeAggregateQuerier
from .table import Table
from .domain import Domain


from abc import ABC, abstractmethod
from typing import TypeVar, Generic


DSType = TypeVar("DSType")
DSQueryType = TypeVar("DSQueryType")
DSResponseType = TypeVar("DSResponseType")


class RangeAggregateScheme(ABC, Generic[DSType, DSQueryType, DSResponseType]):
    r"""
    Interface corresponding to the plaintext aggregate range query scheme
    syntax :math:`(\mathbb{S}, \mathbb{Q}, \mathbb{R})` defined in [EMT22].
    """

    @abstractmethod
    def setup(self, table: Table) -> DSType:
        r"""
        Corresponds to the :math:`\mathbb{S}` algorithm.
        """
        ...

    @abstractmethod
    def generate_querier(
        self, domain: Domain, query: RangeQuery
    ) -> RangeAggregateQuerier[DSQueryType, DSResponseType]:
        r"""
        Corresponds to the :math:`\mathbb{Q}` algorithm.
        """
        ...
