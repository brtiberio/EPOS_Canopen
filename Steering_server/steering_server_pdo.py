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

import logging
import sys
import threading
import time
import numpy as np
from can import CanError

from ..epos import Epos

# import pydevd
# pydevd.settrace('192.168.31.124', port=8000, stdoutToServer=True, stderrToServer=True)

# ----------------------------------------------------------------------------------------------------------------------
# Redefined class for Epos controller to add additional functionality
# ----------------------------------------------------------------------------------------------------------------------


class EposController(Epos):
    maxFollowingError = 7500
    min_value = 0  # type: int
    max_value = 0  # type: int
    zero_ref = 0  # type: int
    calibrated = 0  # type: bool
    QC_TO_DELTA = -7.501E-4  # type: float
    DELTA_TO_QC = 1.0 / QC_TO_DELTA  # type: float
    max_angle = 29  # type: int
    min_angle = -max_angle
    dataDir = "./data/"  # type: str
    current_position = None

    def get_qc_position(self, delta):
        """ Converts angle of wheels to qc

        Given the desired angle of wheels, in degrees of the bicycle model of car,
        convert the requested value to qc position of steering wheel using the
        calibration performed at beginning.

        Args:
            delta: desired angle of wheels in degrees.
        Returns:
            int: a rounded integer with qc position estimated or None if not possible
        """
        if not self.calibrated:
            self.log_info('Device is not yet calibrated')
            return None
        if delta > self.max_angle:
            self.log_info('Angle exceeds limits: max_angle: {0}\t requested: {1}'.format(
                self.max_angle,
                delta))
            return None
        if delta < self.min_angle:
            self.log_info('Angle exceeds limits: min_angle: {0}\t requested: {1}'.format(
                self.min_angle,
                delta))
            return None
        # perform calculations y = mx + b
        val = delta * self.DELTA_TO_QC + self.zero_ref
        val = round(val)
        return int(val)

    def get_delta_angle(self, qc=None):
        """ Converts qc of steering wheel to angle of wheel

        Given the desired qc steering position, convert the requested value to angle of bicycle model in degrees.

        Args:
            qc: an int with desired qc position of steering wheel.
        Returns:
            double: estimated angle of wheels in degrees or None if not possible
        """
        if not self.calibrated:
            self.log_info('Device is not yet calibrated')
            return None
        if qc is None:
            qc = self.current_position
        # perform calculations y = mx + b and solve to x
        delta = (qc - self.zero_ref) * self.QC_TO_DELTA
        return float(delta)

    def start_calibration(self, exit_flag=None):
        """Perform steering wheel calibration

        This function is expected to be run on a thread in order to find the limits
        of the steering wheel position and find the expected value of the zero angle
        of wheels.

        Args:
            exit_flag: threading.Event() to signal the finish of acquisition

        """
        # check if inputs were supplied
        if not exit_flag:
            self.log_info('Error: check arguments supplied')
            return
        state_id = self.check_state()
        # -----------------------------------------------------------------------
        # Confirm epos is in a suitable state for free movement
        # -----------------------------------------------------------------------
        # failed to get state?
        if state_id is -1:
            self.log_info('Error: Unknown state')
            return
        # If epos is not in disable operation at least, motor is expected to be blocked
        if state_id > 4:
            self.log_info('Not a proper operation mode: {0}'.format(
                self.state[state_id]))
            # shutdown
            if not self.change_state('shutdown'):
                self.log_info('Failed to change state to shutdown')
                return
            self.log_info('Successfully changed state to shutdown')

        max_value = 0
        min_value = 0
        num_fails = 0
        # -----------------------------------------------------------------------
        # start requesting for positions of sensor
        # -----------------------------------------------------------------------
        while not exit_flag.isSet():
            current_value, ok = self.read_position_value()
            if not ok:
                self.log_debug('Failed to request current position')
                num_fails = num_fails + 1
            else:
                if current_value > max_value:
                    max_value = current_value
                if current_value < min_value:
                    min_value = current_value
            # sleep?
            time.sleep(0.01)

        self.log_info(
            'Finished calibration routine with {0} fail readings'.format(num_fails))
        self.min_value = min_value
        self.max_value = max_value
        self.zero_ref = round((max_value - min_value) / 2.0 + min_value)
        self.calibrated = True
        self.log_info('MinValue: {0}, MaxValue: {1}, zero_ref: {2}'.format(
            self.min_value, self.max_value, self.zero_ref
        ))
        return

    def move_to_position(self, pos_final, is_angle=False):
        """Move to desired position.

        Plan and apply a motion profile to reduce with low jerk, max speed, max acceleration
        to avoid abrupt variations.
        The function implement the algorithm developed in [1]_

        Args:
            pos_final: desired position.
            is_angle: a boolean, true if pos_final is an angle or false if is qc value
        :return:
            boolean: True if all went as expected or false otherwise

        .. [1] Li, Huaizhong & M Gong, Z & Lin, Wei & Lippa, T. (2007). Motion profile planning for reduced jerk and vibration residuals. 10.13140/2.1.4211.2647.
        """
        # constants
        # t_max = 1.7 seems to be the limit before oscillations.
        t_max = 0.2  # max period for 1 rotation;
        # 1 rev = 3600*4 [qc]
        countsPerRev = 3600 * 4
        #
        # 1Hz = 60rpm = 360degrees/s
        #
        # 360 degrees = sensor resolution * 4
        #
        # this yields: 1Hz = (sensor resolution * 4)/s
        #
        # Fmax = 1 / t_max;
        #
        # max_speed = 60 rpm/t_max [rpm]=
        #          = 360degrees/t_max [degrees/s]=
        #          = (sensor resolution *4)/t_max [qc/s]

        max_speed = countsPerRev / t_max  # degrees per sec

        # max acceleration must be experimental obtained.
        # reduced and fixed.
        max_acceleration = 6000.0  # [qc]/s^2

        # maximum interval for both the acceleration  and deceleration phase are:
        t1_max = 2.0 * max_speed / max_acceleration  # type: float

        # the max distance covered by these two phase (assuming acceleration equal
        # deceleration) is 2* 1/4 * Amax * t1_max^2 = 1/2 * Amax * t1_max^2 = 2Vmax^2/Amax
        max_l13 = 2.0 * max_speed ** 2 / max_acceleration  # type: float

        # max error in quadrature counters
        max_error = 7500
        # num_fails = 0
        # is device calibrated?
        if not self.calibrated:
            self.log_info('Device is not yet calibrated')
            return False
        # is position requested an angle?
        if is_angle:
            pos_final = self.get_qc_position(pos_final)
            # if position can not be calculated, alert user.
            if pos_final is None:
                self.log_info('Failed to calculate position value')
                if not self.change_state('shutdown'):
                    self.log_info('Failed to change Epos state to shutdown')
                return False

        if pos_final > self.max_value or pos_final < self.min_value:
            self.log_info('Final position exceeds physical limits')
            return False

        p_start = self.current_position

        # -----------------------------------------------------------------------
        # get current state of epos and change it if necessary
        # -----------------------------------------------------------------------
        state = self.check_state()
        if state is -1:
            self.log_info('Error: Unknown state')
            return False

        if state is 11:
            # perform fault reset
            ok = self.change_state('fault reset')
            if not ok:
                self.log_info('Error: Failed to change state to fault reset')
                return False

        # shutdown
        if not self.change_state('shutdown'):
            self.log_info('Failed to change Epos state to shutdown')
            return False
        # switch on
        if not self.change_state('switch on'):
            self.log_info('Failed to change Epos state to switch on')
            return False
        if not self.change_state('enable operation'):
            self.log_info('Failed to change Epos state to enable operation')
            return False
        # -----------------------------------------------------------------------
        # Find remaining constants
        # -----------------------------------------------------------------------
        # absolute of displacement
        dist_to_travel = abs(pos_final - p_start)
        if dist_to_travel is 0:
            # already in final point
            return True
        # do we need  a constant velocity phase?
        if dist_to_travel > max_l13:
            t2 = 2.0 * (dist_to_travel - max_l13) / (max_acceleration * t1_max)
            t1 = t1_max
            t3 = t1_max
        else:
            t1 = np.sqrt(2 * dist_to_travel / max_acceleration)
            t2 = 0.0
            t3 = t1

        # time constants
        t1 = t1
        t2 = t2 + t1
        t3 = t3 + t2  # final time

        # allocate vars
        in_var = np.array([], dtype='int32')
        out_var = np.array([], dtype='int32')
        tin = np.array([], dtype='int32')
        tout = np.array([], dtype='int32')
        ref_error = np.array([], dtype='int32')

        # determine the sign of movement
        move_up_or_down = np.sign(pos_final - p_start)
        flag = True
        pi = np.pi
        cos = np.cos
        time.sleep(0.01)
        # choose monotonic for precision
        t0 = time.monotonic()
        num_fails = 0
        while flag and not self.errorDetected:
            # request current time
            tin = np.append(tin, [time.monotonic() - t0])
            # time to exit?
            if tin[-1] > t3:
                flag = False
                in_var = np.append(in_var, [pos_final])
                self.set_position_mode_setting(pos_final)
                # reading a position takes time, as so, it should be enough
                # for it reaches end value since steps are expected to be
                # small
                time.sleep(0.01)
                aux = self.current_position
                out_var = np.append(out_var, [aux])
                tout = np.append(tout, [time.monotonic() - t0])
                ref_error = np.append(ref_error, [in_var[-1] - out_var[-1]])
            # not finished
            else:
                # get reference position for that time
                if tin[-1] <= t1:
                    aux = p_start + \
                          move_up_or_down * max_acceleration / 2.0 * (t1 / (2.0 * pi)) ** 2 * \
                          (1 / 2.0 * (2.0 * pi / t1 *
                                      tin[-1]) ** 2 - (1.0 - cos(2.0 / t1 * pi * tin[-1])))
                else:
                    if (t2 > 0 and tin[-1] > t1 and tin[-1] <= t2):
                        aux = p_start + \
                              move_up_or_down * \
                              (1 / 4.0 * max_acceleration * t1 ** 2 + 1 /
                               2.0 * max_acceleration * t1 * (tin[-1] - t1))
                    else:
                        aux = p_start + \
                              move_up_or_down * (1 / 4.0 * max_acceleration * t1 ** 2
                                                 + 1 / 2.0 * max_acceleration * t1 * t2 +
                                                 max_acceleration / 2.0 *
                                                 (t1 / (2.0 * pi)) ** 2
                                                 * ((2.0 * pi) ** 2 * (tin[-1] - t2) / t1 - 1 / 2.0 * (2.0 * pi / t1
                                                                                                       * (tin[
                                                                                                              -1] - t2)) ** 2 + (
                                                            1.0 - cos(2.0 * pi / t1 * (tin[-1] - t2)))))
                aux = round(aux)
                # append to array and send to device
                in_var = np.append(in_var, [aux])
                ok = self.set_position_mode_setting(np.int32(in_var[-1]).item())
                if not ok:
                    self.log_info('Failed to set target position')
                    num_fails = num_fails + 1
                time.sleep(0.01)
                aux = self.current_position

                out_var = np.append(out_var, [aux])
                tout = np.append(tout, [time.monotonic() - t0])
                ref_error = np.append(ref_error, [in_var[-1] - out_var[-1]])
                if abs(ref_error[-1]) > max_error:
                    self.change_state('shutdown')
                    self.log_info(
                        'Something seems wrong, error is growing to mutch!!!')
                    return False
            # require sleep?
            time.sleep(0.01)
        self.log_info('Finished positioning. Current position {0}'.format(self.current_position))
        return True

    def print_position(self, message):
        """Print velocity value received from PDO

        Args:
            message: message received in PDO
        """
        self.log_debug('{0} received'.format(message.name))
        for var in message:
            self.log_debug('{0} = {1:06X}'.format(var.name, var.raw))
            if var.index == 0x6041:
                pass
            if var.index == 0x6064:
                logging.info('{0:+06.3f} Degrees'.format(self.get_delta_angle(var.raw)))

    def update_position(self, message):
        """Update position value received from PDO

        Args:
            message: message received in PDO
        """
        self.log_debug('{0} received'.format(message.name))
        for var in message:
            # self.log_debug('{0} = {1:06X}'.format(var.name, var.raw))
            if var.index == 0x6064:
                self.current_position = var.raw


def main():
    """Perform steering wheel calibration.

    Ask user to turn the steering wheel to the extremes and finds the max
    """

    import argparse
    if sys.version_info < (3, 0):
        print("Please use python version 3")
        return

    parser = argparse.ArgumentParser(add_help=True,
                                     description='Steering wheel calibration')
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
                        format='[%(asctime)s.%(msecs)03d] [%(name)-12s]: %(levelname)-8s %(message)s',
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

    # event flag to exit
    exit_flag = threading.Event()

    # instantiate object
    epos = EposController()

    # declare threads
    epos_thread = threading.Thread(name="EPOS", target=epos.start_calibration,
                                   args=(exit_flag, ))

    if not (epos.begin(args.nodeID, object_dictionary=args.objDict)):
        logging.info('Failed to begin connection with EPOS device')
        logging.info('Exiting now')
        return

    try:
        epos_thread.start()
        print("Please move steering wheel to extreme positions to calibrate...")
        input("Press Enter when done...")
    except KeyboardInterrupt as e:
        logging.warning('Got exception {0}... exiting now'.format(e))
        return

    exit_flag.set()
    epos_thread.join()
    print("---------------------------------------------")
    print("Max Value: {0}\nMin Value: {1}".format(epos.max_value, epos.min_value))
    print("---------------------------------------------")

    # configure pdo objects.
    if args.objDict is None:
        return
    # --------------------------------------------------------------------------
    # configure pdo objects
    # --------------------------------------------------------------------------
    epos.node.pdo.read()
    epos.node.nmt.state = 'PRE-OPERATIONAL'
    # Do some changes to TxPDO3
    epos.node.pdo.tx[3].clear()
    epos.node.pdo.tx[3].add_variable(0x6041, 0, 16)
    epos.node.pdo.tx[3].add_variable(0x6064, 0, 32)
    epos.node.pdo.tx[3].enabled = True
    # multiple of 100 microseconds
    epos.node.pdo.tx[2].inhibit_time = 10  # 1 millisecond
    epos.node.pdo.tx[3].trans_type = 255
    epos.node.pdo.tx[3].add_callback(epos.update_position)
    epos.node.pdo.tx[3].save()
    # Set back into operational mode
    epos.node.nmt.state = 'OPERATIONAL'
    # TODO change State is failing. to be checked
    time.sleep(0.01)
    epos.change_state('shutdown')

    print("Ctrl+C to exit... ")
    while True:
        try:
            # run it free to test update
            epos.log_info("current_position: {0:+06.2f}".format(epos.get_delta_angle()))
            time.sleep(0.01)
            # angle = float(input('Set your position...'))
            # print('Setting angle to {0}'.format(angle))
            # epos.move_to_position(angle, is_angle=True)
            # time.sleep(3)
        except CanError:
            print("Message NOT sent")
            break
        except ValueError:
            print("Invalid value")
        except KeyboardInterrupt as e:
            print('Got {0}\nexiting now'.format(e))
            break
        finally:
            pass

    epos.node.nmt.state = 'PRE-OPERATIONAL'
    epos.change_state('shutdown')
    return


if __name__ == '__main__':
    main()
