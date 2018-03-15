from liso import LinePlot


if __name__ == "__main__":
    l2 = LinePlot('astra', 'astra_basic/injector')
    l2.plot('Sx', y_unit='Mm')
    l2.plot('emitx', 'emity', y_unit='nm')
    l2.save_plot('Sx', 'Sy', y_unit='mM')

    l1 = LinePlot('impactt', 'impactt_basic/fort')
    l1.plot('Sx', y_unit='um')
    l1.plot('betax', 'betay')
    l1.save_plot('emitx', 'emity', y_unit='Nm')
