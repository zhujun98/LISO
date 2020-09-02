"""
Distributed under the terms of the GNU General Public License v3.0.

The full license is in the file LICENSE, distributed with this software.

Copyright (C) Jun Zhu. All rights reserved.
"""
import asyncio
from collections import OrderedDict
import functools
import sys
import traceback
from threading import Thread

from .scan_param import ScanParam
from ..io import SimWriter
from ..logging import logger


def run_in_thread(daemon=False):
    """Run a function/method in a thread."""
    def wrap(f):
        @functools.wraps(f)
        def threaded_f(*args, **kwargs):
            t = Thread(target=f, daemon=daemon, args=args, kwargs=kwargs)
            t.start()
            return t
        return threaded_f
    return wrap


class LinacScan(object):
    def __init__(self, linac, *, name=''):
        """Initialization.

        :param Linac linac: Linac instance.
        :param str name: Name of the parameter_scan problem.
        """
        self.name = name

        self._linac = linac

        self._params = OrderedDict()

    def add_param(self, name, *args, **kwargs):
        """Add a parameter for scan.

        :param str name: parameter name.
        """
        if name in self._params:
            raise ValueError(f"Parameter {name} already exists!")

        self._params[name] = ScanParam(name, *args, **kwargs)

    def _generate_param_sequence(self, repeat):
        num = 1
        for param in self._params.values():
            num *= len(param)

        # itertools.product is not used here since we don't want
        # the jitter to repeat.
        ret = []
        for i in range(num*repeat):
            item = []
            for param in self._params.values():
                try:
                    item.append(next(param))
                except StopIteration:
                    param.reset()
                    item.append(next(param))
            ret.append(item)
        return ret

    async def _async_scan(self, n_tasks, output, repeat, n_particles,
                          **kwargs):
        x_map = dict()

        tasks = set()
        sequence = self._generate_param_sequence(repeat)
        n_pulses = len(sequence)
        writer = SimWriter(n_pulses, n_particles, output)
        count = 0
        while True:
            if count < n_pulses:
                for i, k in enumerate(self._params):
                    x_map[k] = sequence[count][i]

                task = asyncio.ensure_future(
                    self._linac.async_run(
                        count, x_map, f'tmp{count:06d}', **kwargs))
                tasks.add(task)

                count += 1

                logger.info(f"Scan {count:06d}: "
                            + str(x_map)[1:-1].replace(': ', ' = '))

            if len(tasks) == 0:
                break

            if len(tasks) >= n_tasks or count == n_pulses:
                done, _ = await asyncio.wait(
                    tasks, return_when=asyncio.FIRST_COMPLETED)

                for task in done:
                    try:
                        idx, output = task.result()
                        writer.write(idx, output)
                    except RuntimeError as e:
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        logger.debug(repr(traceback.format_tb(exc_traceback))
                                     + str(e))
                        logger.warning(f"Scan {count:06d}: " + str(e))
                    except Exception as e:
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        logger.error(
                            f"Scan {count:06d} (Unexpected exceptions): "
                            + repr(traceback.format_tb(exc_traceback))
                            + str(e))
                        raise

                    tasks.remove(task)

    def scan(self, n_tasks=1, *,
             repeat=1, n_particles=2000, output='scan.hdf5', **kwargs):
        """Start a parameter scan.

        :param int n_tasks: maximum number of concurrent tasks.
        :param int repeat: number of repeats of the parameter space. For
            pure jitter study, it is the number of runs since the size
            of variable space is 1.
        :param int n_particles: number of particles to be stored.
        :param str output: output file.
        """
        logger.info(str(self._linac))
        logger.info(self.summarize())

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_scan(
            n_tasks, output,
            repeat=repeat, n_particles=n_particles, **kwargs))

        logger.info(f"Scan finished!")

    def summarize(self):
        text = '\n' + '=' * 80 + '\n'
        text += 'Parameter scan: %s\n' % self.name
        text += self.__str__()
        text += '\n'
        for i, ele in enumerate(self._params.values()):
            if i == 0:
                text += ele.__str__()
            else:
                text += ele.list_item()
        text += '=' * 80 + '\n'
        return text

    def __str__(self):
        text = ''
        return text
