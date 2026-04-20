import pyvisa

rm = pyvisa.ResourceManager()
scope = rm.open_resource("TCPIP::192.168.0.170::INSTR")
scope.timeout = 10000

print("IDN:", scope.query("*IDN?"))

try:
    scope.write('FILE:DELETE "D:\\Waveforms\\Document.txt"')
    print("Delete command sent.")

    file_list = scope.query('FILE:LIST "D:\\Waveforms"')
    print("Files after deletion attempt:")
    print(file_list)

except Exception as e:
    print("Error executing file commands:", e)

scope.close()
