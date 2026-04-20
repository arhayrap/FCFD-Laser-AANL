from pyximc import *

probe_flags = EnumerateFlags.ENUMERATE_PROBE
enum_hints = b"addr=xi-com://"

devenum = enumerate_devices(probe_flags, enum_hints)
dev_count = get_device_count(devenum)

for i in range(dev_count):
    dev_name = get_device_name(devenum, i)
    print(dev_name)