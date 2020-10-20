import matplotlib
import numpy as np

def setup(width=10, height=5, params={}):
    print("In Setup")
    # see http://matplotlib.org/users/customizing.html for more options
    rc = {'backend': 'ps',
          'text.usetex': True,
          #'axes.usetex': True,
          'text.latex.preamble': ['\\usepackage{gensymb}'],
          'axes.labelsize': 16, # fontsize for x and y labels (was 10)
          'axes.titlesize': 16,
          'font.size': 16, # was 10
          'legend.fontsize': 16, # was 10
          'xtick.labelsize': 16,
          'ytick.labelsize': 16,
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

def setup3(width=20, height=35, params={}):
    print("In Setup")
    # see http://matplotlib.org/users/customizing.html for more options
    rc = {'backend': 'ps',
          'text.usetex': True,
          #'axes.usetex': True,
          #'text.latex.preamble': ['\\usepackage{gensymb}'],
          'axes.labelsize': 14, # fontsize for x and y labels (was 10)
          'axes.titlesize': 14,
          'font.size': 20, # was 10
          'legend.fontsize': 14, # was 10
          #'legend.handlelength': 4,
          #'xtick.labelsize': 30,
          #'ytick.labelsize': 18,
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