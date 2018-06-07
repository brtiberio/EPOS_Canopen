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

import csv

fileName = 'table2.csv'
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
        self.lineOut =Line2D(self.tdata, self.out, color=redColor, linestyle='None', marker='o')
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

plotter.begin(data['time'], data['position'])
out = np.array([], dtype='int32')
diff = np.array([], dtype='int32')
t = np.array([])


I = 0
maxI = len(data['time'])
exitFlag = False
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
            outi = data['position'][I]
            out=np.append(out, outi + np.random.randint(-100, 100))
            diff = np.append(diff,out[-1]-outi)
            t = np.append(t, data['time'][I])
            # update only every n steps
            if (I % nSteps == 0) or (I == 0):
                plotter.update(t, out, diff, True)
            else:
                plotter.update(t, out, diff)
            # simulate variable slow process
            randSleep = 0.01*np.random.randint(0, 20)
            print('Current frame: {0}\t sleeping:{1}'.format(I, randSleep))
            time.sleep(randSleep)

print(time.monotonic()-t0)
plotter.update(t, out, diff, True)
while( not figClosed):
    time.sleep(0.01)
    plotter.fig.canvas.flush_events()



