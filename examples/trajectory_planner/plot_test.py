import numpy as np
import sys
import time

import matplotlib
if (sys.version_info.major == 3):
    matplotlib.use('Qt5Agg')
# disable toolbar
matplotlib.rcParams['toolbar'] = 'None'

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.animation as animation


# colors similar to matlab
blueColor = (0, 0.4470, 0.7410)
redColor = (0.8500, 0.3250, 0.0980)
yellowColor = (0.9290, 0.6940, 0.1250)
figClosed = False

class Scope(object):
    def __init__(self, ax, maxt=2, dt=0.02):
        self.ax = ax
        self.dt = dt
        self.maxt = maxt
        self.tdata = [0]
        self.ydata = [0]
        self.ydata2 = [0]
        self.line = Line2D(self.tdata, self.ydata, color=redColor)
        self.line2 =Line2D(self.tdata, 2*self.ydata, color=blueColor)
        self.ax.add_line(self.line)
        self.ax.add_line(self.line2)
        self.ax.set_ylim(-.1, 2.1)
        self.ax.set_xlim(0, self.maxt)
        self.ax.legend(['Ref', 'Out'], loc='upper right')
        self.ax.set_ylabel('value')
        self.ax.set_xlabel('Time')

    def update(self, y):
        lastt = self.tdata[-1]
        # if lastt > self.tdata[0] + self.maxt:  # reset the arrays
        #     self.tdata = [self.tdata[-1]]
        #     self.ydata = [self.ydata[-1]]
        #     self.ydata2 = [self.ydata2[-1]]
        #     self.ax.set_xlim(self.tdata[0], self.tdata[0] + self.maxt)

        t = self.tdata[-1] + self.dt
        self.tdata.append(t)
        self.ydata.append(y)
        self.ydata2.append(2*y)
        self.line.set_data(self.tdata, self.ydata)
        self.line2.set_data(self.tdata, self.ydata2)
        self.ax.set_xlim(self.tdata[0], self.tdata[-1])
        self.ax.set_ylim(min([min(self.ydata), min(self.ydata2)]), max([max(self.ydata), max(self.ydata2)]))



def emitter(p=0.03):
    'return a random value with probability p, else 0'
    while True:
        v = np.random.rand(1)
        if v > p:
            yield 0.
        else:
            yield np.random.rand(1)

def handle_close(evt):
    global figClosed
    print('Closed figure!')
    figClosed = True
    return

# Fixing random state for reproducibility
np.random.seed(19680801)


fig, ax = plt.subplots()
scope = Scope(ax)
fig.canvas.mpl_connect('close_event', handle_close)
plt.show(block=False)

while( not figClosed):
    scope.update(np.random.rand(1))
    fig.canvas.draw()
    fig.canvas.flush_events()
    time.sleep(0.01)

print('Exiting')