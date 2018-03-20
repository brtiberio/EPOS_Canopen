import canopen

network = canopen.Network()
network.connect(channel='can0', bustype='socketcan')
# network.connect(bustype='kvaser', channel=0, bitrate=250000)
# network.connect(bustype='pcan', channel='PCAN_USBBUS1', bitrate=250000)
# network.connect(bustype='ixxat', channel=0, bitrate=250000)
# network.connect(bustype='nican', channel='CAN0', bitrate=250000)

node = network.add_node(1)

# # This will attempt to read an SDO from nodes 1 - 127
# network.scanner.search()
# # We may need to wait a short while here to allow all nodes to respond
# time.sleep(0.05)
# for node_id in network.scanner.nodes:
#     print("Found node %d!" % node_id)

# try to read status word or use sdo upload
device_type_data = node.sdo.upload(0x1000, 0)
print("The device type is 0x%X" % device_type_data)
statusword = node.sdo.upload(0x6041, 0)
print("The device type is \n Hex={0:#4X} Bin={0:#16b}".format(statusword))

network.disconnect()
