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


from abc import ABC, abstractmethod
from typing import TypeVar, List, Generic, Union
from dataclasses import dataclass
from fractions import Fraction
from decimal import Decimal


@dataclass(frozen=True)
class ResolveDone:
    __slots__ = ["aggregate"]
    aggregate: Union[int, float, Fraction, Decimal]


ResolveDSQueryType = TypeVar("ResolveDSQueryType")


@dataclass(frozen=True)
class ResolveContinue(Generic[ResolveDSQueryType]):
    __slots__ = ["subqueries"]
    subqueries: List[ResolveDSQueryType]


DSQueryType = TypeVar("DSQueryType")
DSResponseType = TypeVar("DSResponseType")


class RangeAggregateQuerier(ABC, Generic[DSQueryType, DSResponseType]):
    @abstractmethod
    def query(self) -> List[DSQueryType]:
        r"""
        Corresponds to the :math:`\mathbb{Q}` algorithm.
        """
        ...

    @abstractmethod
    def resolve(
        self, responses: List[DSResponseType]
    ) -> Union[ResolveDone, ResolveContinue[DSQueryType]]:
        r"""
        Corresponds to the :math:`\mathbb{R}` algorithm.
        """
        ...
