import matplotlib
import numpy as np
from math import sqrt

def setup(width=10, height=5, params={}):
    print("In Setup")
    # see http://matplotlib.org/users/customizing.html for more options
    rc = {'backend': 'ps',
          'text.usetex': True,
          #'axes.usetex': True,
          'text.latex.preamble': ['\\usepackage{gensymb}'],
          'axes.labelsize': 10, # fontsize for x and y labels (was 10)
          'axes.titlesize': 10,
          'font.size': 10, # was 10
          'legend.fontsize': 10, # was 10
          'xtick.labelsize': 10,
          'ytick.labelsize': 10,
          'figure.figsize': [width,height],
          'font.family': 'serif',
          'figure.subplot.top': 0.95,
          'figure.subplot.left': 0.17,
          'figure.subplot.right': 0.95,
          'figure.subplot.bottom': 0.2,
          'savefig.dpi': 300
    }
    rc.update(params)

    matplotlib.rcParams.update(rc)

def get_figsize(width, height, span):
    if span:
        fig_width = 529.22128 / 72 # IEEE text width
    else:
        fig_width = 258.61064 / 72# IEEE column width
    if not height:
        golden_mean = (sqrt(5)-1.0)/2.0    # Aesthetic ratio
        fig_height = (258.61064 / 72)*golden_mean # height in inches
        fig_height = fig_height * 0.9
    else:
        fig_height = height
    fig_width = fig_width * width
    return fig_width, fig_height

def setup3(width=1, *, height=None, span=False, l=0.15, r=0.98, t=0.98, b=0.17, params={}):

    figsize = get_figsize(width, height, span)
  # see http://matplotlib.org/users/customizing.html for more options

    rc = {'backend': 'ps',
              'text.usetex': True,
              'text.latex.preamble': ['\\usepackage{gensymb}'],
              'axes.labelsize': 8, # fontsize for x and y labels (was 10)
              'axes.titlesize': 8,
              'font.size': 8, # was 10
              'legend.fontsize': 7, # was 10
              'xtick.labelsize': 8,
              'ytick.labelsize': 8,
              'figure.figsize': figsize,
              'font.family': 'serif',
              'figure.subplot.left': l,
              'figure.subplot.right': r,
              'figure.subplot.bottom': b,
              'figure.subplot.top': t,
              'savefig.dpi': 300,
              'lines.linewidth': 1,
              'errorbar.capsize': 2,
    }

    rc.update(params)
    matplotlib.rcParams.update(rc)
'''
def setup3(width=20, height=35, params={}):
    print("In Setup")
    # see http://matplotlib.org/users/customizing.html for more options
    rc = {'backend': 'ps',
          'text.usetex': True,
          #'axes.usetex': True,
          'text.latex.preamble': ['\\usepackage{gensymb}'],
          'axes.labelsize': 10, # fontsize for x and y labels (was 10)
          'axes.titlesize': 10,
          'font.size': 10, # was 10
          'legend.fontsize': 10, # was 10
          'legend.handlelength': 4,
          'xtick.labelsize': 10,
          'ytick.labelsize': 10,
          'figure.figsize': [width,height],
          'font.family': 'serif',
          'figure.subplot.top': 0.95,
          'figure.subplot.left': 0.05,
          'figure.subplot.right': 0.95,
          'figure.subplot.bottom': 0.05,
          'savefig.dpi': 300
    }
    rc.update(params)
    matplotlib.rcParams.update(rc)
'''
def get_color(coderate):
    coderate = (coderate - 0.5) * 480
    return matplotlib.colors.hsv_to_rgb(np.array([coderate, 0.9, 0.9]))


def format_axes(ax, y, x='RSS'):
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)

    for spine in ['left', 'bottom']:
        ax.spines[spine].set_color('gray')
        ax.spines[spine].set_linewidth(0.5)

    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    for axis in [ax.xaxis, ax.yaxis]:
        axis.set_tick_params(direction='out', color='gray')

    if x == 'RSS':
        if standard == '11n-24GHz':
            # ax.set_xticks(np.arange(-100, -83 + 1, 2))
            # ax.set_xticks(np.arange(-100, -83 + 1, 1), minor=True)
            # ax.set_xlim(-100,-83)

            # close settings
            ax.set_xticks(np.arange(-99, -97 + 0.5, 0.5))
            ax.set_xticks(np.arange(-99, -97 + 0.1, 0.1), minor=True)
            ax.set_xlim(-98.6, -97)

        if standard == '11n-5GHz':
            ax.set_xticks(np.arange(-96, -92 + 0.5, 0.5))
            ax.set_xticks(np.arange(-96, -92 + 0.1, 0.1), minor=True)
            ax.set_xlim(-95.6, -92.4)

        ax.set_xlabel(r'RSS [dBm]')

    if x == 'packets':
        ax.set_xticks(np.arange(0, 11000, 2000))
        ax.set_xticks(np.arange(0, 11000, 500), minor=True)
        ax.set_xlabel(r'Packet number')

    if x == 'code rate':
        ax.set_xticks(np.arange(0.5, 1 + 0.1, 0.1))
        ax.set_xlabel(r'Code rate $R$')
        ax.set_xlim(0.45, 1.05)

    if y == 'loss':
        ax.set_yticks(np.arange(0, 1 + 0.2, 0.2))
        ax.set_yticks(np.arange(0, 1 + 0.1, 0.1), minor=True)
        ax.set_ylim(-0.05, 1.05)
        ax.set_ylabel(r'Packet loss probability')

    if y == 'losses':
        ax.set_yticks(np.arange(0, 0.05 + 0.01, 0.01))
        ax.set_ylim(-0.005, 0.055)
        ax.set_ylabel(r'Packet loss probability')

    if y == 'delay':
        ax.set_yscale('log')
        ax.set_ylabel(r'Delay [$\mu$s]')

    if y == 'time':
        # ax.set_yscale('log')
        ax.set_ylabel('Simulation time [$\mu$s]')

    return ax