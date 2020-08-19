"""
Author: Jun Zhu
"""
from abc import ABC, abstractmethod


class OperationalElement(ABC):
    """Abstract class.

    Base class of Variables, Objectives, Jitters and so on used in
    Optimization and Jitter studies.
    """
    def __init__(self, name):
        """Initialization.

        :param name: str
            Name of the element.
        """
        self.name = name

    @abstractmethod
    def list_item(self):
        pass

    @abstractmethod
    def __str__(self):
        pass


class EvaluatedElement(OperationalElement):
    """Inherited from OperationalElement. Abstract class.

    The value of the class instance can be either calculated by parsing
    a given string or evaluating a given function.
    """
    def __init__(self, name, *, expr=None, scale=1.0, func=None):
        """Initialization.

        :param expr: string
            Expression for an attribute of a BeamParameters instance
            or a LineParameters instance,
            e.g. gun.out.Sx, chicane.max.betax.

            Ignored if 'func' is defined.
        :param scale: float
            Multiplier of the value evaluated from 'expr'.
        :param func: functor
            Used fo update the constraint value.
        """
        super().__init__(name)

        self.expr = expr
        self.scale = scale
        self.func = func

        if func is None:
            if expr is None:
                return

            if not isinstance(expr, str):
                raise TypeError("'expr' must be a string!")

            self.expr = expr.split(".")
            if len(self.expr) != 3:
                raise ValueError("'expr' must have the form "
                                 "'beamline_name.WatchParameters_name.param_name' "
                                 "or "
                                 "'beamline_name.LineParameters_name.param_name'")
        else:
            if not hasattr(func, '__call__'):
                raise TypeError("'func' must be callable!")
