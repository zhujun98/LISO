#!/usr/bin/env python
"""
Variable class

Author: Jun Zhu
"""
from ..config import Config

INF = Config.INF


class Variable(object):
    """Optimization Variable Class"""
    def __init__(self, name, type_='c', *, value=0.0, **kwargs):
        """Variable Class Initialization

        :param name: string
            Variable Name.
        :param type_: string
            Variable type
            ('c' - continuous, 'i' - integer, 'd' - discrete), default = 'c'
        :param value: int / float
            Variable Value, default = 0.0
        :param lower: int / float
            Variable lower value.
        :param upper: int / float
            Variable upper value.
        """
        self.name = name
        self.type_ = type_[0].lower()
        if self.type_ == 'c':
            self.value = float(value)
            self.lower = -INF
            self.upper = INF
            for key in kwargs.keys():
                if key.lower() == 'lower':
                    self.lower = float(kwargs[key])
                if key.lower() == 'upper':
                    self.upper = float(kwargs[key])

        elif type_[0].lower() == 'i':
            self.value = int(value)
            self.lower = None
            self.upper = None
            for key in kwargs.keys():
                if key.lower() == 'lower':
                    self.lower = int(kwargs[key])

                if key.lower() == 'upper':
                    self.upper = int(kwargs[key])

            if self.lower is None or self.upper is None:
                raise ValueError('An integer variable requires both '
                                 'lower and upper boundaries')

        elif type_[0].lower() == 'd':
            self.choices = None
            for key in kwargs.keys():
                if key.lower() == 'choices':
                    self.choices = kwargs[key]
                    break

            if self.choices is None:
                raise ValueError('A discrete variable requires to '
                                 'input an array of choices')

            if not isinstance(value, int):
                raise TypeError("A discrete variable requires the 'value' "
                                "to be a valid index the choices array")
            else:
                self.value = self.choices[int(value)]

            self.lower = 0
            self.upper = len(self.choices) - 1
        else:
            raise ValueError('Unknown variable types: should be '
                             'either c(ontinuous), i(nteger) or d(iscrete)')

        if self.upper < self.lower:
            raise ValueError("Upper bound is smaller than lower bound!")

    def __repr__(self):
        if self.type_ == 'd':
            return '{:^12}  {:^6}  {:^12.4e}  {:^12.4e}  {:^12.4e}\n'.format(
                self.name[:12], self.type_, self.choices[int(self.value)],
                min(self.choices), max(self.choices))

        return '{:^12}  {:^6}  {:^12.4e}  {:^12.4e}  {:^12.4e}\n'.format(
            self.name[:12], self.type_, self.value, self.lower, self.upper)

    def __str__(self):
        return '{:^12}  {:^6}  {:^12}  {:^12}  {:^12}\n'.format(
               'Name', 'Type', 'Value', 'Lower Bound', 'Upper Bound') + \
               self.__repr__()
