from typing import Any, Dict, List, Optional

from bitstring import BitStream

from .constants import (
    FLOAT32,
    QWORD_TYPE,
    UINT32,
    UINT64,
    NONE,
    ARRAY_TYPE,
    FLOAT_TYPE,
    STR_TYPE,
    NAME_TYPE,
    INT_TYPE,
    ENUM_TYPE,
    BOOL_TYPE,
)


def read_string(stream: BitStream) -> str:
    length = read_int(stream)
    raw_value: Optional[bytes] = stream.read(f"bytes:{length}")
    if not raw_value:
        return "no bytes"
    try:
        return raw_value.decode("cp1252").replace("\x00", "", -1)
    except:
        return f"failed to decode bytes:\n{raw_value[0:100]}"


def read_int(stream: BitStream) -> Optional[int]:
    return stream.read(UINT32)


def read_float(stream: BitStream) -> Optional[float]:
    return stream.read(FLOAT32)


def read_bool(stream: BitStream) -> bool:
    return bool(stream.read(8))


def read_enum(stream: BitStream) -> Dict[str, str]:
    """Yes, bytes are actually dictionaries in the RL replay format"""
    return {"type": read_string(stream), "value": read_string(stream)}


def read_qword(stream: BitStream) -> Optional[int]:
    return stream.read(UINT64)


class Property:
    name: str
    type: str
    legth: int
    value: Any

    def __init__(self, stream: BitStream):
        self.name = read_string(stream)
        if self.name == NONE:
            return

        self.type = read_string(stream)
        if self.type == ARRAY_TYPE:
            self.value = PropertyArray(stream).value
            return

        self.length = read_int(stream)
        read_int(stream) # unused unknown value
        if self.type == INT_TYPE:
            self.value = read_int(stream)
        elif self.type in (STR_TYPE, NAME_TYPE):
            self.value = read_string(stream)
        elif self.type == FLOAT_TYPE:
            self.value = read_float(stream)
        elif self.type == BOOL_TYPE:
            self.value = read_bool(stream)
        elif self.type == ENUM_TYPE:
            self.value = read_enum(stream)
        elif self.type == QWORD_TYPE:
            self.value = read_qword(stream)
        else:
            raise Exception(f"Can't read property type '{self.type}' in property {self.name}")


class PropertyDictionary(dict):
    def __init__(self, stream: BitStream):
        while True:
            property = Property(stream)
            if property.name == NONE:
                break
            self[property.name] = property.value


class PropertyArray:
    count: Optional[int]
    value: List[PropertyDictionary]

    def __init__(self, stream: BitStream):
        read_int(stream) # unused length value
        read_int(stream) # unused unknown value
        self.count = read_int(stream) or 0
        self.value = [PropertyDictionary(stream) for _ in range(self.count)]

