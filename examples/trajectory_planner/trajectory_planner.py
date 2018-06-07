import canopen

import argparse
import logging
import sys
import time
import numpy as np
import matplotlib

if (sys.version_info.major == 3):
    matplotlib.use('Qt5Agg')
# disable toolbar
matplotlib.rcParams['toolbar'] = 'None'

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# load epos file from base dir
sys.path.append('../../')
from epos import Epos

figClosed = False

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
        plt.tight_layout()
        # create vectors
        self.tdata = [0]
        self.ref = [0]
        self.out = [0]
        self.diff = [0]
        # create lines to for reference and output values
        self.lineRef = Line2D(self.tdata, self.ref, color=redColor)
        self.lineOut =Line2D(self.tdata, self.out, color=blueColor)
        self.lineDiff = Line2D(self.tdata, self.diff, color=yellowColor)
        self.posAx.add_line(self.lineRef)
        self.posAx.add_line(self.lineOut)
        self.posAx.legend(['Ref', 'Out'], loc='upper right')
        self.posAx.set_ylabel('Position [qc]')
        self.errorAx.add_line(self.lineDiff)
        self.errorAx.set_ylabel('Position [qc]')
        self.errorAx.set_xlabel('Time [s]')


    def update (self, tIn, tOut, yRef, yOut, ref_error):
        self.lineRef.set_xdata(tIn)
        self.lineRef.set_ydata(yRef)
        self.lineOut.set_xdata(tOut)
        self.lineOut.set_ydata(yOut)
        self.lineDiff.set_xdata(tOut)
        self.lineDiff.set_ydata(ref_error)
        # require autoscale?
        self.posAx.set_xlim(tIn[0], tOut[-1])
        self.posAx.set_ylim(min([min(yRef), min(yOut)]), max([max(yRef), max(yOut)]))
        self.errorAx.set_xlim(tOut[0], tOut[-1])
        self.errorAx.set_ylim(min(ref_error), max(ref_error))
        plt.tight_layout()
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

def moveToPosition(pFinal, epos):
    # constants

    # Tmax = 1.7 seems to be the limit before oscillations.

    Tmax = 1.7 # max period for 1 rotation;
    # 1 rev = 3600*4 [qc]
    countsPerRev = 3600*4
    '''
     1Hz = 60rpm = 360degrees/s

     360 degrees = sensor resolution * 4

    this yields: 1Hz = (sensor resolution * 4)/s

    Fmax = 1 / Tmax;

    maxSpeed = 60 rpm/Tmax [rpm]=
             = 360degrees/Tmax [degrees/s]=
             = (sensor resolution *4)/Tmax [qc/s]
    '''
    maxSpeed = countsPerRev/Tmax # degrees per sec

    # max acceleration must be experimental obtained.
    # reduced and fixed.
    maxAcceleration = 6000.0  # [qc]/s^2

    # maximum interval for both the accelleration  and deceleration phase are:
    T1max = 2.0 * maxSpeed/maxAcceleration

    # the max distance covered by these two phase (assuming acceleration equal
    # deceleration) is 2* 1/4 * Amax * T1max^2 = 1/2 * Amax * T1max^2 = 2Vmax^2/Amax
    maxL13 = 2.0 * maxSpeed**2/maxAcceleration

    # max error in quadrature counters
    MAXERROR = 5000

    pStart, OK = epos.readPositionValue()
    if not OK:
        logging.info('({0}) Failed to request current position'.format(
            sys._getframe().f_code.co_name))
        return
    #---------------------------------------------------------------------------
    # Find remaining constants
    #---------------------------------------------------------------------------
    # absolute of displacement
    l = abs(pFinal - pStart)
    if l is 0:
        # already in final point
        return
    # do we need  a constant velocity phase?
    if(l>maxL13):
	    T2 = 2.0*(l- maxL13)/(maxAcceleration*T1max)
	    T1 = T1max
	    T3 = T1max
    else:
	    T1 = np.sqrt(2*l/maxAcceleration)
	    T2 = 0.0
	    T3 = T1

    # time constanst
    t1 = T1
    t2 = T2+t1
    t3 = T3+t2 # final time

    # determine the sign of movement
    moveUp_or_down = np.sign(pFinal-pStart)

    # allocate vars
    inVar = np.array([], dtype='int32')
    outVar = np.array([], dtype='int32')
    tin = np.array([], dtype='int32')
    tout = np.array([], dtype='int32')
    ref_error = np.array([], dtype='int32')


    flag = True
    pi = np.pi
    cos = np.cos
    plotter = Plotter()
    plt.show(block=False)
    time.sleep(0.01)

    t0 = time.monotonic()
    while flag:
        # request current time
        tin = np.append(tin,[time.monotonic()-t0])
        # time to exit?
        if tin[-1] > t3:
            flag = False
            inVar= np.append(inVar, [pFinal])
            epos.setPositionModeSetting(pFinal)
            aux, OK = epos.readPositionValue()
            if not OK:
                logging.info('({0}) Failed to request current position'.format(
                    sys._getframe().f_code.co_name))
                return
            outVar = np.append(outVar, [aux])
            tout = np.append(tout,[time.monotonic()-t0])
            ref_error = np.append(ref_error, [inVar[-1]-outVar[-1]])
            # update plot
            plotter.update(tin, tout, inVar, outVar, ref_error)
        # not finished
        else:
            # get reference position for that time
            if (tin[-1] <= t1):
                aux = pStart + \
                moveUp_or_down * maxAcceleration/2.0 * (T1/(2.0*pi))**2 * \
                (1/2.0 * (2.0* pi/T1 * tin[-1])**2 - (1.0-cos(2.0/T1 * pi * tin[-1])))
            else:
                if (T2 > 0 and tin[-1] > t1 and tin[-1] <= t2):
                    aux  = pStart + \
                    moveUp_or_down * (1/4.0 * maxAcceleration * T1**2 + 1/2.0 * maxAcceleration*T1* (tin[-1]-t1))
                else:
                    aux = pStart + moveUp_or_down * (1/4.0 * maxAcceleration * T1**2\
                     + 1/2.0 * maxAcceleration * T1*T2 + maxAcceleration/2.0 * (T1/(2.0*pi))**2 \
                     * ((2.0*pi)**2 * (tin[-1]-t2)/T1 -1/2.0*(2.0*pi/T1 *(tin[-1]-t2))**2 + (1.0 - cos(2.0*pi/T1*(tin[-1]-t2)))))
            aux = round(aux)
            # append to array and send to device
            inVar = np.append(inVar, [aux])
            OK = epos.setPositionModeSetting(np.int32(inVar[-1]).item())
            if not OK:
                logging.info('({0}) Failed to set target position'.format(
                    sys._getframe().f_code.co_name))
                return
            aux, OK = epos.readPositionValue()
            if not OK:
                logging.info('({0}) Failed to request current position'.format(
                    sys._getframe().f_code.co_name))
                return
            outVar = np.append(outVar, [aux])
            tout = np.append(tout,[time.monotonic()-t0])
            ref_error = np.append(ref_error, [inVar[-1]-outVar[-1]])
            if(abs(ref_error[-1])> MAXERROR):
                epos.changeEposState('shutdown')
                print('Something seems wrong, error is growing to mutch!!!')
                return
        plotter.update(tin, tout, inVar, outVar, ref_error)
        # require sleep?
        #time.sleep(0.001)

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
                        format='[%(asctime)s.%(msecs)03d] [%(name)-20s]: %(levelname)-8s %(message)s',
                        datefmt='%d-%m-%Y %H:%M:%S',
                        filename='epos.log',
                        filemode='w')
    # define a Handler which writes INFO messages or higher
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter('[%(name)-20s] %(message)s')
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
    try:
        while (1):
            x = int(input("Enter desired position [qc]: "))
            print('-----------------------------------------------------------')
            print('Moving to position {0:+16,}'.format(x))
            moveToPosition(x, epos)
            print('done')
            print('-----------------------------------------------------------')
    except KeyboardInterrupt as e:
        print('Got execption {0}\nexiting now'.format(e))

    if not epos.changeEposState('shutdown'):
        logging.info('Failed to change Epos state to shutdown')
        return
    network.disconnect()


if __name__ == '__main__':
    main()