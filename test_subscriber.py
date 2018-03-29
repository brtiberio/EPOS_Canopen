
import canopen
from epos import Epos
import argparse
import logging
import sys
from time import sleep

def gotMessage(EmcyError):
    logging.info('[{0}] Got an EMCY message: {1}'.format(sys._getframe().f_code.co_name, EmcyError))
    return

def main():
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

    network = canopen.Network()
    epos = Epos(_network=network)
    if not (epos.begin(args.nodeID, objectDictionary=args.objDict)):
        logging.info('Failed to begin connection with EPOS device')
        logging.info('Exiting now')
        return

    # are there pdo active?
    epos.node.pdo.read()
    logging.info(vars(epos.node.pdo.rx))
    logging.info(vars(epos.node.pdo.rx))
    epos.node.emcy.add_callback(gotMessage)
    try:
        while (1):
            sleep(0.01)
    except KeyboardInterrupt as e:
        print('Got execption {0}\nexiting now'.format(e))
    finally:
        return


if __name__ == '__main__':
    main()