from mcl import MCL
import time


def datareadings(lockinset, datareadings):
    print("Receiving data on set L%i: " % (lockinset + 1), datareadings)


def scopereadings(waveformtype, data):
    print("Receiving %s: " % waveformtype, data)


print("Creating MCL object")
mcl = MCL()
print("Finding systems")
systems = mcl.find_systems()
print(systems)
if (len(systems) > 0):
    mcl_ip = str(next(iter(systems)))
else:
    # mcl_ip = '172.22.11.2'
    mcl_ip = '192.168.0.11'
mcl_ip = input("Enter MCL IP [%s]: " % mcl_ip) or mcl_ip

mcl.lidata_data_readings_l1.register_callback(datareadings)
mcl.lidata_data_readings_l2.register_callback(datareadings)
mcl.scope.register_callback(scopereadings)
mcl.fft.register_callback(scopereadings)

print("Connect to instrument")
mcl.connect(mcl_ip)

print("Getting internal voltages")
print(mcl.config_general_pic_ctrl.val)

print("Printing installed modules etc.")
print(mcl.config_general_local_ctrl.val)

print("Running for 10s")
time.sleep(10)

print("Disconnecting...")
mcl.disconnect()
