#!/usr/bin/python
"""
Classes for plotting parameters' evolution from different codes.

Author: Jun Zhu

"""
import os
from abc import abstractmethod

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from ..data_processing import parse_astra_line
from ..data_processing import parse_impactt_line
from ..data_processing import parse_impactz_line
from ..data_processing import parse_genesis_line
from .vis_utils import get_default_unit
from .vis_utils import get_unit_scale
from .vis_utils import get_label

LABEL_FONT_SIZE = 26
TITLE_FONT_SIZE = 18
TICK_FONT_SIZE = 20
LEGEND_FONT_SIZE = 18
LABEL_PAD = 8
TICK_PAD = 8
MAX_LOCATOR = 7
AX_MARGIN = 0.05


class LinePlot(object):
    """Inherit from BeamEvolution object"""
    def __init__(self, rootname, **args):
        """Initialization.

        :param rootname: string
            Root name (including path) of the files.
        """
        self.rootname = rootname

        self.data = self._load_data()
        self._options = self.data.columns.values

    def save_plot(self, var1, var2=None, **kwargs):
        kwargs['save_image'] = True
        self._plot(var1, var2, **kwargs)

    def plot(self, var1, var2=None, **kwargs):
        kwargs['save_image'] = False
        self._plot(var1, var2, **kwargs)

    def _plot(self, var1, var2, *,
             x_unit=None,
             y_unit=None,
             xlim=None,
             ylim=None,
             save_image=False,
             filename='',
             dpi=300):
        """Plot parameters' evolution along the beamline.

        :param var1: string
            Variable name.
        :param var2: string
            Variable name (optional).
        :param x_unit: string
            Units of y1 axis.
        :param y_unit: string
            Units of y1 axis.
        :param x_unit: string
            Unit for x axis.
        :param y_unit: string
            Unit for y axis.
        :param xlim: tuple, (x_min, x_max)
            Range of the x axis.
        :param ylim: tuple, (y_min, y_max)
            Range of the y axis.
        :param save_image: bool
            Save image to file. Default = False.
        :param filename: string
            Filename of the output file. Default = ''.
            The file will be saved in the same directory as the particle file.
        :param dpi: int
            DPI of the plot. Default = 300.
        """
        if var1 not in self._options or \
                (var2 is not None and var2 not in self._options):
            raise ValueError("Valid options are: {}".format(self._options))

        x_unit = get_default_unit('z') if x_unit is None else x_unit
        # var2 should have the same unit
        y_unit = get_default_unit(var1) if y_unit is None else y_unit

        x_unit_label, x_scale = get_unit_scale(x_unit)
        y_unit_label, y_scale = get_unit_scale(y_unit)

        _, ax = plt.subplots(figsize=(8, 5))
        ax.margins(AX_MARGIN)
        ax.xaxis.set_major_locator(ticker.MaxNLocator(MAX_LOCATOR,
                                                      symmetric=False))
        ax.yaxis.set_major_locator(ticker.MaxNLocator(MAX_LOCATOR,
                                                      symmetric=False))

        colors = ['dodgerblue', 'firebrick']
        styles = ['-', '--']
        vars = [var1, var2]
        for i, var in enumerate(vars):
            if var is not None:
                ax.plot(self.data['z']*x_scale, self.data[var]*y_scale,
                        c=colors[i], ls=styles[i], lw=2, label=get_label(var))

        ax.set_xlabel("$z$ " + x_unit_label,
                      fontsize=LABEL_FONT_SIZE, labelpad=LABEL_PAD)
        ax.set_ylabel("$,$ ".join([get_label(var) for var in vars if var is not None])
                      + " " + y_unit_label, fontsize=LABEL_FONT_SIZE, labelpad=LABEL_PAD)

        ax.tick_params(labelsize=TICK_FONT_SIZE, pad=TICK_PAD)

        ax.set_xlim(xlim)
        ax.set_ylim(ylim)

        if var2 is not None:
            plt.legend(loc=0, fontsize=LEGEND_FONT_SIZE)

        plt.tight_layout()

        if save_image is True:
            if not filename:
                filename = self.rootname + '_' + var1
                if var2 is None:
                    filename += '.png'
                else:
                    filename += '-' + var2 + '.png'
            else:
                filename = os.path.join(os.path.dirname(self.rootname), filename)
            plt.savefig(filename, dpi=dpi)
            print('%s saved!' % os.path.abspath(filename))
        else:
            plt.show()

    @abstractmethod
    def _load_data(self):
        raise NotImplemented


class AstraLinePlot(LinePlot):
    """Plot the parameter evolution along the ASTRA beamline.."""
    def __init__(self, rootname, **kwargs):
        """Initialization."""
        super().__init__(rootname, **kwargs)

    def _load_data(self):
        """Read data from file."""
        return parse_astra_line(self.rootname)


class ImpacttLinePlot(LinePlot):
    """Plot the parameter evolution along the IMPACT-T beamline.."""
    def __init__(self, rootname, **kwargs):
        """Initialization."""
        super().__init__(rootname, **kwargs)

    def _load_data(self):
        """Read data from file."""
        return parse_impactt_line(self.rootname)