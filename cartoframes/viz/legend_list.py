from .legend import Legend


class LegendList(object):
    """LegendList
     Args:
        legends (list, Legend): List of legends for a layer.

    Example:

        .. code::python

            from cartoframes.viz import legend

            LegendList([])
    """

    def __init__(self, legends=None):
        self._legends = self._init_legends(legends)

    def _init_legends(self, legends):
        if isinstance(legends, list):
            legend_list = []
            for legend in legends:
                if isinstance(legend, Legend):
                    legend_list.append(legend)
                else:
                    raise ValueError('Legends list contains invalid elements')
            return legend_list
        elif isinstance(legends, Legend):
            return [legends]
        else:
            return []

    def get_info(self):
        legends_info = []
        for legend in self._legends:
            if legend:
                legends_info.append(legend.get_info())

        return legends_info
