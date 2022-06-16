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

from .serializer import Serializer

from typing import Any
from dataclasses import dataclass

import struct


@dataclass(frozen=True)
class StructSerializer(Serializer[Any]):
    format_string: str

    def save(self, value: Any) -> bytes:
        if isinstance(value, tuple):
            return struct.pack(self.format_string, *value)
        return struct.pack(self.format_string, value)

    def load(self, blob: bytes) -> Any:
        return struct.unpack(self.format_string, blob)
