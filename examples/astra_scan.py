"""
This is a basic example showing how to study parameter_scan.
"""
import numpy as np

from liso import Linac, LinacScan
from liso.logging import logger
logger.setLevel('DEBUG')


linac = Linac()  # instantiate a Linac

linac.add_beamline('astra',
                   name='gun',
                   swd='astra_injector',
                   fin='injector.in',
                   template='astra_scan/injector.in.000',
                   pout='injector.0450.001')

sc = LinacScan(linac)  # instantiate a Jitter (problem)

sc.add_param('gun_gradient', values=np.linspace(130 - 10, 130 + 10, 5))
sc.add_param('gun_phase', values=np.linspace(-15, 5, 5))
sc.add_param('tws_gradient', values=np.linspace(30 - 5, 30 + 5, 5))
sc.add_param('tws_phase', values=np.linspace(-90, -60, 10))

sc.scan(n_tasks=12)