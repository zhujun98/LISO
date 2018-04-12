#!/usr/bin/python
"""
This is a basic example showing how to optimize the emittance in ASTRA
with a local search optimizer.

The solution of running the following code is 
    emitx_um    = 0.3195 
at
    laser_spot  = 0.1189
    main_sole_b = 0.2187


Author: Jun Zhu
"""
from liso import Linac, LinacOptimization, NelderMead


# set up a linac
linac = Linac()

# add a beamline
#
# The first argument is the code name
# name: beamline name
# fin: simulation input file path
# template: simulation input template file path.
# pout: output file name. It is assumed and must be in the same folder as 'fin'.
linac.add_beamline('astra',
                   name='gun',
                   fin='astra_injector/injector.in',
                   template='astra_basic/injector.in.000',
                   pout='injector.0450.001')

print(linac)

# set the optimizer
optimizer = NelderMead()

# set an optimization problem
opt = LinacOptimization(linac)

# There are two options to access a parameter of a linac:
# 1. Use a string: the string must have the form
#        beamline_name.WatchParameters_name.param_name
#        or
#        beamline_name.LineParameters_name.param_name.
# 2. Use a function object: the function has only one argument which is the linac instance.

# objective: its value is the horizontal emittance at the end of the 'gun' beamline.
opt.add_obj('emitx_um', expr='gun.out.emitx', scale=1e6)

# variables with lower boundary (lb) and upper boundary (ub)
opt.add_var('laser_spot',  value=0.10, lb=0.04, ub=0.3)
opt.add_var('main_sole_b', value=0.20, lb=0.00, ub=0.4)

opt.workers = 12  # use parallel Astra
opt.printout = 1  # print the optimization process
opt.solve(optimizer)  # run the optimization

