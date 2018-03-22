import canopen
import logging
import sys


class Epos:
    channel = 'can0'
    bustype = 'socketcan'
    nodeID = 1
    network = None
    _connected = False

    # List of motor types
    motorType = {'DC motor': 1, 'Sinusoidal PM BL motor': 10,
                 'Trapezoidal PM BL motor': 11}
    # If EDS file is present, this is not necessary, all codes can be gotten
    # from object dicionary.

    objectIndex = {'Device Type': 0x1000,
                   'Error Register': 0x1001,
                   'Error History': 0x1003,
                   'COB-ID SYNC Message': 0x1005,
                   'Device Name': 0x1008,
                   'Guard Time': 0x100C,
                   'Life Time Factor': 0x100D,
                   'Store Parameters': 0x1010,
                   'Restore Default Parameters': 0x1011,
                   'COB-ID Emergency Object': 0x1014,
                   'Consumer Heartbeat Time': 0x1016,
                   'Producer Heartbeat Time': 0x1017,
                   'Identity Object': 0x1018,
                   'Verify configuration': 0x1020,
                   'Server SDO 1 Parameter': 0x1200,
                   'Receive PDO 1 Parameter': 0x1400,
                   'Receive PDO 2 Parameter': 0x1401,
                   'Receive PDO 3 Parameter': 0x1402,
                   'Receive PDO 4 Parameter': 0x1403,
                   'Receive PDO 1 Mapping': 0x1600,
                   'Receive PDO 2 Mapping': 0x1601,
                   'Receive PDO 3 Mapping': 0x1602,
                   'Receive PDO 4 Mapping': 0x1603,
                   'Transmit PDO 1 Parameter': 0x1800,
                   'Transmit PDO 2 Parameter': 0x1801,
                   'Transmit PDO 3 Parameter': 0x1802,
                   'Transmit PDO 4 Parameter': 0x1803,
                   'Transmit PDO 1 Mapping': 0x1A00,
                   'Transmit PDO 2 Mapping': 0x1A01,
                   'Transmit PDO 3 Mapping': 0x1A02,
                   'Transmit PDO 4 Mapping': 0x1A03,
                   'Node ID': 0x2000,
                   'CAN Bitrate': 0x2001,
                   'RS232 Baudrate': 0x2002,
                   'Version Numbers': 0x2003,
                   'Serial Number': 0x2004,
                   'RS232 Frame Timeout': 0x2005,
                   'Miscellaneous Configuration': 0x2008,
                   'Internal Dip Switch State': 0x2009,
                   'Custom persistent memory': 0x200C,
                   'Internal DataRecorder Control': 0x2010,
                   'Internal DataRecorder Configuration': 0x2011,
                   'Internal DataRecorder Sampling Period': 0x2012,
                   'Internal DataRecorder Number of Preceding Samples': 0x2013,
                   'Internal DataRecorder Number of Sampling Variables': 0x2014,
                   'DataRecorder Index of Variables': 0x2015,
                   'Internal DataRecorder SubIndex of Variables': 0x2016,
                   'Internal DataRecorder Status': 0x2017,
                   'Internal DataRecorder Max Number of Samples': 0x2018,
                   'Internal DataRecorder Number of Recorded Samples': 0x2019,
                   'Internal DataRecorder Vector Start Offset': 0x201A,
                   'Encoder Counter': 0x2020,
                   'Encoder Counter at Index Pulse': 0x2021,
                   'Hallsensor Pattern': 0x2022,
                   'Internal Object Demand Rotor Angle': 0x2023,
                   'Internal System State': 0x2024,
                   'Internal Object Reserved': 0x2025,
                   'Internal Object ProcessMemory': 0x2026,
                   'Current Actual Value Averaged': 0x2027,
                   'Velocity Actual Value Averaged': 0x2028,
                   'Internal Object Actual Rotor Angle': 0x2029,
                   'Internal Object NTC Temperatur Sensor Value': 0x202A,
                   'Internal Object Motor Phase Current U': 0x202B,
                   'Internal Object Motor Phase Current V': 0x202C,
                   'Internal Object Measured Angle Difference': 0x202D,
                   'Trajectory Profile Time': 0x202E,
                   'CurrentMode Setting Value': 0x2030,
                   'PositionMode Setting Value': 0x2062,
                   'VelocityMode Setting Value': 0x206B,
                   'Configuration Digital Inputs': 0x2070,
                   'Digital Input Funtionalities': 0x2071,
                   'Position Marker': 0x2074,
                   'Digital Output Funtionalities': 0x2078,
                   'Configuration Digital Outputs': 0x2079,
                   'Analog Inputs': 0x207C,
                   'Current Threshold for Homing Mode': 0x2080,
                   'Home Position': 0x2081,
                   'Following Error Actual Value': 0x20F4,
                   'Sensor Configuration': 0x2210,
                   'Digital Position Input': 0x2300,
                   'Internal Object Download Area': 0x2FFF,
                   'ControlWord': 0x6040,
                   'StatusWord': 0x6041,
                   'Modes of Operation': 0x6060,
                   'Modes of Operation Display': 0x6061,
                   'Position Demand Value': 0x6062,
                   'Position Actual Value': 0x6064,
                   'Max Following Error': 0x6065,
                   'Position Window': 0x6067,
                   'Position Window Time': 0x6068,
                   'Velocity Sensor Actual Value': 0x6069,
                   'Velocity Demand Value': 0x606B,
                   'Velocity Actual Value': 0x606C,
                   'Current Actual Value': 0x6078,
                   'Target Position': 0x607A,
                   'Home Offset': 0x607C,
                   'Software Position Limit': 0x607D,
                   'Max Profile Velocity': 0x607F,
                   'Profile Velocity': 0x6081,
                   'Profile Acceleration': 0x6083,
                   'Profile Deceleration': 0x6084,
                   'QuickStop Deceleration': 0x6085,
                   'Motion ProfileType': 0x6086,
                   'Position Notation Index': 0x6089,
                   'Position Dimension Index': 0x608A,
                   'Velocity Notation Index': 0x608B,
                   'Velocity Dimension Index': 0x608C,
                   'Acceleration Notation Index': 0x608D,
                   'Acceleration Dimension Index': 0x608E,
                   'Homing Method': 0x6098,
                   'Homing Speeds': 0x6099,
                   'Homing Acceleration': 0x609A,
                   'Torque Control Parameter': 0x60F6,
                   'Speed Control Parameter': 0x60F9,
                   'Position Control Parameter': 0x60FB,
                   'TargetVelocity': 0x60FF,
                   'MotorType': 0x6402,
                   'Motor Data': 0x6410,
                   'Supported Drive Modes': 0x6502}

    node = []
    state = {0: 'start', 1: 'not ready to switch on', 2: 'switch on disable', 3: 'ready to switch on', 4: 'switched on', 5: 'refresh', 6: 'measure init', 7: 'operation enable', 8: 'quick stop active', 9: 'fault reaction active (disabled)', 10: 'fault reaction active (enable)', 11: 'fault', -1: 'Unknown'}

    def __init__(self, _network=None):

        # check if network is passed over or create a new one
        if not _network:
            self.network = canopen.Network()
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
        try:
            self.node = self.network.add_node(
                nodeID, object_dictionary=objectDitionary)
            self.network.connect(channel=_channel, bustype=_bustype)
            self._connected = True
        except Exception as e:
            print('[Epos:{0}] Exception caught:{1}\n'.format(
                sys._getframe().f_code.co_name, str(e)))
            self._connected = False
        finally:
            return self._connected

    def disconnect(self):
        self.network.disconnect
        return

    # Basic set of functions
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
            try:
                return self.node.sdo.upload(index, subindex)
            except Exception as e:
                print('[Epos:{0}] Exception caught:{1}\n'.format(
                    sys._getframe().f_code.co_name, str(e)))
                return None
        else:
            print('[EPOS:{0}] Error: Epos is not connected\n'.format(
                sys._getframe().f_code.co_name))
            return None

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
            print('[EPOS:{0}] Error: Epos is not connected\n'.format(
                sys._getframe().f_code.co_name))
            return

    ############################################################################
    # High level functions
    ############################################################################
    def readStatusWord(self):
        index = self.objectIndex['StatusWord']
        subindex = 0
        statusword = self.readObject(index, subindex)
        if not None:
            return statusword, True
        else:
            return None, False


    def readControlWord(self):
        # return controlword
        pass

    def writeControlWord(self):
        # return OK
        pass

    def checkEposState(self):
        '''Check current state of Epos

         Ask the StatusWord of EPOS and parse it to return the current state of
		 EPOS.

         +---------------------------------+-----+---------------------+
		 |State                            | ID  | Statusword [binary] |
		 +=================================+=====+=====================+
		 | Start                           | 0   | x0xx xxx0  x000 0000|
		 +---------------------------------+-----+---------------------+
		 | Not Ready to Switch On          | 1   | x0xx xxx1  x000 0000|
		 +---------------------------------+-----+---------------------+
		 |Switch on disabled               | 2   | x0xx xxx1  x100 0000|
		 +---------------------------------+-----+---------------------+
		 |ready to switch on               | 3   | x0xx xxx1  x010 0001|
		 +---------------------------------+-----+---------------------+
		 |switched on                      | 4   | x0xx xxx1  x010 0011|
		 +---------------------------------+-----+---------------------+
		 |refresh                          | 5   | x1xx xxx1  x010 0011|
		 +---------------------------------+-----+---------------------+
		 |measure init                     | 6   | x1xx xxx1  x011 0011|
		 +---------------------------------+-----+---------------------+
		 |operation enable                 | 7   | x0xx xxx1  x011 0111|
		 +---------------------------------+-----+---------------------+
		 |quick stop active                | 8   | x0xx xxx1  x001 0111|
		 +---------------------------------+-----+---------------------+
		 |fault reaction active (disabled) | 9   | x0xx xxx1  x000 1111|
		 +---------------------------------+-----+---------------------+
		 |fault reaction active (enabled)  | 10  | x0xx xxx1  x001 1111|
		 +---------------------------------+-----+---------------------+
		 |Fault                            | 11  | x0xx xxx1  x000 1000|
		 +---------------------------------+-----+---------------------+
		 see section 8.1.1 of firmware manual for more details.

		 Returns:
		     ID:    numeric identification of the state or -1 in case of
                    fail.
		'''
        statusword, ok = self.readStatusWord()
        if not ok:
            print('[Epos:{0}] Failed to request StatusWord\n'.format(
                    sys._getframe().f_code.co_name))
        else:
            # change to int
            statusWord = int.from_bytes(statusword, 'little')

            # state 'start' (0)
			# statusWord == x0xx xxx0  x000 0000
            bitmask =0b0100000101111111
            if(bitmask & statusWord == 0):
                ID = 0
                return ID

			# state 'not ready to switch on' (1)
			# statusWord == x0xx xxx1  x000 0000
            bitmask = 0b0100000101111111
            if (bitmask & statusWord == 256):
            	ID = 1
            	return ID

            # state 'switch on disabled' (2)
            # statusWord == x0xx xxx1  x100 0000
            bitmask = 0b0100000101111111
            if(bitmask & statusWord == 320):
            	ID = 2
            	return ID

            # state 'ready to switch on' (3)
            # statusWord == x0xx xxx1  x010 0001
            bitmask = 0b0100000101111111
            if(bitmask & statusWord == 289):
            	ID = 3
            	return ID

            # state 'switched on' (4)
            # statusWord == x0xx xxx1  x010 0011
            bitmask = 0b0000000101111111
            if(bitmask & statusWord == 291):
            	ID = 4
            	return ID

            # state 'refresh' (5)
            # statusWord == x1xx xxx1  x010 0011
            bitmask = 0b0100000101111111
            if(bitmask & statusWord == 16675):
            	ID = 5
            	return ID

            # state 'measure init' (6)
            # statusWord == x1xx xxx1  x011 0011
            bitmask = 0b0100000101111111
            if(bitmask & statusWord == 16691):
            	ID = 6
            	return ID
            # state 'operation enable' (7)
            # statusWord == x0xx xxx1  x011 0111
            bitmask = 0b0100000101111111
            if(bitmask & statusWord == 311):
            	ID = 7
            	return ID

            # state 'Quick Stop Active' (8)
            # statusWord == x0xx xxx1  x001 0111
            bitmask = 0b0100000101111111
            if(bitmask & statusWord == 279):
            	ID = 8
            	return ID

            # state 'fault reaction active (disabled)' (9)
            # statusWord == x0xx xxx1  x000 1111
            bitmask = 0b0100000101111111
            if(bitmask & statusWord == 271):
            	ID = 9
            	return ID

            # state 'fault reaction active (enabled)' (10)
            # statusWord == x0xx xxx1  x001 1111
            bitmask = 0b0100000101111111
            if(bitmask & statusWord == 287):
            	ID = 10
            	return ID

            # state 'fault' (11)
            # statusWord == x0xx xxx1  x000 1000
            bitmask = 0b0100000101111111
            if(bitmask & statusWord == 264):
            	ID = 11
            	return ID

        # in case of unknown state or fail
        return -1

    def printEposState (self):
        ID = self.checkEposState()
        if ID is -1:
            print('[Epos:{0}] Error: Unknown state\n'.format(sys._getframe().f_code.co_name))
        else:
            print('[Epos:{0}] Current state [ID]:{1} [{2}]\n'.format( sys._getframe().f_code.co_name, self.state[ID], ID))
        return

    def printStatusWord(self):
        statusword, Ok = self.readStatusWord()
        if not Ok:
            print('[Epos:{0}] Failed to retreive statusword\n'.format(sys._getframe().f_code.co_name))
            return
        else:
            statusword = int.from_bytes(statusword, 'little')
            print("[Epos:{1}] The statusword is Hex={0:#06X} Bin={0:#018b}\n".format(
            statusword, sys._getframe().f_code.co_name))
            print('Bit 15: position referenced to home position:                  {0}\n'.format((statusword & (1 << 15))>>15))
            print('Bit 14: refresh cycle of power stage:                          {0}\n'.format((statusword & (1 << 14))>>14))
            print('Bit 13: OpMode specific, some error: [Following|Homing]        {0}\n'.format((statusword & (1 << 13))>>13))
            print('Bit 12: OpMode specific: [Set-point ack|Speed|Homing attained] {0}\n'.format((statusword & (1 << 12))>>12))
            print('Bit 11: Internal limit active:                                 {0}\n'.format((statusword & (1 << 11))>>11))
            print('Bit 10: Target reached:                                        {0}\n'.format((statusword & (1 << 10))>>10))
            print('Bit 09: Remote (NMT Slave State Operational):                  {0}\n'.format((statusword & (1 << 9 ))>>9))
            print('Bit 08: Offset current measured:                               {0}\n'.format((statusword & (1 << 8 ))>>8))
            print('Bit 07: not used (Warning):                                    {0}\n'.format((statusword & (1 << 7 ))>>7))
            print('Bit 06: Switch on disable:                                     {0}\n'.format((statusword & (1 << 6 ))>>6))
            print('Bit 05: Quick stop:                                            {0}\n'.format((statusword & (1 << 5 ))>>5))
            print('Bit 04: Voltage enabled (power stage on):                      {0}\n'.format((statusword & (1 << 4 ))>>4))
            print('Bit 03: Fault:                                                 {0}\n'.format((statusword & (1 << 3 ))>>3))
            print('Bit 02: Operation enable:                                      {0}\n'.format((statusword & (1 << 2 ))>>2))
            print('Bit 01: Switched on:                                           {0}\n'.format((statusword & (1 << 1 ))>>1))
            print('Bit 00: Ready to switch on:                                    {0}\n'.format(statusword & 1))
        return

def main():

    import argparse
    if (sys.version_info < (3, 0)):
        print("Please use python version 3\n")
        return

    parser = argparse.ArgumentParser(add_help=True,
                                     description='Test Epos CANopen Communication\n')
    parser.add_argument('--channel', '-c', action='store', default='can0',
                        type=str, help='Channel to be used', dest='channel')
    parser.add_argument('--bus', '-b', action='store',
                        default='socketcan', type=str, help='Bus type', dest='bus')
    parser.add_argument('--rate', '-r', action='store', default=None,
                        type=int, help='bitrate, if applicable', dest='bitrate')
    parser.add_argument('--nodeID', action='store', default=1, type=int,
                        help='Node ID [ must be between 1- 127]', dest='nodeID')
    parser.add_argument('--objDict', action='store', default=None,
                        type=str, help='Object dictionary file', dest='objDict')
    args = parser.parse_args()

    epos = Epos()
    # epos.begin(1)
    epos.begin(args.nodeID, objectDitionary=args.objDict)
    # check if EDS file is supplied and print it
    if args.objDict:
        for obj in epos.node.object_dictionary.values():
            print('0x%X: %s' % (obj.index, obj.name))
        if isinstance(obj, canopen.objectdictionary.Record):
            for subobj in obj.values():
                print('  %d: %s' % (subobj.subindex, subobj.name))

        # test record a single record
        error_log = epos.node.sdo['Error History']
        # Iterate over arrays or record
        for error in error_log.values():
            print("Error 0x%X was found in the log" % error.raw)

    # use simple hex values
    # try to read status word
    statusword = epos.readObject(0x6041, 0)
    if not statusword:
        print("[EPOS] Error trying to read EPOS statusword\n")
    else:
        print("The statusword is \n Hex={0:#06X} Bin={0:#018b}".format(
            int.from_bytes(statusword, 'little')))

    # test printStatusWord and state
    epos.printEposState()
    epos.printStatusWord()
    # try to read controlword using hex codes
    controlword = epos.readObject(0x6040, 0)
    if not controlword:
        print("[EPOS] Error trying to read EPOS controlword\n")
    else:
        print("The controlword is \n Hex={0:#06X} Bin={0:#018b}".format(
            int.from_bytes(controlword, 'little')))

    # perform a reset, by using controlword
    controlword = int.from_bytes(controlword, 'little')
    controlword = (controlword | (1 << 7))
    print("The controlword is \n Hex={0:#06X} Bin={0:#018b}".format(
        controlword))

    # sending new controlword
    controlword = controlword.to_bytes(2, 'little')
    epos.writeObject(0x6040, 0, controlword)
    # check led status to see if it is green and blinking

    epos.disconnect()
    return


if __name__ == '__main__':
    main()
