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
    #: CANopen defined error codes and Maxon codes also
    errorIndex = {0x00000000:  'Error code: no error',
                  0x06020000:  'Error code: object does not exist',
                  0x06090011:  'Error code: subindex does not exist',
                  0x05040005:  'Error code: out of memory',
                  0x06010000:  'Error code: Unsupported access to an object',
                  0x06010001:  'Error code: Attempt to read a write-only object',
                  0x06010002:  'Error code: Attempt to write a read-only object',
                  0x06040043:  'Error code: general parameter incompatibility',
                  0x06040047:  'Error code: general internal incompatibility in the device',
                  0x06060000:  'Error code: access failed due to an hardware error',
                  0x06090030:  'Error code: value range of parameter exeeded',
                  0x06090031:  'Error code: value of parameter written is too high',
                  0x06090032:  'Error code: value of parameter written is too low',
                  0x06090036:  'Error code: maximum value is less than minimum value',
                  0x08000000:  'Error code: General error',
                  0x08000020:  'Error code: Data cannot be transferred or stored to the application',
                  0x08000021:  'Error code: Data cannot be transferred or stored to the application because of local control',
                  0x08000022:  'Error code: Wrong Device State',
                  # Maxon defined error codes
                  0x0f00ffc0:  'Error code: wrong NMT state',
                  0x0f00ffbf:  'Error code: rs232 command illegeal',
                  0x0f00ffbe:  'Error code: password incorrect',
                  0x0f00ffbc:  'Error code: device not in service mode',
                  0x0f00ffB9:  'Error code: error in Node-ID'
                  }
    #: dictionary describing opMode
    opModes = {6: 'Homing Mode', 3: 'Profile Velocity Mode', 1: 'Profile Position Mode', 
			  -1: 'Position Mode', -2: 'Velocity Mode', -3:'Current Mode', -4: 'Diagnostic Mode',
              -5: 'MasterEncoder Mode', -6: 'Step/Direction Mode'}
    node = []
    #: dictionary object to describe state of EPOS device
    state = {0: 'start', 1: 'not ready to switch on', 2: 'switch on disable',
             3: 'ready to switch on', 4: 'switched on', 5: 'refresh',
             6: 'measure init', 7: 'operation enable', 8: 'quick stop active',
             9: 'fault reaction active (disabled)', 10: 'fault reaction active (enable)', 11: 'fault',
             -1: 'Unknown'}

    def __init__(self, _network=None, debug=False):

        # check if network is passed over or create a new one
        if not _network:
            self.network = canopen.Network()
        else:
            self.network = _network
        
        self.logger = logging.getLogger('EPOS')
        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

    def begin(self, nodeID, _channel='can0', _bustype='socketcan', objectDictionary=None):
        '''Initialize Epos device

        Configure and setup Epos device.

        Args:
            nodeID:    Node ID of the device.
            channel (optional):   Port used for communication. Default can0
            bustype (optional):   Port type used. Default socketcan.
            objectDictionary (optional):   Name of EDS file, if any available.
        Return:
            Ok:        A boolean if all went ok.
        '''
        try:
            self.node = self.network.add_node(
                nodeID, object_dictionary=objectDictionary)
            self.network.connect(channel=_channel, bustype=_bustype)
            self._connected = True
        except Exception as e:
            self.logger.info('[Epos:{0}] Exception caught:{1}\n'.format(
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
                self.logger.INFO('[Epos:{0}] Exception caught:{1}\n'.format(
                    sys._getframe().f_code.co_name, str(e)))
                return None
        else:
            self.logger.info('[EPOS:{0}] Error: Epos is not connected\n'.format(
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
             OK:      boolean if all went ok or not
        '''
        if self._connected:
            try:
                self.node.sdo.download(index, subindex, data)
                return True
            except canopen.SdoAbortedError as e:
                text = "Code 0x{:08X}".format(e.code)
                if e.code in self.errorIndex:
                    text = text + ", " + self.errorIndex[e.code]
                self.logger.info('[EPOS:{0}] SdoAbortedError: '.format(sys._getframe().f_code.co_name) + text)
                return False
            except canopen.SdoCommunicationError:
                self.logger.info('[EPOS:{0}] SdoAbortedError: Timeout or unexpected response'.format(sys._getframe().f_code.co_name))
                return False
        else:
            self.logger.info('[EPOS:{0}] Error: Epos is not connected\n'.format(
                sys._getframe().f_code.co_name))
            return False

    ############################################################################
    # High level functions
    ############################################################################

    def readStatusWord(self):
        '''Read StatusWord
        
        Request current statusword from device.

        Returns:
            statusword: the current controlword or None if any error.
            Ok: A boolean if all went ok.
        '''
        index = self.objectIndex['StatusWord']
        subindex = 0
        statusword = self.readObject(index, subindex)
        # failded to request?
        if not statusword:
            logging.info("[EPOS:{0}] Error trying to read EPOS statusword".format(
            sys._getframe().f_code.co_name))
            return statusword, False

        # return statusword as an int type
        statusword = int.from_bytes(statusword, 'little')
        return statusword, True
            

    def readControlWord(self):
        '''Read ControlWord
        
        Request current controlword from device.

        Returns:
            controlword: the current controlword or None if any error.
            Ok: A boolean if all went ok.
        '''
        index = self.objectIndex['ControlWord']
        subindex = 0
        controlword = self.readObject(index,subindex)
        # failded to request?
        if not controlword:
            logging.info("[EPOS:{0}] Error trying to read EPOS controlword".format(
            sys._getframe().f_code.co_name))
            return controlword, False
        
        # return controlword as an int type
        controlword = int.from_bytes(controlword, 'little')
        return controlword, True

    def writeControlWord(self, controlword):
        '''Send controlword to device

        Args:
            controlword: word to be sent.
        
        Returns:
            Ok: a boolean if all went ok. 
        '''
        # sending new controlword
        self.logger.debug('[EPOS:{0}] Sending controlword Hex={1:#06X} Bin={1:#018b}'.format(
            sys._getframe().f_code.co_name, controlword))
        controlword = controlword.to_bytes(2, 'little')
        return self.writeObject(0x6040, 0, controlword)
        
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
            self.logger.info('[Epos:{0}] Failed to request StatusWord\n'.format(
                sys._getframe().f_code.co_name))
        else:

            # state 'start' (0)
			# statusWord == x0xx xxx0  x000 0000
            bitmask = 0b0100000101111111
            if(bitmask & statusword == 0):
                ID = 0
                return ID

		# state 'not ready to switch on' (1)
		# statusWord == x0xx xxx1  x000 0000
            bitmask = 0b0100000101111111
            if (bitmask & statusword == 256):
            	ID = 1
            	return ID

            # state 'switch on disabled' (2)
            # statusWord == x0xx xxx1  x100 0000
            bitmask = 0b0100000101111111
            if(bitmask & statusword == 320):
            	ID = 2
            	return ID

            # state 'ready to switch on' (3)
            # statusWord == x0xx xxx1  x010 0001
            bitmask = 0b0100000101111111
            if(bitmask & statusword == 289):
            	ID = 3
            	return ID

            # state 'switched on' (4)
            # statusWord == x0xx xxx1  x010 0011
            bitmask = 0b0000000101111111
            if(bitmask & statusword == 291):
            	ID = 4
            	return ID

            # state 'refresh' (5)
            # statusWord == x1xx xxx1  x010 0011
            bitmask = 0b0100000101111111
            if(bitmask & statusword == 16675):
            	ID = 5
            	return ID

            # state 'measure init' (6)
            # statusWord == x1xx xxx1  x011 0011
            bitmask = 0b0100000101111111
            if(bitmask & statusword == 16691):
            	ID = 6
            	return ID
            # state 'operation enable' (7)
            # statusWord == x0xx xxx1  x011 0111
            bitmask = 0b0100000101111111
            if(bitmask & statusword == 311):
            	ID = 7
            	return ID

            # state 'Quick Stop Active' (8)
            # statusWord == x0xx xxx1  x001 0111
            bitmask = 0b0100000101111111
            if(bitmask & statusword == 279):
            	ID = 8
            	return ID

            # state 'fault reaction active (disabled)' (9)
            # statusWord == x0xx xxx1  x000 1111
            bitmask = 0b0100000101111111
            if(bitmask & statusword == 271):
            	ID = 9
            	return ID

            # state 'fault reaction active (enabled)' (10)
            # statusWord == x0xx xxx1  x001 1111
            bitmask = 0b0100000101111111
            if(bitmask & statusword == 287):
            	ID = 10
            	return ID

            # state 'fault' (11)
            # statusWord == x0xx xxx1  x000 1000
            bitmask = 0b0100000101111111
            if(bitmask & statusword == 264):
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
            print("[Epos:{1}] The statusword is Hex={0:#06X} Bin={0:#018b}\n".format(
            statusword, sys._getframe().f_code.co_name))
            print('Bit 15: position referenced to home position:                  {0}'.format((statusword & (1 << 15))>>15))
            print('Bit 14: refresh cycle of power stage:                          {0}'.format((statusword & (1 << 14))>>14))
            print('Bit 13: OpMode specific, some error: [Following|Homing]        {0}'.format((statusword & (1 << 13))>>13))
            print('Bit 12: OpMode specific: [Set-point ack|Speed|Homing attained] {0}'.format((statusword & (1 << 12))>>12))
            print('Bit 11: Internal limit active:                                 {0}'.format((statusword & (1 << 11))>>11))
            print('Bit 10: Target reached:                                        {0}'.format((statusword & (1 << 10))>>10))
            print('Bit 09: Remote (NMT Slave State Operational):                  {0}'.format((statusword & (1 << 9 ))>>9))
            print('Bit 08: Offset current measured:                               {0}'.format((statusword & (1 << 8 ))>>8))
            print('Bit 07: not used (Warning):                                    {0}'.format((statusword & (1 << 7 ))>>7))
            print('Bit 06: Switch on disable:                                     {0}'.format((statusword & (1 << 6 ))>>6))
            print('Bit 05: Quick stop:                                            {0}'.format((statusword & (1 << 5 ))>>5))
            print('Bit 04: Voltage enabled (power stage on):                      {0}'.format((statusword & (1 << 4 ))>>4))
            print('Bit 03: Fault:                                                 {0}'.format((statusword & (1 << 3 ))>>3))
            print('Bit 02: Operation enable:                                      {0}'.format((statusword & (1 << 2 ))>>2))
            print('Bit 01: Switched on:                                           {0}'.format((statusword & (1 << 1 ))>>1))
            print('Bit 00: Ready to switch on:                                    {0}'.format(statusword & 1))
        return

    def printControlWord(self, controlword=None):
        '''Print the meaning of controlword

        Check the meaning of current controlword of device or check the meaning of your own controlword.
        Usefull to check your own controlword before actually sending it to device.

        Args:
            controlword (optional): If None, request the controlword of device.
             
        '''
        if not controlword:
            controlword, Ok = self.readControlWord()
            if not Ok:
                print('[Epos:{0}] Failed to retreive controlword\n'.format(sys._getframe().f_code.co_name))
                return
        else:
            print("[Epos:{1}] The controlword is Hex={0:#06X} Bin={0:#018b}\n".format(
            controlword, sys._getframe().f_code.co_name))
            # Bit 15 to 11 not used, 10 to 9 reserved
            print('Bit 08: Halt:                                                                   {0}'.format((controlword & (1 << 8 ))>>8))
            print('Bit 07: Fault reset:                                                            {0}'.format((controlword & (1 << 7 ))>>7))
            print('Bit 06: Operation mode specific:[Abs=0|rel=1]                                   {0}'.format((controlword & (1 << 6 ))>>6))
            print('Bit 05: Operation mode specific:[Change set immediately]                        {0}'.format((controlword & (1 << 5 ))>>5))
            print('Bit 04: Operation mode specific:[New set-point|reserved|Homing operation start] {0}'.format((controlword & (1 << 4 ))>>4))
            print('Bit 03: Enable operation:                                                       {0}'.format((controlword & (1 << 3 ))>>3))
            print('Bit 02: Quick stop:                                                             {0}'.format((controlword & (1 << 2 ))>>2))
            print('Bit 01: Enable voltage:                                                         {0}'.format((controlword & (1 << 1 ))>>1))
            print('Bit 00: Switch on:                                                              {0}'.format(controlword & 1))
        return


    def readPositionModeSetting(self):
        '''Reads the setted desired Position
		
        Ask Epos device for demand position object. If a correct
        request is made, the position is placed in answer. If
        not, an answer will be empty
		
        Returns:
            position: the demanded position value.
            OK:       A boolean if all requests went ok or not.
        '''
        index = self.objectIndex['PositionMode Setting Value']
        subindex = 0
        position = self.readObject(index, subindex)
        # failded to request?
        if not position:
            logging.info("[EPOS:{0}] Error trying to read EPOS PositionMode Setting Value".format(
            sys._getframe().f_code.co_name))
            return position, False
        # return value as signed int
        position = int.from_bytes(position, 'little', signed=True)
        return position, True

    def setPositionModeSetting(self, position):
        '''Sets the desired Position

        Ask Epos device to define position mode setting object.

        Returns:
            OK: A boolean if all requests went ok or not.
        '''
        index = self.objectIndex['PositionMode Setting Value']
        subindex = 0
        if(position < -2**31 or position > 2**31-1):
            print('[Epos:{0}] Postion out of range'.format(sys._getframe().f_code.co_name))
            return False
        # change to bytes as an int32 value
        position = position.to_bytes(4, 'little', signed=True)
        return self.writeObject(index, subindex, position)

    def readVelocityModeSetting(self):
        '''Reads the setted desired velocity

        Asks EPOS for the desired velocity value in velocity control mode

        Returns:
            velocity: Value setted or None if any error.
            Ok: A boolean if sucessfull or not.
        '''
        index = self.objectIndex['VelocityMode Setting Value']
        subindex = 0
        velocity = self.readObject(index, subindex)
        # failded to request?
        if not velocity:
            logging.info("[EPOS:{0}] Error trying to read EPOS VelocityMode Setting Value".format(
            sys._getframe().f_code.co_name))
            return velocity, False
        # return value as signed int
        velocity = int.from_bytes(velocity, 'little', signed=True)
        return velocity, True

    def setVelocityModeSetting(self, velocity):
        '''Set desired velocity

        Set the value for desired velocity in velocity control mode.

        Args:
            velocity: value to be setted.
        Returns:
            Ok: a boolean if sucessfull or not.
        '''
        index = self.objectIndex['VelocityMode Setting Value']
        subindex = 0
        if(velocity < -2**31 or velocity > 2**31-1):
            print('[Epos:{0}] Velocity out of range'.format(sys._getframe().f_code.co_name))
            return False
        # change to bytes as an int32 value
        velocity = velocity.to_bytes(4, 'little', signed=True)
        return self.writeObject(index, subindex, velocity)

    def readCurrentModeSetting(self):
        '''Read current value setted

        Asks EPOS for the current value setted in current control mode.

        Returns:
            current: value setted.
            Ok:      a boolean if sucessfull or not.
        '''
        index = self.objectIndex['CurrentMode Setting Value']
        subindex = 0
        current = self.readObject(index, subindex)
        # failed to request
        if not current:
            logging.info("[EPOS:{0}] Error trying to read EPOS CurrentMode Setting Value".format(
            sys._getframe().f_code.co_name))
            return current, False
        # return value as signed int
        current = int.from_bytes(current, 'little', signed=True)
        return current, True
    
    def setCurrentModeSetting(self, current):
        '''Set disered current

        Set the value for desired current in current control mode

        Args:
            current: the value to be set [mA]
        
        Returns:
            Ok: a boolean if sucessfull or not
        '''
        index = self.objectIndex['CurrentMode Setting Value']
        subindex = 0
        if(current <-2**15 or current > 2**15-1):
            print('[Epos:{0}] Current out of range'.format(sys._getframe().f_code.co_name))
            return False
        # change to bytes as an int16 value
        current = current.to_bytes(2, 'little', signed=True)
        return self.writeObject(index, subindex, current)

    def readOpMode(self):
        '''Read current operation mode

        Returns:
            opMode: current opMode or None if request fails
            Ok:     A boolean if sucessfull or not
        '''
        index = self.objectIndex['Modes of Operation']
        subindex = 0
        opMode = self.readObject(index, subindex)
        # failed to request
        if not opMode:
            logging.info("[EPOS:{0}] Error trying to read EPOS Operation Mode".format(
            sys._getframe().f_code.co_name))
            return opMode, False
        # change to int value
        opMode = int.from_bytes(opMode, 'little')
        return opMode, True

    def setOpMode(self, opMode):
        '''Set Operation mode

        Sets the operation mode of Epos. OpMode is described as:

        +--------+-----------------------+
        | OpMode | Description           |
        +========+=======================+
        | 6      | Homing Mode           |
        +--------+-----------------------+
        | 3      | Profile Velocity Mode |
        +--------+-----------------------+
        | 1      | Profile Position Mode |
        +--------+-----------------------+
        | -1     | Position Mode         |
        +--------+-----------------------+
        | -2     | Velocity Mode         |
        +--------+-----------------------+
        | -3     | Current Mode          |
        +--------+-----------------------+
        | -4     | Diagnostic Mode       |
        +--------+-----------------------+
        | -5     | MasterEncoder Mode    |
        +--------+-----------------------+
        | -6     | Step/Direction Mode   |
        +--------+-----------------------+

        Args:
            opMode: the desired opMode.
        Returns:
            OK:     A boolean if all requests went ok or not.
        '''
        index = self.objectIndex['Modes of Operation']
        subindex = 0
        if not opMode  in self.opModes:
            logging.info('[EPOS:{0}] Unkown Operation Mode: {1}'.format(sys._getframe().f_code.co_name, opMode))
            return False
        opMode = opMode.to_bytes(1, 'little', signed=True)
        return self.writeObject(index, subindex, opMode)
    
    def printOpMode(self):
        '''Print current operation mode
        '''
        opMode, Ok = self.readOpMode()
        if not Ok:
            print('Failed to request current operation mode')
            return
        if not (opMode  in self.opModes):
            logging.info('[EPOS:{0}] Unkown Operation Mode: {1}'.format(sys._getframe().f_code.co_name, opMode))
            return
        else:
            print('Current operation mode is \"{}\"'.format(self.opModes[opMode]))
            return

    def changeEposState(self, newState):
        '''Change EPOS state

        Change Epos state using controlWord object

        To change Epos state, a write to controlWord object is made.
        The bit change in controlWord is made as shown in the following table:
        +-----------------+--------------------------------+
        |State            | LowByte of Controlword [binary]|
        +=================+================================+
        |shutdown         | 0xxx x110                      |
        +-----------------+--------------------------------+
        |switch on        | 0xxx x111                      |
        +-----------------+--------------------------------+
        |disable voltage  | 0xxx xx0x                      |
        +-----------------+--------------------------------+
        |quick stop       | 0xxx x01x                      |
        +-----------------+--------------------------------+
        |disable operation| 0xxx 0111                      |
        +-----------------+--------------------------------+
        |enable operation | 0xxx 1111                      |
        +-----------------+--------------------------------+
        |fault reset      | 1xxx xxxx                      |
        +-----------------+--------------------------------+

        see section 8.1.3 of firmware for more information

        Args:
            newState: string with state witch user want to switch.

        Returns:
            OK: boolean if all went ok and no error was received.
        '''
        stateOrder = ['shutdown', 'switch on', 'disable voltage', 'quick stop',
                      'disable operation', 'enable operation', 'fault reset']
        
        if not (newState in stateOrder):
            logging.info('[EPOS:{0}] Unkown state: {1}'.format(sys._getframe().f_code.co_name, newState))
            return False
        else:
            controlword, Ok = self.readControlWord()
            if not Ok:
                logging.info('[EPOS:{0}] Failed to retreive controlword'.format(sys._getframe().f_code.co_name))
                return False
            # shutdown  0xxx x110  
            if newState == 'shutdown':
                # clear bits
                mask = not ( 1<<7 | 1<<0 )
                controlword = controlword & mask
                # set bits
                mask  = ( 1<< 2 | 1<<1 )
                controlword = controlword | mask
                return self.writeControlWord(controlword)
            # switch on 0xxx x111 
            if newState == 'switch on':
                # clear bits
                mask = not ( 1<<7 )
                controlword = controlword & mask
                # set bits
                mask  = ( 1<< 2 | 1<<1 | 1<<0 )
                controlword = controlword | mask
                return self.writeControlWord(controlword)
            # disable voltage 0xxx xx0x
            if newState == 'switch on':
                # clear bits
                mask = not ( 1<<7 | 1 << 1 )
                controlword = controlword & mask
                return self.writeControlWord(controlword)
            # quick stop 0xxx x01x
            if newState == 'quick stop':
                # clear bits
                mask = not ( 1<<7 | 1 << 2)
                controlword = controlword & mask
                # set bits
                mask  = ( 1<<1 )
                controlword = controlword | mask
                return self.writeControlWord(controlword)
            # disable operation 0xxx 0111
            if newState == 'disable operation':
                # clear bits
                mask = not ( 1<<7 | 1 << 3)
                controlword = controlword & mask
                # set bits
                mask  = ( 1<<2 | 1<< 1 | 1<<0 )
                controlword = controlword | mask
                return self.writeControlWord(controlword)
            # enable operation 0xxx 1111
            if newState == 'enable operation':
                # clear bits
                mask = not ( 1<<7 )
                controlword = controlword & mask
                # set bits
                mask  = ( 1<< 3 | 1 << 2 | 1 << 1 | 1 << 0 )
                controlword = controlword | mask
                return self.writeControlWord(controlword)
            # fault reset 1xxx xxxx
            if newState == 'fault reset':
                # set bits
                mask  = ( 1<<7 )
                controlword = controlword | mask
                return self.writeControlWord(controlword)



    def setMotorConfig(self, motorType, currentLimit, maximumSpeed, polePairNumber):
        '''Set motor configuration

        Sets the configuration of the motor parameters. The valid motor type is:

        +-----------------------+------+--------------------------+
        |motorType              | value| Description              |
        +=======================+======+==========================+
        |DC motor               | 1    | brushed DC motor         |
        +-----------------------+------+--------------------------+
        |Sinusoidal PM BL motor | 10   | EC motor sinus commutated|
        +-----------------------+------+--------------------------+
        |Trapezoidal PM BL motor| 11   | EC motor block commutated|
        +-----------------------+------+--------------------------+

        The current limit is the current limit is the maximal permissible
        continuous current of the motor in mA.
        Minimum value is 0 and max is hardware dependent.

        The output current limit is recommended to be 2 times the continuous
        current limit.

        The pole pair number refers to the number of magnetic pole pairs
        (number of poles / 2) from rotor of a brushless DC motor.

        The maximum speed is used to prevent mechanical destroys in current
        mode. It is possible to limit the velocity [rpm]

        Thermal winding not changed, using default 40ms.

        Args:
            motorType:      value of motor type. see table behind.
            currentLimit:   max continuous current limit [mA].
            maximumSpeed:   max allowed speed in current mode [rpm].
            polePairNumber: number of pole pairs for brushless DC motors.
        Returns:
            OK:     A boolean if all requests went ok or not.
        '''
        #------------------------------------------------------------------------
        # check values of input
        #------------------------------------------------------------------------
        if not ((motorType in self.motorType ) or (motorType in self.motorType.values())):
            logging.info('[EPOS:{0}] Unknow motorType: {1} '.format(sys._getframe().f_code.co_name, motorType))
            return False
        if (currentLimit < 0 ) or (currentLimit > 2**16 -1 ):
            logging.info('[EPOS:{0}] Current limit out of range: {1} '.format(sys._getframe().f_code.co_name, currentLimit))
            return False
        if (polePairNumber <0 ) or (polePairNumber > 255):
            logging.info('[EPOS:{0}] Pole pair number out of range: {1} '.format(sys._getframe().f_code.co_name, polePairNumber))
            return False
        if (maximumSpeed < 1) or (maximumSpeed > 2**16 -1):
            logging.info('[EPOS:{0}] Maximum speed out of range: {1} '.format(sys._getframe().f_code.co_name, maximumSpeed))
            return False
        #------------------------------------------------------------------------
        # store motorType
        #------------------------------------------------------------------------
        index = self.objectIndex['MotorType']
        subindex = 0
        if motorType in self.motorType:
            motorType = self.motorType[motorType]
        Ok = self.writeObject(index, subindex, motorType.to_bytes(1, 'little'))
        if not Ok:
            logging.info('[EPOS:{0}] Failed to set motorType'.format(sys._getframe().f_code.co_name))
            return Ok
        #------------------------------------------------------------------------
        # store motorData
        #------------------------------------------------------------------------
        index = self.objectIndex['Motor Data']
        # check if it was passed a float
        if (type(currentLimit) == type(1.0)):
            # if true trunc to closes int, similar to floor
            currentLimit=currentLimit.__trunc__
        # constant current limit has subindex 1
        Ok = self.writeObject(index, 1, currentLimit.to_bytes(2, 'little'))
        if not Ok:
            logging.info('[EPOS:{0}] Failed to set currentLimit'.format(sys._getframe().f_code.co_name))
            return Ok
        # output current limit has subindex 2 and is recommended to
        # be the double of constant current limit
        Ok = self.writeObject(index, 2, (currentLimit * 2).to_bytes(2, 'little'))
        if not Ok:
            logging.info('[EPOS:{0}] Failed to set output current limit'.format(sys._getframe().f_code.co_name))
            return Ok
        # pole pair number has subindex 3
        Ok = self.writeObject(index, 3, polePairNumber.to_bytes(1, 'little'))
        if not Ok:
            logging.info('[EPOS:{0}] Failed to set pole pair number: {1}'.format(sys._getframe().f_code.co_name, polePairNumber))
            return Ok
        # maxSpeed has subindex 4
        # check if it was passed a float
        if (type(maximumSpeed) == type(1.0)):
            # if true trunc to closes int, similar to floor
            maximumSpeed=maximumSpeed.__trunc__
        Ok = self.writeObject(index, 4, maximumSpeed.to_bytes(2, 'little'))
        if not Ok:
            logging.info('[EPOS:{0}] Failed to set maximum speed: {1}'.format(sys._getframe().f_code.co_name, maximumSpeed))
            return Ok

def main():

    import argparse
    if (sys.version_info < (3, 0)):
        print("Please use python version 3")
        return

    parser = argparse.ArgumentParser(add_help=True,
                                     description='Test Epos CANopen Communication')
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

    
    # set up logging to file - see previous section for more details
    logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s.%(msecs)03d] [%(name)-12s]: %(levelname)-8s %(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S',
                    filename='epos.log',
                    filemode='w')
    # define a Handler which writes INFO messages or higher
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)

    # instanciate object
    epos = Epos()
    
    if not (epos.begin(args.nodeID, objectDictionary=args.objDict)):
        logging.info('Failed to begin connection with EPOS device')
        logging.info('Exiting now')
        return
    
    # check if EDS file is supplied and print it
    if args.objDict:
        print('----------------------------------------------------------', flush=True)
        print('Printing EDS file entries')
        print('----------------------------------------------------------', flush=True)
        for obj in epos.node.object_dictionary.values():
            print('0x%X: %s' % (obj.index, obj.name))
        if isinstance(obj, canopen.objectdictionary.Record):
            for subobj in obj.values():
                print('  %d: %s' % (subobj.subindex, subobj.name))
        print('----------------------------------------------------------', flush=True)
        # test record a single record
        error_log = epos.node.sdo['Error History']
        # Iterate over arrays or record
        for error in error_log.values():
            print("Error 0x%X was found in the log" % error.raw)
        
        print('----------------------------------------------------------', flush=True)

    # use simple hex values
    # try to read status word
    statusword, ok = epos.readObject(0x6041, 0)
    if not ok:
        print("[EPOS] Error trying to read EPOS statusword\n")
    else:
        print('----------------------------------------------------------', flush=True)
        print("The statusword is \n Hex={0:#06X} Bin={0:#018b}".format(
            int.from_bytes(statusword, 'little')))

    # test printStatusWord and state
    print('----------------------------------------------------------', flush=True)
    print('Testing print of StatusWord and State and ControlWord')
    print('----------------------------------------------------------', flush=True)
    epos.printEposState()
    print('----------------------------------------------------------', flush=True)
    epos.printStatusWord()
    print('----------------------------------------------------------', flush=True)
    # try to read controlword using hex codes
    controlword = epos.readObject(0x6040, 0)
    if not controlword:
        logging.info("[EPOS] Error trying to read EPOS controlword\n")
    else:
        print("The controlword is \n Hex={0:#06X} Bin={0:#018b}".format(
            int.from_bytes(controlword, 'little')))
        print('----------------------------------------------------------', flush=True)
        # perform a reset, by using controlword
        controlword = int.from_bytes(controlword, 'little')
        controlword = (controlword | (1 << 7))
        print('----------------------------------------------------------', flush=True)
        print("The new controlword is \n Hex={0:#06X} Bin={0:#018b}".format(
            controlword))
        print('----------------------------------------------------------', flush=True)
        # sending new controlword
        controlword = controlword.to_bytes(2, 'little')
        epos.writeObject(0x6040, 0, controlword)
        # check led status to see if it is green and blinking
    
    epos.disconnect()
    return


if __name__ == '__main__':
    main()
