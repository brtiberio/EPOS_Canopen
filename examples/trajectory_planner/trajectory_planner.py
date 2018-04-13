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
        # create axis
        self.posAx  = self.fig.add_subplot(2, 1, 1)
        self.errorAx = self.fig.add_subplot(2, 1, 2)
        plt.tight_layout
        # create vectors
        self.tdata = [0]
        self.ref = [0]
        self.out = [0]
        self.diff = [0]
        # create lines to for reference and output values
        self.lineRef = Line2D(self.tdata, self.ref, color=redColor)
        self.lineOut =Line2D(self.tdata, self.out, color=blueColor)
        self.posAx.add_line(self.lineRef)
        self.posAx.add_line(self.lineOut)
        self.posAx.legend(['Ref', 'Out'], loc='upper right')
        self.posAx.set_ylabel('Position [qc]')
        self.posAx.set_xlabel('Time [s]')


    def update (self, XData, yRef, yOut):
        self.lineRef.set_xdata(XData)
        self.lineRef.set_ydata(yRef)
        self.lineOut.set_xdata(XData)
        self.lineOut.set_ydata(yOut)
        # require autoscale?

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
    T1max = 2 * maxSpeed/maxAcceleration

    # the max distance covered by these two phase (assuming acceleration equal
    # deceleration) is 2* 1/4 * Amax * T1max^2 = 1/2 * Amax * T1max^2 = 2Vmax^2/Amax
    maxL13 = 2* maxSpeed^2/maxAcceleration

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
    moveUp_or_down = pFinal-pStart > 0

    # figure()
    # # plot for inVar;
    # h1 = plot(0,y0)
    # xlabel('Time[s]')
    # ylabel('Position[qc]')
    # title('Position Follow test')
    # ylim(1.1*sort([y0 yf]))
    # hold on
    # # plot for outVar
    # h2 = plot(0,y0,'g')

    # allocate vars
    inVar = np.array([])
    outVar = np.array([])
    tin = np.array([])
    tout = np.array([])
    ref_error = np.array([])

    t0 = time.monotonic()
    flag = True

    pi = np.pi
    cos = np.cos

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
            # append to array and send to device
            inVar = np.append(inVar, [aux])
            OK = epos.setPositionModeSetting(inVar[-1])
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
        # update plot
        # h1.XData = tin;
	    # h1.YData = inVar;
	    # h2.XData = tout;
	    # h2.YData = outVar;
	    # drawnow limitrate nocallbacks;
        # to be done
    # end of while loop
    # axis auto
    # legend('reference','output')
    # drawnow
    OK = epos.changeEposState('shutdown')
    if not OK:
        logging.info('({0}) Failed to shutdown Epos device'.format(
            sys._getframe().f_code.co_name))
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

    network.disconnect()


if __name__ == '__main__':
    main()