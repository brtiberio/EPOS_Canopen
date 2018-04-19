import argparse
import logging
import sys
import time
import numpy as np
import matplotlib
import canopen

if (sys.version_info.major == 3):
    matplotlib.use('Qt5Agg')
# disable toolbar
matplotlib.rcParams['toolbar'] = 'None'

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# load epos file from base dir
sys.path.append('../../')
from epos import Epos
import csv

figClosed = False
# nSteps represent the number of points to skip before updating figure
nSteps = 10
# colors similar to matlab
blueColor = (0, 0.4470, 0.7410)
redColor = (0.8500, 0.3250, 0.0980)
yellowColor = (0.9290, 0.6940, 0.1250)

class Plotter():
    def __init__(self):
        # create new figure or use last
        self.fig = plt.figure(1)
        self.fig.clf()
        # create axis
        self.posAx  = self.fig.add_subplot(2, 1, 1)
        self.errorAx = self.fig.add_subplot(2, 1, 2)
        # create vectors
        self.tRef = [0]
        self.tdata = [0]
        self.yRef = [0]
        self.out = [0]
        self.diff = [0]
        # create lines to for reference and output values
        self.lineRef = Line2D(self.tRef, self.yRef, color=blueColor)
        self.lineOut =Line2D(self.tdata, self.out, color=redColor, linestyle='None', marker='o', markersize=1)
        self.lineDiff = Line2D(self.tdata, self.diff, color=yellowColor)
        self.posAx.add_line(self.lineRef)
        self.posAx.add_line(self.lineOut)
        self.posAx.legend(['Ref', 'Out'], loc='upper right')
        self.posAx.set_ylabel('Position [qc]')
        self.errorAx.add_line(self.lineDiff)
        self.errorAx.set_ylabel('Position [qc]')
        self.errorAx.set_xlabel('Time [s]')
        self.errorAx.legend(['error'], loc='upper right')



    def begin(self, tRef, yRef):
        self.tRef = tRef
        self.yRef = yRef
        self.lineRef.set_xdata(np.array(tRef))
        self.lineRef.set_ydata(np.array(yRef))
        self.posAx.set_xlim(tRef[0], tRef[-1])
        self.errorAx.set_xlim(tRef[0], tRef[-1])
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()


    def update (self, tOut, yOut, ref_error, draw= False):
        self.lineOut.set_xdata(tOut)
        self.lineOut.set_ydata(yOut)
        self.lineDiff.set_xdata(tOut)
        self.lineDiff.set_ydata(ref_error)
        # require autoscale?
        if tOut[-1] > self.tRef[-1]:
            self.posAx.set_xlim(self.tRef[0], tOut[-1])
            self.errorAx.set_xlim(self.tRef[0], tOut[-1])
        self.posAx.set_ylim(min([min(self.yRef), min(yOut)]), max([max(self.yRef), max(yOut)]))
        self.errorAx.set_ylim(min(ref_error), max(ref_error))
        if draw:
            self.fig.canvas.draw()
            plt.tight_layout()
        self.fig.canvas.flush_events()

def handle_close(evt):
    global figClosed
    print('Closed figure!')
    figClosed = True
    return

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
    parser.add_argument('--file', '-f', action='store', default='table1.csv',
                        type=str, help='csv file name to be used', dest='file')
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
    formatter = logging.Formatter('[%(name)-12s] %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)
    # instanciate object

    network = canopen.Network()
    network.connect(channel=args.channel, bustype=args.bus)

    epos = Epos(_network=network)
    if not (epos.begin(args.nodeID, objectDictionary=args.objDict)):
        logging.info('Failed to begin connection with EPOS device')
        logging.info('Exiting now')
        return

    # emcy messages handles
    epos.node.emcy.add_callback(gotMessage)

    # get current state of epos
    state = epos.checkEposState()
    if state is -1:
        logging.info('[Epos:{0}] Error: Unknown state\n'.format(sys._getframe().f_code.co_name))
        return

    if state is 11:
        # perform fault reset
        ok = epos.changeEposState('fault reset')
        if not ok:
            logging.info('[Epos:{0}] Error: Failed to change state to fault reset\n'.format(sys._getframe().f_code.co_name))
            return

    # shutdown
    if not epos.changeEposState('shutdown'):
	    logging.info('Failed to change Epos state to shutdown')
	    return
    # switch on
    if not epos.changeEposState('switch on'):
	    logging.info('Failed to change Epos state to switch on')
	    return
    if not epos.changeEposState('enable operation'):
	    logging.info('Failed to change Epos state to enable operation')
	    return

    # load datafile
    fileName = args.file
    with open(fileName) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        data = {}
        for row in reader:
            for header, value in row.items():
                try:
                    data[header].append(int(value))
                except KeyError:
                    data[header] = [value]
                except ValueError:
                    data[header].append(float(value))

    plotter = Plotter()
    time.sleep(0.01)
    plotter.fig.canvas.mpl_connect('close_event', handle_close)
    plt.show(block=False)
    time.sleep(0.01)
    try:
        data['time'][0] = int(data['time'][0])
    except ValueError:
        data['time'][0] = float(data['time'][0])
    data['position'][0] = int(data['position'][0])
    # plot loaded reference
    plotter.begin(data['time'], data['position'])

    out = np.array([], dtype='int32')
    diff = np.array([], dtype='int32')
    t = np.array([])
    I = 0
    maxI = len(data['time'])
    updateFlag = False
    # get current time
    t0 = time.monotonic()
    while( I < maxI):
        tOut = time.monotonic()-t0
        # skip to next step?
        if tOut > data['time'][I]:
            I += 1
            updateFlag = True
        else:
            # send data only once
            if (updateFlag):
                updateFlag = False
                # get new reference position.
                epos.setPositionModeSetting(data['position'][I])
            else:
                # if not time to update new ref, request current position
                aux, OK = epos.readPositionValue()
                if not OK:
                    logging.info('({0}) Failed to request current position'.format(
                        sys._getframe().f_code.co_name))
                    return
                out=np.append(out, aux)
                diff = np.append(diff,data['position'][I]-out[-1])
                t = np.append(t, time.monotonic()-t0)
                # update only every n steps
                if (I % nSteps == 0) or (I == 0):
                    plotter.update(t, out, diff, True)
                else:
                    plotter.update(t, out, diff)
                # use sleep?
                time.sleep(0.005)

    print('Time to process all vars was {0} seconds'.format(time.monotonic()-t0))
    # request one last time
    aux, OK = epos.readPositionValue()
    if not OK:
        logging.info('({0}) Failed to request current position'.format(
            sys._getframe().f_code.co_name))
        return
    out=np.append(out, aux)
    diff = np.append(diff,data['position'][I-1]-out[-1])
    t = np.append(t, time.monotonic()-t0)
    plotter.update(t, out, diff, True)
    if not epos.changeEposState('shutdown'):
        logging.info('Failed to change Epos state to shutdown')
        return
    print('Close figure to exit')
    while( not figClosed):
        time.sleep(0.01)
        plotter.fig.canvas.flush_events()
        

if __name__ == '__main__':
    main()