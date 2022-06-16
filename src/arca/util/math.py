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


def log2_floor(x: int) -> int:
    r"""
    Returns the equivalent of :math:`\lfloor \log_2 (x) \rfloor`. This is a
    slight optimization over :code:`math.floor(math.log2(x))`.

    :param x: the number to compute the log2 floor of
    :return: :math:`\lfloor \log_2 (x) \rfloor`
    """
    return x.bit_length() - 1


def log2_ceil(x: int) -> int:
    r"""
    Returns the equivalent of :math:`\lceil \log_2 (x) \rceil`. This is a
    slight optimization over :code:`math.ceil(math.log2(x))`.

    :param x: the number to compute the log2 ceiling of
    :return: :math:`\lceil \log_2 (x) \rceil`
    """
    return (x - 1).bit_length()


def next_power_of_2(x: int) -> int:
    if x <= 0:
        raise ValueError("x must be positive")
    result: int = 2 ** log2_ceil(x)
    return result
