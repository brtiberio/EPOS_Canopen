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
from time import sleep
import queue

sys.path.append('../')
from epos import Epos


def start_calibration(results=None, epos=None, exit_flag=None, debug=False):
    """
    To be done
    """
    logger = logging.getLogger('CALIBRATION')
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    # check if inputs were supplied
    if not epos or not exit_flag or not results:
        logger.info('[{0}] Error: check arguments supplied\n'.format(
            sys._getframe().f_code.co_name))
        return

    max_value = 0
    min_value = 0
    # start requesting for positions of sensor

    while (exit_flag.isSet() == False):
        currentValue, OK = epos.read_position_value()
        if not OK:
            logging.info('({0}) Failed to request current position'.format(
                sys._getframe().f_code.co_name))
            min_value = None
            max_value = None
            return
        if currentValue > max_value:
            max_value = currentValue
        if currentValue < min_value:
            min_value = currentValue
        # sleep?
        sleep(0.005)

    logging.info('({0}) Finishing calibration routine'.format(
        sys._getframe().f_code.co_name))
    results.put({'min_value': min_value, 'max_value': max_value})
    return


def emcy_error_print(emcy_error):
    """Print any EMCY Error Received on CAN BUS
    """
    logging.info('[{0}] Got an EMCY message: {1}'.format(
        sys._getframe().f_code.co_name, emcy_error))
    return


def main():
    """Perform steering wheel calibration.

    Ask user to turn the steering wheel to the extremes and finds the max
    """

    import argparse
    if (sys.version_info < (3, 0)):
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
    epos = Epos()

    min_value = 0
    max_value = 0
    results_queue = queue.Queue()
    # declare threads
    epos_thread = threading.Thread(name="EPOS", target=start_calibration,
                                   args=(results_queue, epos, exit_flag))

    if not (epos.begin(args.nodeID, object_dictionary=args.objDict)):
        logging.info('Failed to begin connection with EPOS device')
        logging.info('Exiting now')
        return
    # emcy messages handles
    epos.node.emcy.add_callback(emcy_error_print)

    try:
        epos_thread.start()
        print("Please move steering wheel to extreme positions to calibrate...")
        input("Press Enter when done...")
    except KeyboardInterrupt as e:
        logging.warning('Got exception {0}... exiting now'.format(e))
        return

    exit_flag.set()
    epos_thread.join()
    try:
        ret_vals = results_queue.get(timeout=30)
    except queue.Empty:
        logging.info("Queue response timeout")
        return
    if ret_vals is None:
        logging.info("Failed to perform calibration")
        return
    max_value = ret_vals['max_value']
    min_value = ret_vals['min_value']
    print("---------------------------------------------")
    print("Max Value: {0}\nMin Value: {1}".format(max_value, min_value))
    print("---------------------------------------------")
    return


if __name__ == '__main__':
    main()
