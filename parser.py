import bitstring

INT32 = 'int:32'
UINT32 = 'uintle:32'

def parsestr(bits):
    length = bits.read(UINT32)
    print(f"l: {length}")
    return bits.read(f"bytes:{length}").decode("ascii").replace("\x00", "", -1)

def parseprop(bits):
    prop = {}
    prop["name"] = parsestr(bits)
    if prop["name"] == "None":
        return prop
    prop["type"] = parsestr(bits)
    if prop["type"] == "ArrayProperty":
        return prop
    prop["length"] = bits.read(UINT32)
    prop["blob"] = bits.read(UINT32)

    if prop["type"] == "IntProperty":
        prop["value"] = bits.read(UINT32)
    return prop

def parse(filename):
    f = open(filename, "rb")
    bits = bitstring.BitStream(f)

    data = {}
    data["length"]= bits.read(INT32)
    data["crc"] = bits.read(UINT32)
    data["engine_version"] = bits.read(UINT32)
    data["license"] = bits.read(UINT32)
    data["net_license"] = bits.read(UINT32)
    data["TAGame"] = parsestr(bits)
    data["props"] = []

    data["props"].append(parseprop(bits))
    data["props"].append(parseprop(bits))
    data["props"].append(parseprop(bits))
    data["props"].append(parseprop(bits))

    return data

