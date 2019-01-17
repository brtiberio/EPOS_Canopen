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
    # from object dictionary.
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
                   'Internal Object NTC Temperature Sensor Value': 0x202A,
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
    errorIndex = {0x00000000: 'Error code: no error',
                  # 0x050x xxxx
                  0x05030000: 'Error code: toggle bit not alternated',
                  0x05040000: 'Error code: SDO protocol timeout',
                  0x05040001: 'Error code: Client/server command specifier not valid or unknown',
                  0x05040002: 'Error code: invalid block size',
                  0x05040003: 'Error code: invalid sequence number',
                  0x05040004: 'Error code: CRC error',
                  0x05040005: 'Error code: out of memory',
                  # 0x060x xxxx
                  0x06010000: 'Error code: Unsupported access to an object',
                  0x06010001: 'Error code: Attempt to read a write-only object',
                  0x06010002: 'Error code: Attempt to write a read-only object',
                  0x06020000: 'Error code: object does not exist',
                  0x06040041: 'Error code: object can not be mapped to the PDO',
                  0x06040042: 'Error code: the number and length of the objects to be mapped would exceed PDO length',
                  0x06040043: 'Error code: general parameter incompatibility',
                  0x06040047: 'Error code: general internal incompatibility in the device',
                  0x06060000: 'Error code: access failed due to an hardware error',
                  0x06070010: 'Error code: data type does not match, length of service parameter does not match',
                  0x06070012: 'Error code: data type does not match, length of service parameter too high',
                  0x06070013: 'Error code: data type does not match, length of service parameter too low',
                  0x06090011: 'Error code: subindex does not exist',
                  0x06090030: 'Error code: value range of parameter exceeded',
                  0x06090031: 'Error code: value of parameter written is too high',
                  0x06090032: 'Error code: value of parameter written is too low',
                  0x06090036: 'Error code: maximum value is less than minimum value',
                  0x060A0023: 'Error code: resource not available: SDO connection',
                  # 0x0800 xxxx
                  0x08000000: 'Error code: General error',
                  0x08000020: 'Error code: Data cannot be transferred or stored to the application',
                  0x08000021: 'Error code: Data cannot be transferred or stored to the application because of local control',
                  0x08000022: 'Error code: Wrong Device State. Data can not be transfered',
                  0x08000023: 'Error code: Object dictionary dynamic generation failed or no object dictionary present',
                  # Maxon defined error codes
                  0x0f00ffc0: 'Error code: wrong NMT state',
                  0x0f00ffbf: 'Error code: rs232 command illegal',
                  0x0f00ffbe: 'Error code: password incorrect',
                  0x0f00ffbc: 'Error code: device not in service mode',
                  0x0f00ffB9: 'Error code: error in Node-ID'
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

    def begin(self, nodeID, _channel='can0', _bustype='socketcan', object_dictionary=None):
        """ Initialize Epos device

        Configure and setup Epos device.

        Args:
            nodeID:    Node ID of the device.
            _channel (optional):   Port used for communication. Default can0
            _bustype (optional):   Port type used. Default socketcan.
            object_dictionary (optional):   Name of EDS file, if any available.
        Return:
            bool: A boolean if all went ok.
        """
        try:
            self.node = self.network.add_node(
                nodeID, object_dictionary=object_dictionary)
            # in not connected?
            if not self.network.bus:
                # so try to connect
                self.network.connect(channel=_channel, bustype=_bustype)
        except Exception as e:
            self.log_info('Exception caught:{0}'.format(str(e)))
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

    def log_info(self, message=None):
        """ Log a message

        A wrap around logging.
        The log message will have the following structure\:
        [class name \: function name ] message

        Args:
            message: a string with the message.
        """
        if message is None:
            # do nothing
            return
        self.logger.info('[{0}:{1}] {2}'.format(
            self.__class__.__name__,
            sys._getframe(1).f_code.co_name,
            message))
        return

    def log_debug(self, message=None):
        """ Log a message with debug level

        A wrap around logging.
        The log message will have the following structure\:
        [class name \: function name ] message

        the function name will be the caller function retrieved automatically 
        by using sys._getframe(1).f_code.co_name

        Args:
            message: a string with the message.
        """
        if message is None:
            # do nothing
            return

        self.logger.debug('[{0}:{1}] {2}'.format(
            self.__class__.__name__,
            sys._getframe(1).f_code.co_name,
            message))
        return

    def read_object(self, index, subindex):
        """Reads an object

         Request a read from dictionary object referenced by index and subindex.

         Args:
             index:     reference of dictionary object index
             subindex:  reference of dictionary object subindex
         Returns:
             bytes:  message returned by EPOS or empty if unsuccessful
        """
        if self._connected:
            try:
                return self.node.sdo.upload(index, subindex)
            except Exception as e:
                self.log_info('Exception caught:{0}'.format(str(e)))
                return None
        else:
            self.log_info(' Error: {0} is not connected'.format(
                self.__class__.__name__))
            return None

    def write_object(self, index, subindex, data):
        """Write an object

         Request a write to dictionary object referenced by index and subindex.

         Args:
             index:     reference of dictionary object index
             subindex:  reference of dictionary object subindex
             data:      data to be stored
         Returns:
             bool:      boolean if all went ok or not
        """
        if self._connected:
            try:
                self.node.sdo.download(index, subindex, data)
                return True
            except canopen.SdoAbortedError as e:
                text = "Code 0x{:08X}".format(e.code)
                if e.code in self.errorIndex:
                    text = text + ", " + self.errorIndex[e.code]
                self.log_info('SdoAbortedError: ' + text)
                return False
            except canopen.SdoCommunicationError:
                self.log_info('SdoAbortedError: Timeout or unexpected response')
                return False
        else:
            self.log_info(' Error: {0} is not connected'.format(
                self.__class__.__name__))
            return False

    # --------------------------------------------------------------------------
    # High level functions
    # --------------------------------------------------------------------------

    def read_statusword(self):
        """Read StatusWord

        Request current statusword from device.

        Returns:
            tuple: A tuple containing:

            :statusword:  the current statusword or None if any error.
            :ok: A boolean if all went ok.
        """
        index = self.objectIndex['StatusWord']
        subindex = 0
        statusword = self.read_object(index, subindex)
        # failed to request?
        if not statusword:
            self.log_info('Error trying to read {0} statusword'.format(
                self.__class__.__name__))
            return statusword, False

        # return statusword as an int type
        statusword = int.from_bytes(statusword, 'little')
        return statusword, True

    def read_controlword(self):
        """Read ControlWord

        Request current controlword from device.

        Returns:
            tuple: A tuple containing:

            :controlword: the current controlword or None if any error.
            :ok: A boolean if all went ok.
        """
        index = self.objectIndex['ControlWord']
        subindex = 0
        controlword = self.read_object(index, subindex)
        # failed to request?
        if not controlword:
            self.log_info('Error trying to read {0} controlword'.format(
                self.__class__.__name__))
            return controlword, False

        # return controlword as an int type
        controlword = int.from_bytes(controlword, 'little')
        return controlword, True

    def write_controlword(self, controlword):
        """Send controlword to device

        Args:
            controlword: word to be sent.

        Returns:
            bool: a boolean if all went ok.
        """
        # sending new controlword
        self.log_debug(
            'Sending controlword Hex={0:#06X} Bin={0:#018b}'.format(controlword))
        controlword = controlword.to_bytes(2, 'little')
        return self.write_object(0x6040, 0, controlword)

    def check_state(self):
        """Check current state of Epos

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
        """
        statusword, ok = self.read_statusword()
        if not ok:
            self.log_info('Failed to request StatusWord')
            return -1
        else:

            # state 'start' (0)
            # statusWord == x0xx xxx0  x000 0000
            bitmask = 0b0100000101111111
            if bitmask & statusword == 0:
                return 0

            # state 'not ready to switch on' (1)
            # statusWord == x0xx xxx1  x000 0000
            bitmask = 0b0100000101111111
            if bitmask & statusword == 256:
                return 1

            # state 'switch on disabled' (2)
            # statusWord == x0xx xxx1  x100 0000
            bitmask = 0b0100000101111111
            if bitmask & statusword == 320:
                return 2

            # state 'ready to switch on' (3)
            # statusWord == x0xx xxx1  x010 0001
            bitmask = 0b0100000101111111
            if bitmask & statusword == 289:
                return 3

            # state 'switched on' (4)
            # statusWord == x0xx xxx1  x010 0011
            bitmask = 0b0000000101111111
            if bitmask & statusword == 291:
                return 4

            # state 'refresh' (5)
            # statusWord == x1xx xxx1  x010 0011
            bitmask = 0b0100000101111111
            if bitmask & statusword == 16675:
                return 5

            # state 'measure init' (6)
            # statusWord == x1xx xxx1  x011 0011
            bitmask = 0b0100000101111111
            if bitmask & statusword == 16691:
                return 6
            # state 'operation enable' (7)
            # statusWord == x0xx xxx1  x011 0111
            bitmask = 0b0100000101111111
            if bitmask & statusword == 311:
                return 7

            # state 'Quick Stop Active' (8)
            # statusWord == x0xx xxx1  x001 0111
            bitmask = 0b0100000101111111
            if bitmask & statusword == 279:
                return 8

            # state 'fault reaction active (disabled)' (9)
            # statusWord == x0xx xxx1  x000 1111
            bitmask = 0b0100000101111111
            if bitmask & statusword == 271:
                return 9

            # state 'fault reaction active (enabled)' (10)
            # statusWord == x0xx xxx1  x001 1111
            bitmask = 0b0100000101111111
            if bitmask & statusword == 287:
                return 10

            # state 'fault' (11)
            # statusWord == x0xx xxx1  x000 1000
            bitmask = 0b0100000101111111
            if bitmask & statusword == 264:
                return 11

        # in case of unknown state or fail
        # in case of unknown state or fail
        self.log_info('Error: Unknown state. Statusword is Bin={0:#018b}'.format(
            int.from_bytes(statusword, 'little'))
        )
        return -1

    def print_state(self):
        ID = self.check_state()
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

    def print_statusword(self):
        statusword, ok = self.read_statusword()
        if not ok:
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

    def print_controlword(self, controlword=None):
        """Print the meaning of controlword

        Check the meaning of current controlword of device or check the meaning of your own controlword.
        Useful to check your own controlword before actually sending it to device.

        Args:
            controlword (optional): If None, request the controlword of device.

        """
        if not controlword:
            controlword, ok = self.read_controlword()
            if not ok:
                print('[{0}:{1}] Failed to retrieve controlword\n'.format(
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

    def read_position_mode_setting(self):
        """Reads the set desired Position

        Ask Epos device for demand position object. If a correct
        request is made, the position is placed in answer. If
        not, an answer will be empty

        Returns:
            tuple: A tuple containing:

            :position: the demanded position value.
            :ok:       A boolean if all requests went ok or not.
        """
        index = self.objectIndex['PositionMode Setting Value']
        subindex = 0
        position = self.read_object(index, subindex)
        # failed to request?
        if not position:
            self.log_info("Error trying to read EPOS PositionMode Setting Value")
            return position, False
        # return value as signed int
        position = int.from_bytes(position, 'little', signed=True)
        return position, True

    def set_position_mode_setting(self, position):
        """Sets the desired Position

        Ask Epos device to define position mode setting object.

        Returns:
            bool: A boolean if all requests went ok or not.
        """
        index = self.objectIndex['PositionMode Setting Value']
        subindex = 0
        if position < -2 ** 31 or position > 2 ** 31 - 1:
            self.log_info("Position out of range")
            return False
        # change to bytes as an int32 value
        position = position.to_bytes(4, 'little', signed=True)
        return self.write_object(index, subindex, position)

    def read_velocity_mode_setting(self):
        """Reads the set desired velocity

        Asks EPOS for the desired velocity value in velocity control mode

        Returns:
            tuple: A tuple containing:

            :velocity: Value set or None if any error.
            :ok: A boolean if successful or not.
        """
        index = self.objectIndex['VelocityMode Setting Value']
        subindex = 0
        velocity = self.read_object(index, subindex)
        # failed to request?
        if not velocity:
            self.log_info("Error trying to read EPOS VelocityMode Setting Value")
            return velocity, False
        # return value as signed int
        velocity = int.from_bytes(velocity, 'little', signed=True)
        return velocity, True

    def set_velocity_mode_setting(self, velocity):
        """Set desired velocity

        Set the value for desired velocity in velocity control mode.

        Args:
            velocity: value to be set.
        Returns:
            bool: a boolean if successful or not.
        """
        index = self.objectIndex['VelocityMode Setting Value']
        subindex = 0
        if velocity < -2 ** 31 or velocity > 2 ** 31 - 1:
            self.log_info("Velocity out of range")
            return False
        # change to bytes as an int32 value
        velocity = velocity.to_bytes(4, 'little', signed=True)
        return self.write_object(index, subindex, velocity)

    def read_current_mode_setting(self):
        """Read current value set

        Asks EPOS for the current value set in current control mode.

        Returns:
            tuple: A tuple containing:

            :current: value set.
            :ok:      a boolean if successful or not.
        """
        index = self.objectIndex['CurrentMode Setting Value']
        subindex = 0
        current = self.read_object(index, subindex)
        # failed to request
        if not current:
            self.log_info("Error trying to read EPOS CurrentMode Setting Value")
            return current, False
        # return value as signed int
        current = int.from_bytes(current, 'little', signed=True)
        return current, True

    def set_current_mode_setting(self, current):
        """Set desired current

        Set the value for desired current in current control mode

        Args:
            current: the value to be set [mA]
        Returns:
            bool: a boolean if successful or not
        """
        index = self.objectIndex['CurrentMode Setting Value']
        subindex = 0
        if current < -2 ** 15 or current > 2 ** 15 - 1:
            self.log_info("Current out of range")
            return False
        # change to bytes as an int16 value
        current = current.to_bytes(2, 'little', signed=True)
        return self.write_object(index, subindex, current)

    def read_op_mode(self):
        """Read current operation mode

        Returns:
            tuple: A tuple containing:

            :op_mode: current op_mode or None if request fails
            :ok:     A boolean if successful or not
        """
        index = self.objectIndex['Modes of Operation']
        subindex = 0
        op_mode = self.read_object(index, subindex)
        # failed to request
        if not op_mode:
            self.log_info("Error trying to read EPOS Operation Mode")
            return op_mode, False
        # change to int value
        op_mode = int.from_bytes(op_mode, 'little', signed=True)
        return op_mode, True

    def set_op_mode(self, op_mode):
        """Set Operation mode

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
            op_mode: the desired opMode.
        Returns:
            bool:     A boolean if all requests went ok or not.
        """
        index = self.objectIndex['Modes of Operation']
        subindex = 0
        if not op_mode in self.opModes:
            self.log_info("Unknown Operation Mode: {0}".format(op_mode))
            return False
        op_mode = op_mode.to_bytes(1, 'little', signed=True)
        return self.write_object(index, subindex, op_mode)

    def print_op_mode(self):
        """Print current operation mode
        """
        op_mode, ok = self.read_op_mode()
        if not ok:
            print('Failed to request current operation mode')
            return
        if not (op_mode in self.opModes):
            self.log_info("Unknown Operation Mode: {0}".format(op_mode))
            return
        else:
            print('Current operation mode is \"{}\"'.format(
                self.opModes[op_mode]))
        return

    def change_state(self, new_state):
        """Change EPOS state

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
            new_state: string with state witch user want to switch.

        Returns:
            bool: boolean if all went ok and no error was received.
        """
        state_order = ['shutdown', 'switch on', 'disable voltage', 'quick stop',
                       'disable operation', 'enable operation', 'fault reset']

        if not (new_state in state_order):
            self.log_info("Unknown state: {0}".format(new_state))
            return False
        else:
            controlword, Ok = self.read_controlword()
            if not Ok:
                self.log_info("Failed to retrieve controlword")
                return False
            # shutdown  0xxx x110
            if new_state == 'shutdown':
                # clear bits
                mask = ~ (1 << 7 | 1 << 0)
                controlword = controlword & mask
                # set bits
                mask = (1 << 2 | 1 << 1)
                controlword = controlword | mask
                return self.write_controlword(controlword)
            # switch on 0xxx x111
            if new_state == 'switch on':
                # clear bits
                mask = ~ (1 << 7)
                controlword = controlword & mask
                # set bits
                mask = (1 << 2 | 1 << 1 | 1 << 0)
                controlword = controlword | mask
                return self.write_controlword(controlword)
            # disable voltage 0xxx xx0x
            if new_state == 'switch on':
                # clear bits
                mask = ~ (1 << 7 | 1 << 1)
                controlword = controlword & mask
                return self.write_controlword(controlword)
            # quick stop 0xxx x01x
            if new_state == 'quick stop':
                # clear bits
                mask = ~ (1 << 7 | 1 << 2)
                controlword = controlword & mask
                # set bits
                mask = (1 << 1)
                controlword = controlword | mask
                return self.write_controlword(controlword)
            # disable operation 0xxx 0111
            if new_state == 'disable operation':
                # clear bits
                mask = ~ (1 << 7 | 1 << 3)
                controlword = controlword & mask
                # set bits
                mask = (1 << 2 | 1 << 1 | 1 << 0)
                controlword = controlword | mask
                return self.write_controlword(controlword)
            # enable operation 0xxx 1111
            if new_state == 'enable operation':
                # clear bits
                mask = ~ (1 << 7)
                controlword = controlword & mask
                # set bits
                mask = (1 << 3 | 1 << 2 | 1 << 1 | 1 << 0)
                controlword = controlword | mask
                return self.write_controlword(controlword)
            # fault reset 1xxx xxxx
            if new_state == 'fault reset':
                # set bits
                mask = (1 << 7)
                controlword = controlword | mask
                return self.write_controlword(controlword)

    def set_motor_config(self, motor_type, current_limit, max_speed, pole_pair_number):
        """Set motor configuration

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
            motor_type:      value of motor type. see table behind.
            current_limit:   max continuous current limit [mA].
            max_speed:   max allowed speed in current mode [rpm].
            pole_pair_number: number of pole pairs for brushless DC motors.
        Returns:
            bool:     A boolean if all requests went ok or not.
        """
        # ------------------------------------------------------------------------
        # check values of input
        # ------------------------------------------------------------------------
        if not ((motor_type in self.motorType) or (motor_type in self.motorType.values())):
            self.log_info("Unknown motor_type: {0}".format(motor_type))
            return False
        if (current_limit < 0) or (current_limit > 2 ** 16 - 1):
            self.log_info("Current limit out of range: {0} ".format(current_limit))
            return False
        if (pole_pair_number < 0) or (pole_pair_number > 255):
            self.log_info("Pole pair number out of range: {0} ".format(pole_pair_number))
            return False
        if (max_speed < 1) or (max_speed > 2 ** 16 - 1):
            self.log_info("Maximum speed out of range: {0} ".format(max_speed))
            return False
        # ------------------------------------------------------------------------
        # store motor_type
        # ------------------------------------------------------------------------
        index = self.objectIndex['MotorType']
        subindex = 0
        if motor_type in self.motorType:
            motor_type = self.motorType[motor_type]
        ok = self.write_object(index, subindex, motor_type.to_bytes(1, 'little'))
        if not ok:
            self.log_info("Failed to set motor_type")
            return ok
        # ------------------------------------------------------------------------
        # store motorData
        # ------------------------------------------------------------------------
        index = self.objectIndex['Motor Data']
        # check if it was passed a float
        if isinstance(current_limit, float):
            # if true trunc to closes int, similar to floor
            current_limit = current_limit.__trunc__
        # constant current limit has subindex 1
        ok = self.write_object(index, 1, current_limit.to_bytes(2, 'little'))
        if not ok:
            self.log_info("Failed to set current_limit")
            return ok
        # output current limit has subindex 2 and is recommended to
        # be the double of constant current limit
        ok = self.write_object(
            index, 2, (current_limit * 2).to_bytes(2, 'little'))
        if not ok:
            self.log_info("Failed to set output current limit")
            return ok
        # pole pair number has subindex 3
        ok = self.write_object(index, 3, pole_pair_number.to_bytes(1, 'little'))
        if not ok:
            self.log_info("Failed to set pole pair number: {0}".format(pole_pair_number))
            return ok
        # maxSpeed has subindex 4
        # check if it was passed a float
        if isinstance(max_speed, float):
            # if true trunc to closes int, similar to floor
            max_speed = max_speed.__trunc__
        ok = self.write_object(index, 4, max_speed.to_bytes(2, 'little'))
        if not ok:
            self.log_info("Failed to set maximum speed: {0}".format(max_speed))
            return ok
        # no fails, return True
        return True

    def read_motor_config(self):
        """Read motor configuration

        Read the current motor configuration

        Requests from EPOS the current motor type and motor data.
        The motor_config is a dictionary containing the following information:

        * **motor_type** describes the type of motor.
        * **current_limit** - describes the maximum continuous current limit.
        * **max_current_limit** - describes the maximum allowed current limit.
          Usually is set as two times the continuous current limit.
        * **pole_pair_number** - describes the pole pair number of the rotor of
          the brushless DC motor.
        * **max_speed** - describes the maximum allowed speed in current mode.
        * **thermal_time_constant** - describes the thermal time constant of motor
          winding is used to calculate the time how long the maximal output
          current is allowed for the connected motor [100 ms].

        If unable to request the configuration or unsuccessfully, None and false is
        returned .

        Returns:
            tuple: A tuple with:

            :motor_config: A structure with the current configuration of motor
            :ok:          A boolean if all went as expected or not.
        """
        motor_config = {}  # dictionary to store config
        # ------------------------------------------------------------------------
        # store motorType
        # ------------------------------------------------------------------------
        index = self.objectIndex['MotorType']
        subindex = 0
        value = self.read_object(index, subindex)
        if value is None:
            self.log_info("Failed to get motorType")
            return None, False
        # append motorType to dict
        motor_config.update({'motorType': int.from_bytes(value, 'little')})
        # ------------------------------------------------------------------------
        # store motorData
        # ------------------------------------------------------------------------
        index = self.objectIndex['Motor Data']
        value = self.read_object(index, 1)
        if value is None:
            self.log_info("Failed to get currentLimit")
            return None, False
        motor_config.update({'currentLimit': int.from_bytes(value, 'little')})
        # output current limit has subindex 2 and is recommended to
        # be the double of constant current limit
        value = self.read_object(index, 2)
        if value is None:
            self.log_info("Failed to get maxCurrentLimit")
            return None, False
        motor_config.update(
            {'maxCurrentLimit': int.from_bytes(value, 'little')})
        # pole pair number has subindex 3
        value = self.read_object(index, 3)
        if value is None:
            self.log_info("Failed to get polePairNumber")
            return None, False
        motor_config.update({'polePairNumber': int.from_bytes(value, 'little')})
        # maxSpeed has subindex 4
        value = self.read_object(index, 4)
        if value is None:
            self.log_info("Failed to get maximumSpeed")
            return None, False
        motor_config.update({'maximumSpeed': int.from_bytes(value, 'little')})
        # thermal time constant has index 5
        value = self.read_object(index, 5)
        if value is None:
            self.log_info("Failed to get thermalTimeConstant")
            return None, False
        motor_config.update(
            {'thermalTimeConstant': int.from_bytes(value, 'little')})
        # no fails, return dict and ok
        return motor_config, True

    def print_motor_config(self):
        """Print current motor config

        Request current motor config and print it
        """
        motor_config, ok = self.read_motor_config()
        for key, value in self.motorType.items():  # dict.items():  (for Python 3.x)
            if value == motor_config['motorType']:
                break

        if not ok:
            print('[EPOS:{0}] Failed to request current motor configuration'.format(
                sys._getframe().f_code.co_name))
            return
        print('--------------------------------------------------------------')
        print('Current motor configuration:')
        print('--------------------------------------------------------------')
        print('Motor Type is {0}'.format(key))
        print('Motor constant current limit {0}[mA]'.format(
            motor_config['currentLimit']))
        print('Motor maximum current limit {0}[mA]'.format(
            motor_config['maxCurrentLimit']))
        print('Motor maximum speed in current mode {0}[rpm]'.format(
            motor_config['maximumSpeed']))
        print('Motor number of pole pairs {0}'.format(
            motor_config['polePairNumber']))
        print('Motor thermal time constant {0}[s]'.format(
            motor_config['currentLimit'] / 10.0))
        print('--------------------------------------------------------------')
        return

    def set_sensor_config(self, pulse_number, sensor_type, sensor_polarity):
        """Change sensor configuration

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
            pulse_number:    Number of pulses per revolution.
            sensor_type:     1,2 or 3 according to the previous table.
            sensor_polarity: a value between 0 and 3 describing the polarity
                              of sensors as stated before.
        Returns:
            bool: A boolean if all went as expected or not.
        """
        # validate attributes first
        if pulse_number < 16 or pulse_number > 7500:
            self.log_info("Error pulse_number out of range: {0}".format(pulse_number))
            return False
        if not (sensor_type in [1, 2, 3]):
            self.log_info("Error sensor_type not valid: {0}".format(sensor_type))
            return False
        if not (sensor_polarity in [0, 1, 2, 3]):
            self.log_info("Error sensor_polarity not valid: {0}".format(sensor_polarity))
            return False
        # change epos state first to shutdown state
        # or it will fail
        ok = self.change_state('shutdown')
        if not ok:
            self.log_info("Error failed to change EPOS state into shutdown")
            return False
        # get index
        index = self.objectIndex['Sensor Configuration']
        # pulse_number has subindex 1
        ok = self.write_object(index, 1, pulse_number.to_bytes(2, 'little'))
        if not ok:
            self.log_info("Error setting pulse_number")
            return False
        # sensor_type has subindex 2
        ok = self.write_object(index, 2, sensor_type.to_bytes(2, 'little'))
        if not ok:
            self.log_info("Error setting sensor_type")
            return False
        # sensor_polarity has subindex 4
        ok = self.write_object(index, 4, sensor_polarity.to_bytes(2, 'little'))
        if not ok:
            self.log_info("Error setting sensor_polarity")
            return False
        return True

    def read_sensor_config(self):
        """Read sensor configuration

        Requests from EPOS the current sensor configuration.
        The sensor_config is an structure containing the following information:

        * sensorType - describes the type of sensor.
        * pulseNumber - describes the number of pulses per revolution in one channel.
        * sensorPolarity - describes the of each sensor.

        If unable to request the configuration or unsucessfull, an empty
        structure is returned. Any error inside any field requests are marked
        with 'error'.

        Returns:
            tuple: A tuple containing:

            :sensor_config: A dictionary with the current configuration of the sensor
            :ok: A boolean if all went as expected or not.
        """
        sensor_config = {}
        # get index
        index = self.objectIndex['Sensor Configuration']
        # pulseNumber has subindex 1
        value = self.read_object(index, 1)
        if value is None:
            self.log_info("Error getting pulseNumber")
            return None, False
        sensor_config.update({'pulseNumber': int.from_bytes(value, 'little')})
        # sensorType has subindex 2
        value = self.read_object(index, 2)
        if value is None:
            self.log_info("Error getting sensorType")
            return None, False
        sensor_config.update({'sensorType': int.from_bytes(value, 'little')})
        # sensorPolarity has subindex 4
        value = self.read_object(index, 4)
        if value is None:
            self.log_info("Error getting sensorPolarity")
            return None, False
        sensor_config.update(
            {'sensorPolarity': int.from_bytes(value, 'little')})
        return sensor_config, True

    def print_sensor_config(self):
        """Print current sensor configuration
        """
        sensor_config, ok = self.read_sensor_config()
        # to adjust indexes ignore use a dummy first element
        sensor_type = ['', 'Incremental Encoder with index (3-channel)',
                       'Incremental Encoder without index (2-channel)',
                       'Hall Sensors (Remark: consider worse resolution)']
        if not ok:
            print('[EPOS:{0}] Failed to request current sensor configuration'.format(
                sys._getframe().f_code.co_name))
            return
        print('--------------------------------------------------------------')
        print('Current sensor configuration:')
        print('--------------------------------------------------------------')
        print('Sensor pulse Number is {0}'.format(sensor_config['pulseNumber']))
        print('Sensor type is {0}'.format(
            sensor_type[sensor_config['sensorType']]))
        value = sensor_config['sensorPolarity']
        if (value & 1 << 1) >> 1:
            print('Hall sensor polarity inverted')
        else:
            print('Hall sensor polarity normal')
        if value & 1:
            print('Encoder polarity inverted')
        else:
            print('Encoder polarity normal')
        print('--------------------------------------------------------------')
        return

    def set_current_control_parameters(self, pGain, iGain):
        """Set the PI gains used in current control mode

        Args:
            pGain: Proportional gain.
            iGain: Integral gain.
        Returns:
            bool: A boolean if all went as expected or not.
        """
        # any float?
        if isinstance(pGain, float) or isinstance(iGain, float):
            self.log_info("Error all values must be int, not floats")
            return False
        # any out of range?
        # validate attributes first
        if pGain < 0 or pGain > 2 ** 15 - 1:
            self.log_info("Error pGain out of range: {0}".format(pGain))
            return False
        if iGain < 0 or iGain > 2 ** 15 - 1:
            self.log_info("Error iGain out of range: {0}".format(iGain))
            return False
        # all ok. Proceed
        index = self.objectIndex['Current Control Parameter']
        # pGain has subindex 1
        ok = self.write_object(
            index, 1, pGain.to_bytes(2, 'little', signed=True))
        if not ok:
            self.log_info("Error setting pGain")
            return False
        # iGain has subindex 2
        ok = self.write_object(
            index, 2, iGain.to_bytes(2, 'little', signed=True))
        if not ok:
            self.log_info("Error setting iGain")
            return False
        # all ok, return True
        return True

    def read_current_control_parameters(self):
        """Read the PI gains used in  current control mode

        Returns:
            tuple: A tuple containing:

            :gains: A dictionary with the current pGain and iGain
            :ok: A boolean if all went as expected or not.
        """
        index = self.objectIndex['Current Control Parameter']
        curr_mode_parameters = {}
        # pGain has subindex 1
        value = self.read_object(index, 1)
        if value is None:
            self.log_info("Error getting pGain")
            return None, False
        # can not be less than zero, but is considered signed!
        curr_mode_parameters.update(
            {'pGain': int.from_bytes(value, 'little', signed=True)})

        # iGain has subindex 2
        value = self.read_object(index, 2)
        if value is None:
            self.log_info("Error getting iGain")
            return None, False
        curr_mode_parameters.update(
            {'iGain': int.from_bytes(value, 'little', signed=True)})
        return curr_mode_parameters, True

    def print_current_control_parameters(self):
        """Print the current mode control PI gains

        Request current mode control parameter gains from device and print.
        """
        curr_mode_parameters, ok = self.read_current_control_parameters()
        if not ok:
            print('[Epos:{0}] Error requesting Position mode control parameters'.format(
                sys._getframe().f_code.co_name))
            return
        print('--------------------------------------------------------------')
        print('Current Position mode control parameters:')
        print('--------------------------------------------------------------')
        for key, value in curr_mode_parameters.items():
            print('{0}: {1}'.format(key, value))
        print('--------------------------------------------------------------')

    def set_software_pos_limit(self, min_pos, max_pos):
        """Set the software position limits

        Use encoder readings as limit position for extremes
        range = [-2147483648 | 2147483647]

        Args:
            min_pos: minimum position limit
            max_pos: maximum position limit
        Return:
            bool: A boolean if all went as expected or not.
        """
        # validate attributes
        if not (isinstance(min_pos, int) and isinstance(max_pos, int)):
            self.log_info("Error input values must be int")
            return False
        if min_pos < -2 ** 31 or min_pos > 2 ** 31 - 1:
            self.log_info("Error min_pos out of range")
            return False
        if max_pos < -2 ** 31 or max_pos > 2 ** 31 - 1:
            self.log_info("Error max_pos out of range")
            return False
        index = self.objectIndex['Software Position Limit']
        # min_pos has subindex 1
        ok = self.write_object(index, 0x1, min_pos.to_bytes(4, 'little'))
        if not ok:
            self.log_info("Error setting min_pos")
            return False
        # max_pos has subindex 2
        ok = self.write_object(index, 0x2, max_pos.to_bytes(4, 'little'))
        if not ok:
            self.log_info("Error setting max_pos")
            return False
        return True

    def read_software_pos_limit(self):
        """Read the software position limit

        Return:
            tuple: A tuple containing:

            :limits: a dictionary containing minPos and maxPos
            :ok: A boolean if all went as expected or not.
        """
        limits = {}
        index = self.objectIndex['Software Position Limit']
        # min has subindex 1
        value = self.read_object(index, 0x1)
        if value is None:
            self.log_info("Failed to read min position")
            return None, False
        limits.update({'minPos': int.from_bytes(value, 'little')})
        # max has subindex 2
        value = self.read_object(index, 0x2)
        if value is None:
            self.log_info("Failed to read max position")
            return None, False
        limits.update({'maxPos': int.from_bytes(value, 'little')})
        return limits, True

    def print_software_pos_limit(self):
        """ Print current software position limits
        """
        limits, ok = self.read_software_pos_limit()
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

    def set_quick_stop_deceleration(self, quickstop_deceleration):
        """Set the quick stop deceleration.

        The quick stop deceleration defines the deceleration
        during a fault reaction.

        Args:
            quickstop_deceleration: the value of deceleration in rpm/s
        Return:
            bool: A boolean if all went as expected or not.
        """
        # validate attributes
        if not isinstance(quickstop_deceleration, int):
            self.log_info("Error input value must be int")
            return False
        if quickstop_deceleration < 1 or quickstop_deceleration > 2 ** 32 - 1:
            self.log_info("Error quick stop deceleration out of range")
            return False
        index = self.objectIndex['QuickStop Deceleration']
        ok = self.write_object(
            index, 0x0, quickstop_deceleration.to_bytes(4, 'little'))
        if not ok:
            self.log_info("Error setting quick stop deceleration")
            return False
        return True

    def read_quickstop_deceleration(self):
        """ Read the quick stop deceleration.

        Read deceleration used in fault reaction state.

        Returns:
            tuple: A tuple containing:

            :quickstop_deceleration: The value of deceleration in rpm/s.
            :ok: A boolean if all went as expected or not.
        """
        index = self.objectIndex['QuickStop Deceleration']
        deceleration = self.read_object(index, 0x0)
        if deceleration is None:
            self.log_info("Failed to read quick stop deceleration value")
            return None, False
        deceleration = int.from_bytes(deceleration, 'little')
        return deceleration, True

    def read_position_control_parameters(self):
        """ Read position mode control parameters

        Read position mode control PID gains and and feedfoward
        and acceleration values

        Returns:
            tuple: A tuple containing:

            :pos_mode_parameters: a dictionary containing pGain,
                iGain, dGain, vFeed and aFeed.
            :ok: A boolean if all went as expected or not.
        """
        index = self.objectIndex['Position Control Parameter']
        pos_mode_parameters = {}
        # pGain has subindex 1
        value = self.read_object(index, 1)
        if value is None:
            self.log_info("Error getting pGain")
            return None, False
        # can not be less than zero, but is considered signed!
        pos_mode_parameters.update(
            {'pGain': int.from_bytes(value, 'little', signed=True)})

        # iGain has subindex 2
        value = self.read_object(index, 2)
        if value is None:
            self.log_info("Error getting iGain")
            return None, False
        pos_mode_parameters.update(
            {'iGain': int.from_bytes(value, 'little', signed=True)})

        # dGain has subindex 3
        value = self.read_object(index, 3)
        if value is None:
            self.log_info("Error getting dGain")
            return None, False
        pos_mode_parameters.update(
            {'dGain': int.from_bytes(value, 'little', signed=True)})

        # vFeedFoward has subindex 4
        value = self.read_object(index, 4)
        if value is None:
            self.log_info("Error getting vFeed")
            return None, False
        # these are not considered signed!
        pos_mode_parameters.update({'vFeed': int.from_bytes(value, 'little')})

        # aFeedFoward has subindex 5
        value = self.read_object(index, 5)
        if value is None:
            self.log_info("Error getting aFeed")
            return None, False
        pos_mode_parameters.update({'aFeed': int.from_bytes(value, 'little')})
        return pos_mode_parameters, True

    def set_position_control_parameters(self, pGain, iGain, dGain, vFeed=0, aFeed=0):
        """Set position mode control parameters

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
            vFeed: velocity feed forward gain value. Default to 0
            aFeed: acceleration feed forward gain value. Default to 0
        Returns:
            OK: A boolean if all requests went ok or not
        """
        # validate attributes first
        # any float?
        if (isinstance(pGain, float) or isinstance(iGain, float) or
                isinstance(dGain, float) or isinstance(vFeed, float) or
                isinstance(aFeed, float)):
            self.log_info("Error all values must be int, not floats")
            return False
        # any out of range?
        if pGain < 0 or pGain > 2 ** 15 - 1:
            self.log_info("Error pGain out of range: {0}".format(pGain))
            return False
        if iGain < 0 or iGain > 2 ** 15 - 1:
            self.log_info("Error iGain out of range: {0}".format(
                iGain))
            return False
        if dGain < 0 or dGain > 2 ** 15 - 1:
            self.log_info("Error dGain out of range: {0}".format(
                dGain))
            return False
        if iGain < 0 or iGain > 2 ** 15 - 1:
            self.log_info("Error iGain out of range: {0}".format(
                pGain))
            return False
        if vFeed < 0 or vFeed > 2 ** 16 - 1:
            self.log_info("Error vFeed out of range: {0}".format(
                vFeed))
            return False
        if aFeed < 0 or aFeed > 2 ** 16 - 1:
            self.log_info("Error aFeed out of range: {0}".format(
                aFeed))
            return False
        # all ok. Proceed
        index = self.objectIndex['Position Control Parameter']
        # pGain has subindex 1
        ok = self.write_object(
            index, 1, pGain.to_bytes(2, 'little', signed=True))
        if not ok:
            self.log_info("Error setting pGain")
            return False
        # iGain has subindex 2
        ok = self.write_object(
            index, 2, iGain.to_bytes(2, 'little', signed=True))
        if not ok:
            self.log_info("Error setting iGain")
            return False
        # dGain has subindex 3
        ok = self.write_object(
            index, 3, dGain.to_bytes(2, 'little', signed=True))
        if not ok:
            self.log_info("Error setting dGain")
            return False
        # vFeed has subindex 4
        ok = self.write_object(index, 4, vFeed.to_bytes(2, 'little'))
        if not ok:
            self.log_info("Error setting vFeed")
            return False
        # aFeed has subindex 5
        ok = self.write_object(index, 5, aFeed.to_bytes(2, 'little'))
        if not ok:
            self.log_info("Error setting aFeed")
            return False
        # all ok, return True
        return True

    def print_position_control_parameters(self):
        """Print position control mode parameters

        Request device for the position control mode parameters
        and prints it.
        """
        pos_mode_parameters, ok = self.read_position_control_parameters()
        if not ok:
            print('[Epos:{0}] Error requesting Position mode control parameters'.format(
                sys._getframe().f_code.co_name))
            return
        print('--------------------------------------------------------------')
        print('Current Position mode control parameters:')
        print('--------------------------------------------------------------')
        for key, value in pos_mode_parameters.items():
            print('{0}: {1}'.format(key, value))
        print('--------------------------------------------------------------')

    def read_following_error(self):
        """Returns the current following error

        Read the current following error value which is the difference
        between actual value and desired value.

        Returns:
            tuple: a tuple containing:

            :following_error: value of actual following error.
            :ok: A boolean if all requests went ok or not.
        """
        index = self.objectIndex['Following Error Actual Value']
        following_error = self.read_object(index, 0x0)
        if not following_error:
            self.log_info("Error getting Following Error Actual Value")
            return None, False
        following_error = int.from_bytes(following_error, 'little', signed=True)
        return following_error, True

    def read_max_following_error(self):
        """Read the Max following error

        Read the max following error value which is the maximum allowed difference
        between actual value and desired value in modulus.

        Returns:
            tuple: a tuple containing:

            :max_following_error: value of max following error.
            :ok: A boolean if all requests went ok or not.
        """
        index = self.objectIndex['Max Following Error']
        max_following_error = self.read_object(index, 0x0)
        if not max_following_error:
            self.log_info("Error getting Max Following Error Value")
            return None, False
        max_following_error = int.from_bytes(max_following_error, 'little')
        return max_following_error, True

    def set_max_following_error(self, max_following_error):
        """Set the Max following error

        The Max Following Error is the maximum permissible difference
        between demanded and actual position at any time of evaluation.
        It serves as a safety and motion-supervising feature.
        If the following error becomes too high, this is a sign of something
        going wrong. Either the drive cannot reach the required speed
        or it is even blocked.

        Args:
            max_following_error: The value of maximum following error.
        Returns:
            bool: A boolean if all requests went ok or not.
        """
        # validate attributes
        if not isinstance(max_following_error, int):
            self.log_info("Error input value must be int")
            return False
        if max_following_error < 0 or max_following_error > 2 ** 32 - 1:
            self.log_info("Error Max Following error out of range")
            return False

        index = self.objectIndex['Max Following Error']
        ok = self.write_object(
            index, 0x0, max_following_error.to_bytes(4, 'little'))
        if not ok:
            self.log_info("Error setting Max Following Error Value")
            return False
        return True

    def read_position_value(self):
        """Read current position value

        Returns:
            tuple: a tuple containing:

            :position: current position in quadrature counts.
            :ok: A boolean if all requests went ok or not.
        """
        index = self.objectIndex['Position Actual Value']
        position = self.read_object(index, 0x0)
        if position is None:
            self.log_info("Failed to read current position value")
            return None, False
        position = int.from_bytes(position, 'little', signed=True)
        return position, True

    def read_position_window(self):
        """Read current position Window value.

        Position window is the modulus threshold value in which the output
        is considered to be achieved.

        Returns:
            tuple: a tuple containing:

            :position_window: current position window in quadrature counts.
            :ok: A boolean if all requests went ok or not.
        """
        index = self.objectIndex['Position Window']
        position_window, ok = self.read_object(index, 0x0)
        if not ok:
            self.log_info("Failed to read current position window")
            return None, False
        return position_window, True

    def set_position_window(self, position_window):
        """Set position Window value

        Position window is the modulus threshold value in which the output
        is considered to be achieved.

        Args:
            position_window: position window in quadrature counts
        Returns:
            bool: A boolean if all requests went ok or not.
        """
        # validate attributes
        if not isinstance(position_window, int):
            self.log_info("Error input value must be int")
            return False
        if position_window < 0 or position_window > 2 ** 32 - 1:
            self.log_info("Error position window out of range")
            return False
        index = self.objectIndex['Position Window']
        ok = self.write_object(index, 0x0, position_window.to_bytes(4, 'little'))
        if not ok:
            self.log_info("Failed to set current position window")
            return None, False
        return True

    def read_position_window_time(self):
        """Read current position Window time value.

        Position window time is the minimum time in milliseconds in which
        the output must be inside the position window for the target is
        considered to have been reached.

        Returns:
            tuple: a tuple containing:

            :position_window_time: current position window time in milliseconds.
            :ok: A boolean if all requests went ok or not.
        """
        index = self.objectIndex['Position Window Time']
        position_window_time, ok = self.read_object(index, 0x0)
        if not ok:
            self.log_info("Failed to read current position window time")
            return None, False
        return position_window_time, True

    def set_position_window_time(self, position_window_time):
        """Set position Window Time value

        Position window time is the minimum time in milliseconds in which
        the output must be inside the position window for the target is
        considered to have been reached.

        Args:
            position_window_time: position window time in milliseconds.
        Returns:
            bool: A boolean if all requests went ok or not.
        """
        # validate attributes
        if not isinstance(position_window_time, int):
            self.log_info("Error input value must be int")
            return False
        if position_window_time < 0 or position_window_time > 2 ** 16 - 1:
            self.log_info("Error position window time out of range")
            return False
        index = self.objectIndex['Position Window Time']
        ok = self.write_object(
            index, 0x0, position_window_time.to_bytes(2, 'little'))
        if not ok:
            self.log_info("Failed to set current position window time")
            return None, False
        return True

    def read_velocity_value(self):
        """Read current velocity value

        Returns:
            tuple: a tuple containing:

            :velocity: current velocity in rpm.
            :ok: A boolean if all requests went ok or not.
        """
        index = self.objectIndex['Velocity Actual Value']
        velocity, ok = self.read_object(index, 0x0)
        if not ok:
            self.log_info("Failed to read current velocity value")
            return None, False
        return velocity, True

    def read_velocity_value_averaged(self):
        """Read current velocity averaged value

        Returns:
            tuple: a tuple containing:

            :velocity: current velocity in rpm.
            :ok: A boolean if all requests went ok or not.
        """
        index = self.objectIndex['Velocity Actual Value Averaged']
        velocity, ok = self.read_object(index, 0x0)
        if not ok:
            self.log_info("Failed to read current velocity averaged value")
            return None, False
        return velocity, True

    def read_current_value(self):
        """Read current value

        Returns:
            tuple: a tuple containing:

            :current: current in mA.
            :ok: A boolean if all requests went ok or not.
        """
        index = self.objectIndex['Current Actual Value']
        current, ok = self.read_object(index, 0x0)
        if not ok:
            self.log_info("Failed to read current value")
            return None, False
        return current, True

    def read_current_value_averaged(self):
        """Read current averaged value

        Returns:
            tuple: a tuple containing:

            :current: current averaged in mA.
            :ok: A boolean if all requests went ok or not.
        """
        index = self.objectIndex['Current Actual Value Averaged']
        current, ok = self.read_object(index, 0x0)
        if not ok:
            self.log_info("Failed to read current averaged value")
            return None, False
        return current, True

    def save_config(self):
        """Save all configurations
        """
        self.node.store()
        return

    def load_config(self):
        """Load all configurations
        """
        self.node.restore()
        return


def main():
    """Test EPOS CANopen communication with some examples.

    Use a few examples to test communication with Epos device using
    a few functions. Also resets the fault error if present.

    Show sample using also the EDS file.
    """

    import argparse
    if sys.version_info < (3, 0):
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

    # instantiate object
    epos = Epos()

    if not (epos.begin(args.nodeID, object_dictionary=args.objDict)):
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
    statusword = epos.read_object(0x6041, 0)
    if not statusword:
        print("[EPOS] Error trying to read EPOS statusword\n")
        return
    else:
        print('----------------------------------------------------------', flush=True)
        print("The statusword is \n Hex={0:#06X} Bin={0:#018b}".format(
            int.from_bytes(statusword, 'little')))

    # test print_statusword and state
    print('----------------------------------------------------------', flush=True)
    print('Testing print of StatusWord and State and ControlWord')
    print('----------------------------------------------------------', flush=True)
    epos.print_state()
    print('----------------------------------------------------------', flush=True)
    epos.print_statusword()
    print('----------------------------------------------------------', flush=True)
    # try to read controlword using hex codes
    controlword = epos.read_object(0x6040, 0)
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
        epos.write_object(0x6040, 0, controlword)
        # check led status to see if it is green and blinking
    epos.print_position_control_parameters()
    epos.print_motor_config()
    epos.print_sensor_config()
    epos.disconnect()
    return


if __name__ == '__main__':
    main()
