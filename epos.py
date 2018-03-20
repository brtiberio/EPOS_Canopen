import canopen
import logging
import sys


class Epos:
    channel = 'can0'
    bustype = 'socketcan'
    nodeID  = 1
    network = None
    _connected = False

    # List of motor types
    motorType = {'DC motor': 1, 'Sinusoidal PM BL motor': 10, 'Trapezoidal PM BL motor': 11}

    node = []

    def __init__(self, _network=None):

        # check if network is passed over or create a new one
        if not _network:
            self.network =  canopen.Network()
        else:
            self.network = _network

    def begin(self, nodeID, _channel='can0', _bustype='socketcan', objectDitionary=None):
        '''Initialize Epos device

        Configure and setup Epos device.

        Args:
            nodeID:    Node ID of the device.
            channel:   Port used for communication. Default can0
            bustype:   Port type used. Default socketcan.
            network:   Use an already configured network.
        Return:
            Ok:        A boolean if all went ok.
        '''
        self.network.connect(channel=_channel, bustype=_bustype)
        if (self.network.bus.channel == None):
            print("[EPOS begin] Got the following exception\n")
            return
        self.node = self.network.add_node(nodeID, object_dictionary=objectDitionary)
        self._connected = True

    def readObject(self, index, subindex):
        '''Reads an object

         Request a read from dictionary object referenced by index and subindex.

         Args:
             index:     reference of dictionary object index
             subindex:  reference of dictionary object subindex
         Returns:
             answer:  message returned by EPOS or empty if unsucessfull
        '''
        if self._connected:
           return self.node.sdo.upload(index, subindex)
        else:
            print('[EPOS] Error: Epos is not connected\n')
            return

    def writeObject(self, index, subindex, data):
        '''Write an object

         Request a write to dictionary object referenced by index and subindex.

         Args:
             index:     reference of dictionary object index
             subindex:  reference of dictionary object subindex
             data:      data to be stored
         Returns:
             answer:  message returned by EPOS or empty if unsucessfull
             OK:      boolean if all went ok or not
        '''
        if self._connected:
            return self.node.sdo.download(index, subindex, data)
        else:
            print('[EPOS] Error: Epos is not connected\n')
            return



def main():

    import argparse
    if (sys.version_info < (3, 0)):
        print("Please use python version 3\n")
        return

    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(description='Test Epos CANopen Communication\n')

    epos = Epos()
    # epos.begin(1)
    epos.begin(1, objectDitionary='maxon-70_10.eds')
    for obj in epos.node.object_dictionary.values():
        print('0x%X: %s' % (obj.index, obj.name))
        if isinstance(obj, canopen.objectdictionary.Record):
            for subobj in obj.values():
                print('  %d: %s' % (subobj.subindex, subobj.name))

    error_log = epos.node.sdo['Error History']
    # Iterate over arrays or records
    for error in error_log.values():
        print("Error 0x%X was found in the log" % error.raw)
    # try to read status word
    statusword = epos.readObject(0x6041, 0)
    if not statusword:
        print("[EPOS] Error trying to read EPOS statusword\n")
    else:
        print("The statusword is \n Hex={0:#06X} Bin={0:#018b}".format(int.from_bytes(statusword, 'little')))
    controlword = epos.readObject(0x6040, 0)
    if not controlword:
        print("[EPOS] Error trying to read EPOS controlword\n")
    else:
        print("The controlword is \n Hex={0:#06X} Bin={0:#018b}".format(int.from_bytes(controlword, 'little')))

    # perform a reset, by using controlword
    controlword = int.from_bytes(controlword, 'little')
    controlword = (controlword |(1 << 7))
    print("The controlword is \n Hex={0:#06X} Bin={0:#018b}".format(controlword))
    # sending new controlword
    controlword = controlword.to_bytes(2, 'little')
    epos.writeObject(0x6040, 0, controlword)

    epos.network.disconnect()
    return

if __name__ == '__main__':
    main()
