#!/usr/bin/python
# -*- coding: utf-8 -*-
# The MIT License (MIT)
# Copyright (c) 2018 Bruno Tibério
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
                   'Current Control Parameter': 0x60F6,
                   'Speed Control Parameter': 0x60F9,
                   'Position Control Parameter': 0x60FB,
                   'TargetVelocity': 0x60FF,
                   'MotorType': 0x6402,
                   'Motor Data': 0x6410,
                   'Supported Drive Modes': 0x6502}
    # CANopen defined error codes and Maxon codes also
    errorIndex = {0x00000000:  'Error code: no error',
                  # 0x050x xxxx
                  0x05030000:  'Error code: toogle bit not alternated',
                  0x05040000:  'Error code: SDO protocol timeout',
                  0x05040001:  'Error code: Client/server command specifier not valid or unknown',
                  0x05040002:  'Error code: invalide block size',
                  0x05040003:  'Error code: invalide sequence number',
                  0x05040004:  'Error code: CRC error',
                  0x05040005:  'Error code: out of memory',
                  # 0x060x xxxx
                  0x06010000:  'Error code: Unsupported access to an object',
                  0x06010001:  'Error code: Attempt to read a write-only object',
                  0x06010002:  'Error code: Attempt to write a read-only object',
                  0x06020000:  'Error code: object does not exist',
                  0x06040041:  'Error code: object can not be mapped to the PDO',
                  0x06040042:  'Error code: the number and length of the objects to be mapped would exceed PDO length',
                  0x06040043:  'Error code: general parameter incompatibility',
                  0x06040047:  'Error code: general internal incompatibility in the device',
                  0x06060000:  'Error code: access failed due to an hardware error',
                  0x06070010:  'Error code: data type does not match, length of service parameter does not match',
                  0x06070012:  'Error code: data type does not match, length of service parameter too high',
                  0x06070013:  'Error code: data type does not match, length of service parameter too low',
                  0x06090011:  'Error code: subindex does not exist',
                  0x06090030:  'Error code: value range of parameter exeeded',
                  0x06090031:  'Error code: value of parameter written is too high',
                  0x06090032:  'Error code: value of parameter written is too low',
                  0x06090036:  'Error code: maximum value is less than minimum value',
                  0x060A0023:  'Error code: resource not available: SDO connection',
                  # 0x0800 xxxx
                  0x08000000:  'Error code: General error',
                  0x08000020:  'Error code: Data cannot be transferred or stored to the application',
                  0x08000021:  'Error code: Data cannot be transferred or stored to the application because of local control',
                  0x08000022:  'Error code: Wrong Device State. Data can not be transfered',
                  0x08000023:  'Error code: Object dictionary dynamic generation failed or no object dictionary present',
                  # Maxon defined error codes
                  0x0f00ffc0:  'Error code: wrong NMT state',
                  0x0f00ffbf:  'Error code: rs232 command illegeal',
                  0x0f00ffbe:  'Error code: password incorrect',
                  0x0f00ffbc:  'Error code: device not in service mode',
                  0x0f00ffB9:  'Error code: error in Node-ID'
                  }
    # dictionary describing opMode
    opModes = {6: 'Homing Mode', 3: 'Profile Velocity Mode', 1: 'Profile Position Mode',
               -1: 'Position Mode', -2: 'Velocity Mode', -3: 'Current Mode', -4: 'Diagnostic Mode',
               -5: 'MasterEncoder Mode', -6: 'Step/Direction Mode'}
    node = []
    # dictionary object to describe state of EPOS device
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
            bool: A boolean if all went ok.
        '''
        try:
            self.node = self.network.add_node(
                nodeID, object_dictionary=objectDictionary)
            # in not connected?
            if not self.network.bus:
                # so try to connect
                self.network.connect(channel=_channel, bustype=_bustype)
        except Exception as e:
            self.logInfo('Exception caught:{0}'.format(str(e)))
        finally:
            # check if is connected
            if not self.network.bus:
                self._connected = False
            else:
                self._connected = True
            return self._connected

    def disconnect(self):
        self.network.disconnect()
        return
    # --------------------------------------------------------------
    # Basic set of functions
    # --------------------------------------------------------------

    def logInfo(self, message=None):
        ''' Log a message

        A wrap around logging.
        The log message will have the following structure\:
        [class name \: function name ] message

        Args:
            message: a string with the message.
        '''
        if message is None:
            # do nothing
            return
        self.logger.info('[{0}:{1}] {2}'.format(
            self.__class__.__name__,
            sys._getframe(1).f_code.co_name,
            message))
        return

    def logDebug(self, message=None):
        ''' Log a message

        A wrap around logging.
        The log message will have the following structure\:
        [class name \: function name ] message

        the function name will be the caller function retrieved automatically 
        by using sys._getframe(1).f_code.co_name

        Args:
            message: a string with the message.
        '''
        if message is None:
            # do nothing
            return

        self.logger.debug('[{0}:{1}] {2}'.format(
            self.__class__.__name__,
            sys._getframe(1).f_code.co_name,
            message))
        return

    def readObject(self, index, subindex):
        '''Reads an object

         Request a read from dictionary object referenced by index and subindex.

         Args:
             index:     reference of dictionary object index
             subindex:  reference of dictionary object subindex
         Returns:
             bytes:  message returned by EPOS or empty if unsucessfull
        '''
        if self._connected:
            try:
                return self.node.sdo.upload(index, subindex)
            except Exception as e:
                self.logInfo('Exception caught:{0}'.format(str(e)))
                return None
        else:
            self.logInfo(' Error: {0} is not connected'.format(
                self.__class__.__name__))
            return None

    def writeObject(self, index, subindex, data):
        '''Write an object

         Request a write to dictionary object referenced by index and subindex.

         Args:
             index:     reference of dictionary object index
             subindex:  reference of dictionary object subindex
             data:      data to be stored
         Returns:
             bool:      boolean if all went ok or not
        '''
        if self._connected:
            try:
                self.node.sdo.download(index, subindex, data)
                return True
            except canopen.SdoAbortedError as e:
                text = "Code 0x{:08X}".format(e.code)
                if e.code in self.errorIndex:
                    text = text + ", " + self.errorIndex[e.code]
                self.logInfo('SdoAbortedError: ' + text)
                return False
            except canopen.SdoCommunicationError:
                self.logInfo('SdoAbortedError: Timeout or unexpected response')
                return False
        else:
            self.logInfo(' Error: {0} is not connected'.format(
                self.__class__.__name__))
            return False

    ############################################################################
    # High level functions
    ############################################################################

    def readStatusWord(self):
        '''Read StatusWord

        Request current statusword from device.

        Returns:
            tupple: A tupple containing:

            :statusword:  the current statusword or None if any error.
            :Ok: A boolean if all went ok.
        '''
        index = self.objectIndex['StatusWord']
        subindex = 0
        statusword = self.readObject(index, subindex)
        # failded to request?
        if not statusword:
            self.logInfo('Error trying to read {0} statusword'.format(
                self.__class__.__name__))
            return statusword, False

        # return statusword as an int type
        statusword = int.from_bytes(statusword, 'little')
        return statusword, True

    def readControlWord(self):
        '''Read ControlWord

        Request current controlword from device.

        Returns:
            tupple: A tupple containing:

            :controlword: the current controlword or None if any error.
            :Ok: A boolean if all went ok.
        '''
        index = self.objectIndex['ControlWord']
        subindex = 0
        controlword = self.readObject(index, subindex)
        # failded to request?
        if not controlword:
            self.logInfo('Error trying to read {0} controlword'.format(
                self.__class__.__name__))
            return controlword, False

        # return controlword as an int type
        controlword = int.from_bytes(controlword, 'little')
        return controlword, True

    def writeControlWord(self, controlword):
        '''Send controlword to device

        Args:
            controlword: word to be sent.

        Returns:
            bool: a boolean if all went ok.
        '''
        # sending new controlword
        self.logDebug(
            'Sending controlword Hex={0:#06X} Bin={0:#018b}'.format(controlword))
        controlword = controlword.to_bytes(2, 'little')
        return self.writeObject(0x6040, 0, controlword)

    def checkEposState(self):
        '''Check current state of Epos

        Ask the StatusWord of EPOS and parse it to return the current state of EPOS.

        +----------------------------------+-----+---------------------+
        | State                            | ID  | Statusword [binary] |
        +==================================+=====+=====================+
        | Start                            | 0   | x0xx xxx0  x000 0000|
        +----------------------------------+-----+---------------------+
        | Not Ready to Switch On           | 1   | x0xx xxx1  x000 0000|
        +----------------------------------+-----+---------------------+
        | Switch on disabled               | 2   | x0xx xxx1  x100 0000|
        +----------------------------------+-----+---------------------+
        | ready to switch on               | 3   | x0xx xxx1  x010 0001|
        +----------------------------------+-----+---------------------+
        | switched on                      | 4   | x0xx xxx1  x010 0011|
        +----------------------------------+-----+---------------------+
        | refresh                          | 5   | x1xx xxx1  x010 0011|
        +----------------------------------+-----+---------------------+
        | measure init                     | 6   | x1xx xxx1  x011 0011|
        +----------------------------------+-----+---------------------+
        | operation enable                 | 7   | x0xx xxx1  x011 0111|
        +----------------------------------+-----+---------------------+
        | quick stop active                | 8   | x0xx xxx1  x001 0111|
        +----------------------------------+-----+---------------------+
        | fault reaction active (disabled) | 9   | x0xx xxx1  x000 1111|
        +----------------------------------+-----+---------------------+
        | fault reaction active (enabled)  | 10  | x0xx xxx1  x001 1111|
        +----------------------------------+-----+---------------------+
        | Fault                            | 11  | x0xx xxx1  x000 1000|
        +----------------------------------+-----+---------------------+

        see section 8.1.1 of firmware manual for more details.

        Returns:
            int: numeric identification of the state or -1 in case of fail.
        '''
        statusword, ok = self.readStatusWord()
        if not ok:
            self.logInfo('Failed to request StatusWord')
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
        # in case of unknown state or fail
        self.logInfo('Error: Unknown state. Statusword is Bin={0:#018b}'.format(
            int.from_bytes(statusword, 'little'))
        )
        return -1

    def printEposState(self):
        ID = self.checkEposState()
        if ID is -1:
            print('[{0}:{1}] Error: Unknown state\n'.format(
                self.__class__.__name__,
                sys._getframe().f_code.co_name))
        else:
            print('[{0}:{1}] Current state [ID]:{2} [{3}]\n'.format(
                self.__class__.__name__,
                sys._getframe().f_code.co_name,
                self.state[ID],
                ID))
        return

    def printStatusWord(self):
        statusword, Ok = self.readStatusWord()
        if not Ok:
            print('[{0}:{1}] Failed to retreive statusword\n'.format(
                self.__class__.__name__,
                sys._getframe().f_code.co_name))
            return
        else:
            print("[{0}:{1}] The statusword is Hex={2:#06X} Bin={2:#018b}\n".format(
                self.__class__.__name__,
                sys._getframe().f_code.co_name,
                statusword))
            print('Bit 15: position referenced to home position:                  {0}'.format(
                (statusword & (1 << 15)) >> 15))
            print('Bit 14: refresh cycle of power stage:                          {0}'.format(
                (statusword & (1 << 14)) >> 14))
            print('Bit 13: OpMode specific, some error: [Following|Homing]        {0}'.format(
                (statusword & (1 << 13)) >> 13))
            print('Bit 12: OpMode specific: [Set-point ack|Speed|Homing attained] {0}'.format(
                (statusword & (1 << 12)) >> 12))
            print('Bit 11: Internal limit active:                                 {0}'.format(
                (statusword & (1 << 11)) >> 11))
            print('Bit 10: Target reached:                                        {0}'.format(
                (statusword & (1 << 10)) >> 10))
            print('Bit 09: Remote (NMT Slave State Operational):                  {0}'.format(
                (statusword & (1 << 9)) >> 9))
            print('Bit 08: Offset current measured:                               {0}'.format(
                (statusword & (1 << 8)) >> 8))
            print('Bit 07: not used (Warning):                                    {0}'.format(
                (statusword & (1 << 7)) >> 7))
            print('Bit 06: Switch on disable:                                     {0}'.format(
                (statusword & (1 << 6)) >> 6))
            print('Bit 05: Quick stop:                                            {0}'.format(
                (statusword & (1 << 5)) >> 5))
            print('Bit 04: Voltage enabled (power stage on):                      {0}'.format(
                (statusword & (1 << 4)) >> 4))
            print('Bit 03: Fault:                                                 {0}'.format(
                (statusword & (1 << 3)) >> 3))
            print('Bit 02: Operation enable:                                      {0}'.format(
                (statusword & (1 << 2)) >> 2))
            print('Bit 01: Switched on:                                           {0}'.format(
                (statusword & (1 << 1)) >> 1))
            print('Bit 00: Ready to switch on:                                    {0}'.format(
                statusword & 1))
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
                print('[{0}:{1}] Failed to retreive controlword\n'.format(
                    self.__class__.__name__,
                    sys._getframe().f_code.co_name))
                return
        print("[{0}:{1}] The controlword is Hex={2:#06X} Bin={2:#018b}\n".format(
            self.__class__.__name__,
            sys._getframe().f_code.co_name,
            controlword))
        # Bit 15 to 11 not used, 10 to 9 reserved
        print('Bit 08: Halt:                                                                   {0}'.format(
            (controlword & (1 << 8)) >> 8))
        print('Bit 07: Fault reset:                                                            {0}'.format(
            (controlword & (1 << 7)) >> 7))
        print('Bit 06: Operation mode specific:[Abs=0|rel=1]                                   {0}'.format(
            (controlword & (1 << 6)) >> 6))
        print('Bit 05: Operation mode specific:[Change set immediately]                        {0}'.format(
            (controlword & (1 << 5)) >> 5))
        print('Bit 04: Operation mode specific:[New set-point|reserved|Homing operation start] {0}'.format(
            (controlword & (1 << 4)) >> 4))
        print('Bit 03: Enable operation:                                                       {0}'.format(
            (controlword & (1 << 3)) >> 3))
        print('Bit 02: Quick stop:                                                             {0}'.format(
            (controlword & (1 << 2)) >> 2))
        print('Bit 01: Enable voltage:                                                         {0}'.format(
            (controlword & (1 << 1)) >> 1))
        print('Bit 00: Switch on:                                                              {0}'.format(
            controlword & 1))
        return

    def readPositionModeSetting(self):
        '''Reads the setted desired Position

        Ask Epos device for demand position object. If a correct
        request is made, the position is placed in answer. If
        not, an answer will be empty

        Returns:
            tupple: A tupple containing:

            :position: the demanded position value.
            :OK:       A boolean if all requests went ok or not.
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
            bool: A boolean if all requests went ok or not.
        '''
        index = self.objectIndex['PositionMode Setting Value']
        subindex = 0
        if(position < -2**31 or position > 2**31-1):
            print('[Epos:{0}] Postion out of range'.format(
                sys._getframe().f_code.co_name))
            return False
        # change to bytes as an int32 value
        position = position.to_bytes(4, 'little', signed=True)
        return self.writeObject(index, subindex, position)

    def readVelocityModeSetting(self):
        '''Reads the setted desired velocity

        Asks EPOS for the desired velocity value in velocity control mode

        Returns:
            tupple: A tupple containing:

            :velocity: Value setted or None if any error.
            :Ok: A boolean if sucessfull or not.
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
            bool: a boolean if sucessfull or not.
        '''
        index = self.objectIndex['VelocityMode Setting Value']
        subindex = 0
        if(velocity < -2**31 or velocity > 2**31-1):
            print('[Epos:{0}] Velocity out of range'.format(
                sys._getframe().f_code.co_name))
            return False
        # change to bytes as an int32 value
        velocity = velocity.to_bytes(4, 'little', signed=True)
        return self.writeObject(index, subindex, velocity)

    def readCurrentModeSetting(self):
        '''Read current value setted

        Asks EPOS for the current value setted in current control mode.

        Returns:
            tupple: A tupple containing:

            :current: value setted.
            :Ok:      a boolean if sucessfull or not.
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
        '''Set desired current

        Set the value for desired current in current control mode

        Args:
            current: the value to be set [mA]
        Returns:
            bool: a boolean if sucessfull or not
        '''
        index = self.objectIndex['CurrentMode Setting Value']
        subindex = 0
        if(current < -2**15 or current > 2**15-1):
            print('[Epos:{0}] Current out of range'.format(
                sys._getframe().f_code.co_name))
            return False
        # change to bytes as an int16 value
        current = current.to_bytes(2, 'little', signed=True)
        return self.writeObject(index, subindex, current)

    def readOpMode(self):
        '''Read current operation mode

        Returns:
            tupple: A tupple containing:

            :opMode: current opMode or None if request fails
            :Ok:     A boolean if sucessfull or not
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
        opMode = int.from_bytes(opMode, 'little', signed=True)
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
            bool:     A boolean if all requests went ok or not.
        '''
        index = self.objectIndex['Modes of Operation']
        subindex = 0
        if not opMode in self.opModes:
            logging.info('[EPOS:{0}] Unkown Operation Mode: {1}'.format(
                sys._getframe().f_code.co_name, opMode))
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
        if not (opMode in self.opModes):
            logging.info('[EPOS:{0}] Unkown Operation Mode: {1}'.format(
                sys._getframe().f_code.co_name, opMode))
            return
        else:
            print('Current operation mode is \"{}\"'.format(
                self.opModes[opMode]))
        return

    def changeEposState(self, newState):
        '''Change EPOS state

        Change Epos state using controlWord object

        To change Epos state, a write to controlWord object is made.
        The bit change in controlWord is made as shown in the following table:

        +-------------------+--------------------------------+
        | State             | LowByte of Controlword [binary]|
        +===================+================================+
        | shutdown          | 0xxx x110                      |
        +-------------------+--------------------------------+
        | switch on         | 0xxx x111                      |
        +-------------------+--------------------------------+
        | disable voltage   | 0xxx xx0x                      |
        +-------------------+--------------------------------+
        | quick stop        | 0xxx x01x                      |
        +-------------------+--------------------------------+
        | disable operation | 0xxx 0111                      |
        +-------------------+--------------------------------+
        | enable operation  | 0xxx 1111                      |
        +-------------------+--------------------------------+
        | fault reset       | 1xxx xxxx                      |
        +-------------------+--------------------------------+

        see section 8.1.3 of firmware for more information

        Args:
            newState: string with state witch user want to switch.

        Returns:
            bool: boolean if all went ok and no error was received.
        '''
        stateOrder = ['shutdown', 'switch on', 'disable voltage', 'quick stop',
                      'disable operation', 'enable operation', 'fault reset']

        if not (newState in stateOrder):
            logging.info('[EPOS:{0}] Unkown state: {1}'.format(
                sys._getframe().f_code.co_name, newState))
            return False
        else:
            controlword, Ok = self.readControlWord()
            if not Ok:
                logging.info('[EPOS:{0}] Failed to retreive controlword'.format(
                    sys._getframe().f_code.co_name))
                return False
            # shutdown  0xxx x110
            if newState == 'shutdown':
                # clear bits
                mask = not (1 << 7 | 1 << 0)
                controlword = controlword & mask
                # set bits
                mask = (1 << 2 | 1 << 1)
                controlword = controlword | mask
                return self.writeControlWord(controlword)
            # switch on 0xxx x111
            if newState == 'switch on':
                # clear bits
                mask = not (1 << 7)
                controlword = controlword & mask
                # set bits
                mask = (1 << 2 | 1 << 1 | 1 << 0)
                controlword = controlword | mask
                return self.writeControlWord(controlword)
            # disable voltage 0xxx xx0x
            if newState == 'switch on':
                # clear bits
                mask = not (1 << 7 | 1 << 1)
                controlword = controlword & mask
                return self.writeControlWord(controlword)
            # quick stop 0xxx x01x
            if newState == 'quick stop':
                # clear bits
                mask = not (1 << 7 | 1 << 2)
                controlword = controlword & mask
                # set bits
                mask = (1 << 1)
                controlword = controlword | mask
                return self.writeControlWord(controlword)
            # disable operation 0xxx 0111
            if newState == 'disable operation':
                # clear bits
                mask = not (1 << 7 | 1 << 3)
                controlword = controlword & mask
                # set bits
                mask = (1 << 2 | 1 << 1 | 1 << 0)
                controlword = controlword | mask
                return self.writeControlWord(controlword)
            # enable operation 0xxx 1111
            if newState == 'enable operation':
                # clear bits
                mask = not (1 << 7)
                controlword = controlword & mask
                # set bits
                mask = (1 << 3 | 1 << 2 | 1 << 1 | 1 << 0)
                controlword = controlword | mask
                return self.writeControlWord(controlword)
            # fault reset 1xxx xxxx
            if newState == 'fault reset':
                # set bits
                mask = (1 << 7)
                controlword = controlword | mask
                return self.writeControlWord(controlword)

    def setMotorConfig(self, motorType, currentLimit, maximumSpeed, polePairNumber):
        '''Set motor configuration

        Sets the configuration of the motor parameters. The valid motor type is:

        +-------------------------+-------+---------------------------+
        | motorType               | value | Description               |
        +=========================+=======+===========================+
        | DC motor                | 1     | brushed DC motor          |
        +-------------------------+-------+---------------------------+
        | Sinusoidal PM BL motor  | 10    | EC motor sinus commutated |
        +-------------------------+-------+---------------------------+
        | Trapezoidal PM BL motor | 11    | EC motor block commutated |
        +-------------------------+-------+---------------------------+

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
            bool:     A boolean if all requests went ok or not.
        '''
        # ------------------------------------------------------------------------
        # check values of input
        # ------------------------------------------------------------------------
        if not ((motorType in self.motorType) or (motorType in self.motorType.values())):
            logging.info('[EPOS:{0}] Unknow motorType: {1} '.format(
                sys._getframe().f_code.co_name, motorType))
            return False
        if (currentLimit < 0) or (currentLimit > 2**16 - 1):
            logging.info('[EPOS:{0}] Current limit out of range: {1} '.format(
                sys._getframe().f_code.co_name, currentLimit))
            return False
        if (polePairNumber < 0) or (polePairNumber > 255):
            logging.info('[EPOS:{0}] Pole pair number out of range: {1} '.format(
                sys._getframe().f_code.co_name, polePairNumber))
            return False
        if (maximumSpeed < 1) or (maximumSpeed > 2**16 - 1):
            logging.info('[EPOS:{0}] Maximum speed out of range: {1} '.format(
                sys._getframe().f_code.co_name, maximumSpeed))
            return False
        # ------------------------------------------------------------------------
        # store motorType
        # ------------------------------------------------------------------------
        index = self.objectIndex['MotorType']
        subindex = 0
        if motorType in self.motorType:
            motorType = self.motorType[motorType]
        Ok = self.writeObject(index, subindex, motorType.to_bytes(1, 'little'))
        if not Ok:
            logging.info('[EPOS:{0}] Failed to set motorType'.format(
                sys._getframe().f_code.co_name))
            return Ok
        # ------------------------------------------------------------------------
        # store motorData
        # ------------------------------------------------------------------------
        index = self.objectIndex['Motor Data']
        # check if it was passed a float
        if isinstance(currentLimit, float):
            # if true trunc to closes int, similar to floor
            currentLimit = currentLimit.__trunc__
        # constant current limit has subindex 1
        Ok = self.writeObject(index, 1, currentLimit.to_bytes(2, 'little'))
        if not Ok:
            logging.info('[EPOS:{0}] Failed to set currentLimit'.format(
                sys._getframe().f_code.co_name))
            return Ok
        # output current limit has subindex 2 and is recommended to
        # be the double of constant current limit
        Ok = self.writeObject(
            index, 2, (currentLimit * 2).to_bytes(2, 'little'))
        if not Ok:
            logging.info('[EPOS:{0}] Failed to set output current limit'.format(
                sys._getframe().f_code.co_name))
            return Ok
        # pole pair number has subindex 3
        Ok = self.writeObject(index, 3, polePairNumber.to_bytes(1, 'little'))
        if not Ok:
            logging.info('[EPOS:{0}] Failed to set pole pair number: {1}'.format(
                sys._getframe().f_code.co_name, polePairNumber))
            return Ok
        # maxSpeed has subindex 4
        # check if it was passed a float
        if isinstance(maximumSpeed, float):
            # if true trunc to closes int, similar to floor
            maximumSpeed = maximumSpeed.__trunc__
        Ok = self.writeObject(index, 4, maximumSpeed.to_bytes(2, 'little'))
        if not Ok:
            logging.info('[EPOS:{0}] Failed to set maximum speed: {1}'.format(
                sys._getframe().f_code.co_name, maximumSpeed))
            return Ok
        # no fails, return True
        return True

    def readMotorConfig(self):
        '''Read motor configuration

        Read the current motor configuration

        Requests from EPOS the current motor type and motor data.
        The motorConfig is a dictionary containing the following information:

        * **motorType** describes the type of motor.
        * **currentLimit** - describes the maximum continuous current limit.
        * **maxCurrentLimit** - describes the maximum allowed current limit.
          Usually is set as two times the continuous current limit.
        * **polePairNumber** - describes the pole pair number of the rotor of
          the brushless DC motor.
        * **maximumSpeed** - describes the maximum allowed speed in current mode.
        * **thermalTimeConstant** - describes the thermal time constant of motor
          winding is used to calculate the time how long the maximal output
          current is allowed for the connected motor [100 ms].

        If unable to request the configuration or unsucessfull, None and false is
        returned .

        Returns:
            tupple: A tupple with:

            :motorConfig: A structure with the current configuration of motor
            :OK:          A boolean if all went as expected or not.
        '''
        motorConfig = {}  # dictionary to store config
        # ------------------------------------------------------------------------
        # store motorType
        # ------------------------------------------------------------------------
        index = self.objectIndex['MotorType']
        subindex = 0
        value = self.readObject(index, subindex)
        if value is None:
            logging.info('[EPOS:{0}] Failed to get motorType'.format(
                sys._getframe().f_code.co_name))
            return None, False
        # append motorType to dict
        motorConfig.update({'motorType': int.from_bytes(value, 'little')})
        # ------------------------------------------------------------------------
        # store motorData
        # ------------------------------------------------------------------------
        index = self.objectIndex['Motor Data']
        value = self.readObject(index, 1)
        if value is None:
            logging.info('[EPOS:{0}] Failed to get currentLimit'.format(
                sys._getframe().f_code.co_name))
            return None, False
        motorConfig.update({'currentLimit': int.from_bytes(value, 'little')})
        # output current limit has subindex 2 and is recommended to
        # be the double of constant current limit
        value = self.readObject(index, 2)
        if value is None:
            logging.info('[EPOS:{0}] Failed to get maxCurrentLimit'.format(
                sys._getframe().f_code.co_name))
            return None, False
        motorConfig.update(
            {'maxCurrentLimit': int.from_bytes(value, 'little')})
        # pole pair number has subindex 3
        value = self.readObject(index, 3)
        if value is None:
            logging.info('[EPOS:{0}] Failed to get polePairNumber'.format(
                sys._getframe().f_code.co_name))
            return None, False
        motorConfig.update({'polePairNumber': int.from_bytes(value, 'little')})
        # maxSpeed has subindex 4
        value = self.readObject(index, 4)
        if value is None:
            logging.info('[EPOS:{0}] Failed to get maximumSpeed'.format(
                sys._getframe().f_code.co_name))
            return None, False
        motorConfig.update({'maximumSpeed': int.from_bytes(value, 'little')})
        # thermal time constant has index 5
        value = self.readObject(index, 5)
        if value is None:
            logging.info('[EPOS:{0}] Failed to get thermalTimeConstant'.format(
                sys._getframe().f_code.co_name))
            return None, False
        motorConfig.update(
            {'thermalTimeConstant': int.from_bytes(value, 'little')})
        # no fails, return dict and ok
        return motorConfig, True

    def printMotorConfig(self):
        '''Print current motor config

        Request current motor config and print it
        '''
        motorConfig, Ok = self.readMotorConfig()
        for key, value in self.motorType.items():    # dict.items():  (for Python 3.x)
            if value == motorConfig['motorType']:
                break

        if not Ok:
            print('[EPOS:{0}] Failed to request current motor configuration'.format(
                sys._getframe().f_code.co_name))
            return
        print('--------------------------------------------------------------')
        print('Current motor configuration:')
        print('--------------------------------------------------------------')
        print('Motor Type is {0}'.format(key))
        print('Motor constant current limit {0}[mA]'.format(
            motorConfig['currentLimit']))
        print('Motor maximum current limit {0}[mA]'.format(
            motorConfig['maxCurrentLimit']))
        print('Motor maximum speed in current mode {0}[rpm]'.format(
            motorConfig['maximumSpeed']))
        print('Motor number of pole pairs {0}'.format(
            motorConfig['polePairNumber']))
        print('Motor thermal time constant {0}[s]'.format(
            motorConfig['currentLimit']/10.0))
        print('--------------------------------------------------------------')
        return

    def setSensorConfig(self, pulseNumber, sensorType, sensorPolarity):
        '''Change sensor configuration

        Change the sensor configuration of motor. **Only possible if in disable state**
        The encoder pulse number should be set to number of counts per
        revolution of the connected incremental encoder.
        range : [16 - 7500]

        sensor type is described as:

        +-------+--------------------------------------------------+
        | value | description                                      |
        +=======+==================================================+
        | 1     | Incremental Encoder with index (3-channel)       |
        +-------+--------------------------------------------------+
        | 2     | Incremental Encoder without index (2-channel)    |
        +-------+--------------------------------------------------+
        | 3     | Hall Sensors (Remark: consider worse resolution) |
        +-------+--------------------------------------------------+

        sensor polarity is set by setting the corresponding bit from the word:

        +------+--------------------------------------------------------+
        | Bit  | description                                            |
        +======+========================================================+
        | 15-2 | Reserved (0)                                           |
        +------+--------------------------------------------------------+
        | 1    | Hall sensors polarity 0: normal / 1: inverted          |
        +------+--------------------------------------------------------+
        | 0    | | Encoder polarity 0: normal                           |
        |      | | 1: inverted (or encoder mounted on motor shaft side) |
        +------+--------------------------------------------------------+

        Args:
            pulseNumber:    Number of pulses per revolution.
            sensorType:     1,2 or 3 according to the previous table.
            sensorPolarity: a value between 0 and 3 describing the polarity
                              of sensors as stated before.
        Returns:
            bool: A boolean if all went as expected or not.
        '''
        # validate attributes first
        if(pulseNumber < 16 or pulseNumber > 7500):
            logging.info('[Epos:{0}] Error pulseNumber out of range: {1}'.format(
                sys._getframe().f_code.co_name,
                pulseNumber))
            return False
        if not (sensorType in [1, 2, 3]):
            logging.info('[Epos:{0}] Error sensorType not valid: {1}'.format(
                sys._getframe().f_code.co_name,
                sensorType))
            return False
        if not (sensorPolarity in [0, 1, 2, 3]):
            logging.info('[Epos:{0}] Error sensorPolarity not valid: {1}'.format(
                sys._getframe().f_code.co_name,
                sensorPolarity))
            return False
        # change epos state first to shutdown state
        # or it will fail
        Ok = self.changeEposState('shutdown')
        if not Ok:
            logging.info('[Epos:{0}] Error failed to change EPOS state into shutdown'.format(
                sys._getframe().f_code.co_name))
            return False
        # get index
        index = self.objectIndex['Sensor Configuration']
        # pulseNumber has subindex 1
        Ok = self.writeObject(index, 1, pulseNumber.to_bytes(2, 'little'))
        if not Ok:
            logging.info('[Epos:{0}] Error setting pulseNumber'.format(
                sys._getframe().f_code.co_name))
            return False
        # sensorType has subindex 2
        Ok = self.writeObject(index, 2, sensorType.to_bytes(2, 'little'))
        if not Ok:
            logging.info('[Epos:{0}] Error setting sensorType'.format(
                sys._getframe().f_code.co_name))
            return False
        # sensorPolarity has subindex 4
        Ok = self.writeObject(index, 4, sensorPolarity.to_bytes(2, 'little'))
        if not Ok:
            logging.info('[Epos:{0}] Error setting sensorPolarity'.format(
                sys._getframe().f_code.co_name))
            return False
        return True

    def readSensorConfig(self):
        '''Read sensor configuration

        Requests from EPOS the current sensor configuration.
        The sensorConfig is an struture containing the following information:

        * sensorType - describes the type of sensor.
        * pulseNumber - describes the number of pulses per revolution in one channel.
        * sensorPolarity - describes the of each sensor.

        If unable to request the configuration or unsucessfull, an empty
        structure is returned. Any error inside any field requests are marked
        with 'error'.

        Returns:
            tupple: A tupple containing:

            :sensorConfig: A dictionary with the current configuration of the sensor
            :OK: A boolean if all went as expected or not.
        '''
        sensorConfig = {}
        # get index
        index = self.objectIndex['Sensor Configuration']
        # pulseNumber has subindex 1
        value = self.readObject(index, 1)
        if value is None:
            logging.info('[Epos:{0}] Error getting pulseNumber'.format(
                sys._getframe().f_code.co_name))
            return None, False
        sensorConfig.update({'pulseNumber': int.from_bytes(value, 'little')})
        # sensorType has subindex 2
        value = self.readObject(index, 2)
        if value is None:
            logging.info('[Epos:{0}] Error getting sensorType'.format(
                sys._getframe().f_code.co_name))
            return None, False
        sensorConfig.update({'sensorType': int.from_bytes(value, 'little')})
        # sensorPolarity has subindex 4
        value = self.readObject(index, 4)
        if value is None:
            logging.info('[Epos:{0}] Error getting sensorPolarity'.format(
                sys._getframe().f_code.co_name))
            return None, False
        sensorConfig.update(
            {'sensorPolarity': int.from_bytes(value, 'little')})
        return sensorConfig, True

    def printSensorConfig(self):
        '''Print current sensor configuration
        '''
        sensorConfig, Ok = self.readSensorConfig()
        # to adjust indexes ignore use a dummy first element
        sensorType = ['', 'Incremental Encoder with index (3-channel)',
                      'Incremental Encoder without index (2-channel)',
                      'Hall Sensors (Remark: consider worse resolution)']
        if not Ok:
            print('[EPOS:{0}] Failed to request current sensor configuration'.format(
                sys._getframe().f_code.co_name))
            return
        print('--------------------------------------------------------------')
        print('Current sensor configuration:')
        print('--------------------------------------------------------------')
        print('Sensor pulse Number is {0}'.format(sensorConfig['pulseNumber']))
        print('Sensor type is {0}'.format(
            sensorType[sensorConfig['sensorType']]))
        value = sensorConfig['sensorPolarity']
        if (value & 1 << 1) >> 1:
            print('Hall sensor polarity inverted')
        else:
            print('Hall sensor polarity normal')
        if (value & 1):
            print('Encoder polarity inverted')
        else:
            print('Encoder polarity normal')
        print('--------------------------------------------------------------')
        return

    def setCurrentControlParameters(self, pGain, iGain):
        '''Set the PI gains used in current control mode

        Args:
            pGain: Proportional gain.
            iGain: Integral gain.
        Returns:
            bool: A boolean if all went as expected or not.
        '''
        # any float?
        if (isinstance(pGain, float) or isinstance(iGain, float)):
            logging.info('[Epos:{0}] Error all values must be int, not floats'.format(
                sys._getframe().f_code.co_name))
            return False
        # any out of range?
        # validate attributes first
        if(pGain < 0 or pGain > 2**15-1):
            logging.info('[Epos:{0}] Error pGain out of range: {1}'.format(
                sys._getframe().f_code.co_name,
                pGain))
            return False
        if(iGain < 0 or iGain > 2**15-1):
            logging.info('[Epos:{0}] Error iGain out of range: {1}'.format(
                sys._getframe().f_code.co_name,
                iGain))
            return False
        # all ok. Proceed
        index = self.objectIndex['Current Control Parameter']
        # pGain has subindex 1
        Ok = self.writeObject(
            index, 1, pGain.to_bytes(2, 'little', signed=True))
        if not Ok:
            logging.info('[Epos:{0}] Error setting pGain'.format(
                sys._getframe().f_code.co_name))
            return False
        # iGain has subindex 2
        Ok = self.writeObject(
            index, 2, iGain.to_bytes(2, 'little', signed=True))
        if not Ok:
            logging.info('[Epos:{0}] Error setting iGain'.format(
                sys._getframe().f_code.co_name))
            return False
        # all ok, return True
        return True

    def readCurrentControlParameters(self):
        '''Read the PI gains used in  current control mode

        Returns:
            tupple: A tupple containing:

            :gains: A dictionary with the current pGain and iGain
            :OK: A boolean if all went as expected or not.
        '''
        index = self.objectIndex['Current Control Parameter']
        currModeParameters = {}
        # pGain has subindex 1
        value = self.readObject(index, 1)
        if value is None:
            logging.info('[Epos:{0}] Error getting pGain'.format(
                sys._getframe().f_code.co_name))
            return None, False
        # can not be less than zero, but is considered signed!
        currModeParameters.update(
            {'pGain': int.from_bytes(value, 'little', signed=True)})

        # iGain has subindex 2
        value = self.readObject(index, 2)
        if value is None:
            logging.info('[Epos:{0}] Error getting iGain'.format(
                sys._getframe().f_code.co_name))
            return None, False
        currModeParameters.update(
            {'iGain': int.from_bytes(value, 'little', signed=True)})
        return currModeParameters, True

    def printCurrentControlParameters(self):
        '''Print the current mode control PI gains

        Request current mode control parameter gains from device and print.
        '''
        currModeParameters, ok = self.readCurrentControlParameters()
        if not ok:
            print('[Epos:{0}] Error requesting Position mode control parameters'.format(
                sys._getframe().f_code.co_name))
            return
        print('--------------------------------------------------------------')
        print('Current Position mode control parameters:')
        print('--------------------------------------------------------------')
        for key, value in currModeParameters.items():
            print('{0}: {1}'.format(key, value))
        print('--------------------------------------------------------------')

    def setSoftwarePosLimit(self, minPos, maxPos):
        '''Set the software position limits

        Use encoder readings as limit position for extremes
        range = [-2147483648 | 2147483647]

        Args:
            minPos: minimum possition limit
            maxPos: maximum possition limit
        Return:
            bool: A boolean if all went as expected or not.
        '''
        # validate attributes
        if not (isinstance(minPos, int) and isinstance(maxPos, int)):
            logging.info('[Epos:{0}] Error input values must be int'.format(
                sys._getframe().f_code.co_name))
            return False
        if (minPos < -2**31 or minPos > 2**31-1):
            logging.info('[Epos:{0}] Error minPos out of range'.format(
                sys._getframe().f_code.co_name))
            return False
        if (maxPos < -2**31 or maxPos > 2**31-1):
            logging.info('[Epos:{0}] Error maxPos out of range'.format(
                sys._getframe().f_code.co_name))
            return False
        index = self.objectIndex['Software Position Limit']
        # minPos has subindex 1
        ok = self.writeObject(index, 0x1, minPos.to_bytes(4, 'little'))
        if not ok:
            logging.info('[Epos:{0}] Error setting minPos'.format(
                sys._getframe().f_code.co_name))
            return False
        # maxPos has subindex 2
        ok = self.writeObject(index, 0x2, maxPos.to_bytes(4, 'little'))
        if not ok:
            logging.info('[Epos:{0}] Error setting maxPos'.format(
                sys._getframe().f_code.co_name))
            return False
        return True

    def readSoftwarePosLimit(self):
        '''Read the software position limit

        Return:
            tupple: A tupple containing:

            :limits: a dictionary containing minPos and maxPos
            :OK: A boolean if all went as expected or not.
        '''
        limits = {}
        index = self.objectIndex['Software Position Limit']
        # min has subindex 1
        value = self.readObject(index, 0x1)
        if value is None:
            logging.info('[Epos:{0}] Failed to read min position'.format(
                sys._getframe().f_code.co_name))
            return None, False
        limits.update({'minPos': int.from_bytes(value, 'little')})
        # max has subindex 2
        value = self.readObject(index, 0x2)
        if value is None:
            logging.info('[Epos:{0}] Failed to read max position'.format(
                sys._getframe().f_code.co_name))
            return None, False
        limits.update({'maxPos': int.from_bytes(value, 'little')})
        return limits, True

    def printSoftwarePosLimit(self):
        ''' Print current software position limits
        '''
        limits, ok = self.readSoftwarePosLimit()
        if not ok:
            print('[Epos:{0}] Failed to request software position limits'.format(
                sys._getframe().f_code.co_name))
            return
        print('--------------------------------------------------------------')
        print('Software Position limits:')
        print('--------------------------------------------------------------')
        print('Minimum [qc]: {0}'.format(limits['minPos']))
        print('Maximum [qc]: {0}'.format(limits['maxPos']))
        print('--------------------------------------------------------------')

    def setQuickStopDeceleration(self, quickstopDeceleration):
        '''Set the quick stop deceleration.

        The quick stop deceleration defines the deceleration
        during a fault reaction.

        Args:
            quicstopDeceleration: the value of deceleration in rpm/s
        Return:
            bool: A boolean if all went as expected or not.
        '''
        # validate attributes
        if not isinstance(quickstopDeceleration, int):
            logging.info('[Epos:{0}] Error input value must be int'.format(
                sys._getframe().f_code.co_name))
            return False
        if (quickstopDeceleration < 1 or quickstopDeceleration > 2**32-1):
            logging.info('[Epos:{0}] Error quick stop deceleration out of range'.format(
                sys._getframe().f_code.co_name))
            return False
        index = self.objectIndex['QuickStop Deceleration']
        ok = self.writeObject(
            index, 0x0, quickstopDeceleration.to_bytes(4, 'little'))
        if not ok:
            logging.info('[Epos:{0}] Error setting quick stop deceleration'.format(
                sys._getframe().f_code.co_name))
            return False
        return True

    def readQuickStopDeceleration(self):
        ''' Read the quick stop deceleration.

        Read deceleration used in fault reaction state.

        Returns:
            tupple: A tupple containing:

            :quickstopDeceleration: The value of deceleration in rpm/s.
            :OK: A boolean if all went as expected or not.
        '''
        index = self.objectIndex['QuickStop Deceleration']
        deceleration = self.readObject(index, 0x0)
        if deceleration is None:
            logging.info('[Epos:{0}] Failed to read quick stop deceleration value'.format(
                sys._getframe().f_code.co_name))
            return None, False
        deceleration = int.from_bytes(deceleration, 'little')
        return deceleration, True

    def readPositionControlParameters(self):
        ''' Read position mode control parameters

        Read position mode control PID gains and and feedfoward
        and acceleration values

        Returns:
            tupple: A tupple containing:

            :posModeParameters: a dictionary containg pGain,
                iGain, dGain, vFeed and aFeed.
            :OK: A boolean if all went as expected or not.
        '''
        index = self.objectIndex['Position Control Parameter']
        posModeParameters = {}
        # pGain has subindex 1
        value = self.readObject(index, 1)
        if value is None:
            logging.info('[Epos:{0}] Error getting pGain'.format(
                sys._getframe().f_code.co_name))
            return None, False
        # can not be less than zero, but is considered signed!
        posModeParameters.update(
            {'pGain': int.from_bytes(value, 'little', signed=True)})

        # iGain has subindex 2
        value = self.readObject(index, 2)
        if value is None:
            logging.info('[Epos:{0}] Error getting iGain'.format(
                sys._getframe().f_code.co_name))
            return None, False
        posModeParameters.update(
            {'iGain': int.from_bytes(value, 'little', signed=True)})

        # dGain has subindex 3
        value = self.readObject(index, 3)
        if value is None:
            logging.info('[Epos:{0}] Error getting dGain'.format(
                sys._getframe().f_code.co_name))
            return None, False
        posModeParameters.update(
            {'dGain': int.from_bytes(value, 'little', signed=True)})

        # vFeedFoward has subindex 4
        value = self.readObject(index, 4)
        if value is None:
            logging.info('[Epos:{0}] Error getting vFeed'.format(
                sys._getframe().f_code.co_name))
            return None, False
        # these are not considered signed!
        posModeParameters.update({'vFeed': int.from_bytes(value, 'little')})

        # aFeedFoward has subindex 5
        value = self.readObject(index, 5)
        if value is None:
            logging.info('[Epos:{0}] Error getting aFeed'.format(
                sys._getframe().f_code.co_name))
            return None, False
        posModeParameters.update({'aFeed': int.from_bytes(value, 'little')})
        return posModeParameters, True

    def setPositionControlParameters(self, pGain, iGain, dGain, vFeed=0, aFeed=0):
        '''Set position mode control parameters

        Set position control PID gains and feedfoward velocity and
        acceleration values.

        **Feedback and Feed Forward**

        *PID feedback amplification*

        PID stands for Proportional, Integral and Derivative control parameters.
        They describe how the error signal e is amplified in order to
        produce an appropriate correction. The goal is to reduce this error, i.e.
        the deviation between the set (or demand) value and the measured (or
        actual) value. Low values of control parameters will usually result in a
        sluggish control behavior. High values will lead to a stiffer control with the
        risk of overshoot and at too high an amplification, the system may start
        oscillating.

        *Feed-forward*

        With the PID algorithms, corrective action only occurs if there is
        a deviation between the set and actual values. For positioning
        systems, this means that there always is â€“ in fact, there has to
        be a position error while in motion. This is called following
        error. The objective of the feedforward control is to minimize
        this following error by taking into account the set value changes
        in advance. Energy is provided in an open-loop controller set-up
        to compensate friction and for the purpose of mass inertia acceleration.
        Generally, there are two parameters available in feed-forward.
        They have to be determined for the specific application and motion
        task\:

        * Speed feed-forward gain: This component is multiplied by the
          demanded speed and compensates for speed-proportional friction.
        * Acceleration feed-forward correction\: This component is related
          to the mass inertia of the system and provides sufficient current
          to accelerate this inertia.

        Incorporating the feed forward features reduces the average following
        error when accelerating and decelerating. By combining a feed-forward
        control and PID, the PID controller only has to correct the
        residual error remaining after feed-forward, thereby improving the
        system response and allowing very stiff control behavior.

        According to `Position Regulation with Feed Forward\
        <https://www.maxonmotor.com/medias/sys_master/root/8803614294046/\
        EPOS-Application-Note-Position-Regulation-with-Feed-Forward-En.pdf>`_
        the acceleration and velocity feed forward take effect in Profile
        Position Mode and Homing Mode. There is no influence to all the other
        operation modes like Position Mode, Profile Velocity Mode, Velocity Mode
        and Current Mode

        Args:
            pGain: Proportional gain value
            iGain: Integral gain value
            dGain: Derivative gain value
            vFeed: velocity feed foward gain value. Default to 0
            aFeed: acceleration feed foward gain value. Default to 0
        Returns:
            OK: A boolean if all requests went ok or not
        '''
        # validate attributes first
        # any float?
        if (isinstance(pGain, float) or isinstance(iGain, float) or
            isinstance(dGain, float) or isinstance(vFeed, float) or
                isinstance(aFeed, float)):
            logging.info('[Epos:{0}] Error all values must be int, not floats'.format(
                sys._getframe().f_code.co_name))
            return False
        # any out of range?
        if(pGain < 0 or pGain > 2**15-1):
            logging.info('[Epos:{0}] Error pGain out of range: {1}'.format(
                sys._getframe().f_code.co_name,
                pGain))
            return False
        if (iGain < 0 or iGain > 2**15-1):
            logging.info('[Epos:{0}] Error iGain out of range: {1}'.format(
                sys._getframe().f_code.co_name,
                iGain))
            return False
        if (dGain < 0 or dGain > 2**15-1):
            logging.info('[Epos:{0}] Error dGain out of range: {1}'.format(
                sys._getframe().f_code.co_name,
                dGain))
            return False
        if (iGain < 0 or iGain > 2**15-1):
            logging.info('[Epos:{0}] Error iGain out of range: {1}'.format(
                sys._getframe().f_code.co_name,
                pGain))
            return False
        if (vFeed < 0 or vFeed > 2**16-1):
            logging.info('[Epos:{0}] Error vFeed out of range: {1}'.format(
                sys._getframe().f_code.co_name,
                vFeed))
            return False
        if (aFeed < 0 or aFeed > 2**16-1):
            logging.info('[Epos:{0}] Error aFeed out of range: {1}'.format(
                sys._getframe().f_code.co_name,
                aFeed))
            return False
        # all ok. Proceed
        index = self.objectIndex['Position Control Parameter']
        # pGain has subindex 1
        Ok = self.writeObject(
            index, 1, pGain.to_bytes(2, 'little', signed=True))
        if not Ok:
            logging.info('[Epos:{0}] Error setting pGain'.format(
                sys._getframe().f_code.co_name))
            return False
        # iGain has subindex 2
        Ok = self.writeObject(
            index, 2, iGain.to_bytes(2, 'little', signed=True))
        if not Ok:
            logging.info('[Epos:{0}] Error setting iGain'.format(
                sys._getframe().f_code.co_name))
            return False
        # dGain has subindex 3
        Ok = self.writeObject(
            index, 3, dGain.to_bytes(2, 'little', signed=True))
        if not Ok:
            logging.info('[Epos:{0}] Error setting dGain'.format(
                sys._getframe().f_code.co_name))
            return False
        # vFeed has subindex 4
        Ok = self.writeObject(index, 4, vFeed.to_bytes(2, 'little'))
        if not Ok:
            logging.info('[Epos:{0}] Error setting vFeed'.format(
                sys._getframe().f_code.co_name))
            return False
        # aFeed has subindex 5
        Ok = self.writeObject(index, 5, aFeed.to_bytes(2, 'little'))
        if not Ok:
            logging.info('[Epos:{0}] Error setting aFeed'.format(
                sys._getframe().f_code.co_name))
            return False
        # all ok, return True
        return True

    def printPositionControlParameters(self):
        '''Print position control mode parameters

        Request device for the position control mode parameters
        and prints it.
        '''
        posModeParameters, ok = self.readPositionControlParameters()
        if not ok:
            print('[Epos:{0}] Error requesting Position mode control parameters'.format(
                sys._getframe().f_code.co_name))
            return
        print('--------------------------------------------------------------')
        print('Current Position mode control parameters:')
        print('--------------------------------------------------------------')
        for key, value in posModeParameters.items():
            print('{0}: {1}'.format(key, value))
        print('--------------------------------------------------------------')

    def readFollowingError(self):
        '''Returns the current following error

        Read the current following error value which is the difference
        between atual value and desired value.

        Returns:
            tupple: a tupple containing:

            :followingError: value of actual following error.
            :OK: A boolean if all requests went ok or not.
        '''
        index = self.objectIndex['Following Error Actual Value']
        followingError = self.readObject(index, 0x0)
        if not followingError:
            logging.info('[Epos:{0}] Error getting Following Error Actual Value'.format(
                sys._getframe().f_code.co_name))
            return None, False
        followingError = int.from_bytes(followingError, 'little', signed=True)
        return followingError, True

    def readMaxFollowingError(self):
        '''Read the Max following error

        Read the max following error value which is the maximum allowed difference
        between atual value and desired value in modulus.

        Returns:
            tupple: a tupple containing:

            :maxFollowingError: value of max following error.
            :OK: A boolean if all requests went ok or not.
        '''
        index = self.objectIndex['Max Following Error']
        maxFollowingError = self.readObject(index, 0x0)
        if not maxFollowingError:
            logging.info('[Epos:{0}] Error getting Max Following Error Value'.format(
                sys._getframe().f_code.co_name))
            return None, False
        maxFollowingError = int.from_bytes(maxFollowingError, 'little')
        return maxFollowingError, True

    def setMaxFollowingError(self, maxFollowingError):
        '''Set the Max following error

        The Max Following Error is the maximum permissible difference
        between demanded and actual position at any time of evaluation.
        It serves as a safety and motion-supervising feature.
        If the following error becomes too high, this is a sign of something
        going wrong. Either the drive cannot reach the required speed
        or it is even blocked.

        Args:
            maxFollowingError: The value of maximum following error.
        Returns:
            bool: A boolean if all requests went ok or not.
        '''
        # validate attributes
        if not isinstance(maxFollowingError, int):
            logging.info('[Epos:{0}] Error input value must be int'.format(
                sys._getframe().f_code.co_name))
            return False
        if (maxFollowingError < 0 or maxFollowingError > 2**32-1):
            logging.info('[Epos:{0}] Error Max Following error out of range'.format(
                sys._getframe().f_code.co_name))
            return False

        index = self.objectIndex['Max Following Error']
        ok = self.writeObject(
            index, 0x0, maxFollowingError.to_bytes(4, 'little'))
        if not ok:
            logging.info('[Epos:{0}] Error setting Max Following Error Value'.format(
                sys._getframe().f_code.co_name))
            return False
        return True

    def readPositionValue(self):
        '''Read current position value

        Returns:
            tupple: a tupple containing:

            :position: current position in quadrature counts.
            :Ok: A boolean if all requests went ok or not.
        '''
        index = self.objectIndex['Position Actual Value']
        position = self.readObject(index, 0x0)
        if position is None:
            logging.info('[Epos:{0}] Failed to read current position value'.format(
                sys._getframe().f_code.co_name))
            return None, False
        position = int.from_bytes(position, 'little', signed=True)
        return position, True

    def readPositionWindow(self):
        '''Read current position Window value.

        Position window is the modulus threashold value in which the output
        is considerated to be achieved.

        Returns:
            tupple: a tupple containing:

            :postionWindow: current position window in quadrature counts.
            :Ok: A boolean if all requests went ok or not.
        '''
        index = self.objectIndex['Position Window']
        positionWindow, ok = self.readObject(index, 0x0)
        if not ok:
            logging.info('[Epos:{0}] Failed to read current position window'.format(
                sys._getframe().f_code.co_name))
            return None, False
        return positionWindow, True

    def setPositionWindow(self, positionWindow):
        '''Set position Window value

        Position window is the modulos threashold value in which the output
        is considerated to be achieved.

        Args:
            positionWindow: position window in quadrature counts
        Returns:
            bool: A boolean if all requests went ok or not.
        '''
        # validate attributes
        if not isinstance(positionWindow, int):
            logging.info('[Epos:{0}] Error input value must be int'.format(
                sys._getframe().f_code.co_name))
            return False
        if (positionWindow < 0 or positionWindow > 2**32-1):
            logging.info('[Epos:{0}] Error position window out of range'.format(
                sys._getframe().f_code.co_name))
            return False
        index = self.objectIndex['Position Window']
        ok = self.writeObject(index, 0x0, positionWindow.to_bytes(4, 'little'))
        if not ok:
            logging.info('[Epos:{0}] Failed to set current position window'.format(
                sys._getframe().f_code.co_name))
            return None, False
        return True

    def readPositionWindowTime(self):
        '''Read current position Window time value.

        Position window time is the minimum time in milliseconds in which
        the output must be inside the position window for the target is
        considerated to have been reached.

        Returns:
            tupple: a tupple containing:

            :postionWindowTime: current position window time in milliseconds.
            :Ok: A boolean if all requests went ok or not.
        '''
        index = self.objectIndex['Position Window Time']
        positionWindowTime, ok = self.readObject(index, 0x0)
        if not ok:
            logging.info('[Epos:{0}] Failed to read current position window time'.format(
                sys._getframe().f_code.co_name))
            return None, False
        return positionWindowTime, True

    def setPositionWindowTime(self, positionWindowTime):
        '''Set position Window Time value

        Position window time is the minimum time in milliseconds in which
        the output must be inside the position window for the target is
        considerated to have been reached.

        Args:
            positionWindowTime: position window time in milliseconds.
        Returns:
            bool: A boolean if all requests went ok or not.
        '''
        # validate attributes
        if not isinstance(positionWindowTime, int):
            logging.info('[Epos:{0}] Error input value must be int'.format(
                sys._getframe().f_code.co_name))
            return False
        if (positionWindowTime < 0 or positionWindowTime > 2**16-1):
            logging.info('[Epos:{0}] Error position window time out of range'.format(
                sys._getframe().f_code.co_name))
            return False
        index = self.objectIndex['Position Window Time']
        ok = self.writeObject(
            index, 0x0, positionWindowTime.to_bytes(2, 'little'))
        if not ok:
            logging.info('[Epos:{0}] Failed to set current position window time'.format(
                sys._getframe().f_code.co_name))
            return None, False
        return True

    def readVelocityValue(self):
        '''Read current velocity value

        Returns:
            tupple: a tupple containing:

            :velocity: current velocity in rpm.
            :Ok: A boolean if all requests went ok or not.
        '''
        index = self.objectIndex['Velocity Actual Value']
        velocity, ok = self.readObject(index, 0x0)
        if not ok:
            logging.info('[Epos:{0}] Failed to read current velocity value'.format(
                sys._getframe().f_code.co_name))
            return None, False
        return velocity, True

    def readVelocityValueAveraged(self):
        '''Read current velocity averaged value

        Returns:
            tupple: a tupple containing:

            :velocity: current velocity in rpm.
            :Ok: A boolean if all requests went ok or not.
        '''
        index = self.objectIndex['Velocity Actual Value Averaged']
        velocity, ok = self.readObject(index, 0x0)
        if not ok:
            logging.info('[Epos:{0}] Failed to read current velocity averaged value'.format(
                sys._getframe().f_code.co_name))
            return None, False
        return velocity, True

    def readCurrentValue(self):
        '''Read current value

        Returns:
            tupple: a tupple containing:

            :current: current in mA.
            :Ok: A boolean if all requests went ok or not.
        '''
        index = self.objectIndex['Current Actual Value']
        current, ok = self.readObject(index, 0x0)
        if not ok:
            logging.info('[Epos:{0}] Failed to read current value'.format(
                sys._getframe().f_code.co_name))
            return None, False
        return current, True

    def readCurrentValueAveraged(self):
        '''Read current averaged value

        Returns:
            tupple: a tupple containing:

            :current: current averaged in mA.
            :Ok: A boolean if all requests went ok or not.
        '''
        index = self.objectIndex['Current Actual Value Averaged']
        current, ok = self.readObject(index, 0x0)
        if not ok:
            logging.info('[Epos:{0}] Failed to read current averaged value'.format(
                sys._getframe().f_code.co_name))
            return None, False
        return current, True

    def saveConfig(self):
        '''Save all configurrations
        '''
        self.node.store()
        return

    def loadConfig(self):
        '''Load all configurations
        '''
        self.node.restore()
        return


def main():
    '''Test EPOS CANopen communication with some examples.

    Use a few examples to test communication with Epos device using
    a few functions. Also resets the fault error if present.

    Show sample using also the EDS file.
    '''

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
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s.%(msecs)03d] [%(name)-20s]: %(levelname)-8s %(message)s',
                        datefmt='%d-%m-%Y %H:%M:%S',
                        filename='epos.log',
                        filemode='w')
    # define a Handler which writes INFO messages or higher
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-20s: %(levelname)-8s %(message)s')
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
    statusword = epos.readObject(0x6041, 0)
    if not statusword:
        print("[EPOS] Error trying to read EPOS statusword\n")
        return
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
    epos.printPositionControlParameters()
    epos.printMotorConfig()
    epos.printSensorConfig()
    epos.disconnect()
    return


if __name__ == '__main__':
    main()
