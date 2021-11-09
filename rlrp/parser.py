from typing import Any, Dict
import bitstring

INT32 = 'int:32'
UINT32 = 'uintle:32'
UINT64 = 'uintle:64'
FLOAT32 = 'floatle:32'

def print(str):
    pass

def parsestr(bits):
    length = bits.read(UINT32)
    # if length > 100:
    #     bits.read(UINT64)
    bytes = bits.read(f"bytes:{length}")
    # print(f"weird value: {bytes[0:100]}")
    # try:
    print(f"L: {length}")
    decode = bytes.decode('cp1252')
    return decode.replace("\x00", "", -1)
    # except Exception as e:
    #     print(e)
    #     print(f"failed to decode {length}, {bytes[0:20]}")

def parseprop(bits):
    prop = dict()
    prop['name'] = parsestr(bits)
    print(f"name: {prop['name']}")
    if prop["name"] == "None":
        return prop
    prop["type"] = parsestr(bits)
    print(f"type {prop['type']}")
    if prop["type"] == "ArrayProperty":
        return parsearray(prop["name"], bits)
    prop["length"] = bits.read(UINT32)
    prop["blob"] = bits.read(UINT32)

    if prop["type"] == "IntProperty":
        prop["value"] = bits.read(UINT32)
    if prop["type"] in ("StrProperty", "NameProperty"):
        prop["value"] = parsestr(bits)
    if prop["type"] == "FloatProperty":
        prop["value"] = bits.read(FLOAT32)
    if prop["type"] == "BoolProperty":
        prop["value"] = bits.read(8)
    if prop["type"] == "ByteProperty":
        prop["value"] = parsebytes(bits)
    if prop["type"] == "QWordProperty":
        prop["value"] = bits.read(UINT64)

    print(f"value {prop['value']}")
    return prop

def parsebytes(bits):
    type = parsestr(bits)
    value = parsestr(bits)
    return {"type": type, "value": value}

def parsearray(name, bits):
    length = bits.read(UINT32)
    print(f"l: {length}")
    blob = bits.read(UINT32)
    print(f"blob {blob}")
    items = bits.read(UINT32)
    print(f"items {items}")
    props = []
    for i in range(items):
        print(f"i {i}")
        prop = parsedict(bits)
        props.append(prop)

    return {"name": name, "value": props}

def parsedict(bits):
    props = dict()
    while True:
        prop = parseprop(bits)
        print(f"adding prop: {prop}")
        if prop["name"] == "None":
            break
        props[prop["name"]] = prop["value"]
    return props


def parselevel(bits):
    return {"name": parsestr(bits)}

def parsekeyframe(bits):
    return {
        "time": bits.read(FLOAT32),
        "frame": bits.read(UINT32),
        "file_position": bits.read(UINT32)
            }

def parsedebugstr(bits):
    return {
        "number": bits.read(UINT32),
        "username": parsestr(bits),
        "text": parsestr(bits)
            }

def parse(filename):
    f = open(filename, "rb")
    bits = bitstring.BitStream(f)

    header = {}
    header["length"]= bits.read(INT32)
    header["crc"] = bits.read(UINT32)
    header["engine_version"] = bits.read(UINT32)
    header["license"] = bits.read(UINT32)
    header["net_license"] = bits.read(UINT32)
    header["TAGame"] = parsestr(bits)
    header["props"] = parsedict(bits)

    replay = {}
    replay["length"] = bits.read(UINT32)
    replay["crc"] = bits.read(UINT32)
    replay["level_length"] = bits.read(UINT32)
    replay["levels"] = []
    for i in range(replay["level_length"]):
        replay["levels"].append(parselevel(bits))

    replay["keyframe_length"] = bits.read(UINT32)
    replay["keyframes"] = []
    for i in range(replay["keyframe_length"]):
        replay["keyframes"].append(parsekeyframe(bits))

    replay["network_stream_length"] = bits.read(UINT32)
    network_stream = bits.read(f"bytes:{replay['network_stream_length']}")

    replay["debug_string_length"] = bits.read(UINT32)
    replay["debug_strings"] = [
            parsedebugstr(bits) for x in range(replay["debug_string_length"])
            ]

    return replay

