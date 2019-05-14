from __future__ import absolute_import

from . import defaults


class Style(object):
    """Style

    Args:
        style (str, dict): The style for the layer. It can be a dictionary or a viz string.
          More info at
          `CARTO VL styling <https://carto.com/developers/carto-vl/guides/style-with-expressions/>`

    Example:

        String API.

        .. code::
            from cartoframes.vis import Style

            Style('color: blue')

            Style('''
                @sum: sqrt($pop_max) / 100
                @grad: [red, blue, green]
                color: ramp(globalEqIntervals($pop_min, 3), @grad)
                filter: @sum > 20
            ''')

        Dict API.

        .. code::
            from cartoframes.vis import Style

            Style({
                'color': 'blue'
            })

            Style({
                'vars': {
                    'sum': 'sqrt($pop_max) / 100',
                    'grad': '[red, blue, green]'
                },
                'color': 'ramp(globalEqIntervals($pop_min, 3), @grad)',
                'filter': '@sum > 20'
            })
    """

    def __init__(self, style=None):
        self.viz = self._init_style(style)

    def _init_style(self, style):
        """Adds style properties to the viz"""
        if style is None:
            return ''
        elif isinstance(style, dict):
            return self._parse_style_properties_dict(style)
        elif isinstance(style, str):
            return style
        else:
            raise ValueError('`style` must be a dictionary or a viz string')

    def _parse_style_properties_dict(self, style):
        style_variables = []
        style_properties = []

        for prop in style:
            if prop == 'vars':
                variables = style.get(prop)
                for var in variables:
                    style_variables.append(
                        '@{name}: {value}'.format(
                            name=var,
                            value=_convstr(variables.get(var))
                        )
                    )
            elif prop in defaults._STYLE_PROPERTIES and style.get(prop) is not None:
                style_properties.append(
                    '{name}: {value}'.format(
                        name=prop,
                        value=_convstr(style.get(prop))
                    )
                )
            else:
                raise ValueError('Style property "' + prop + '" is not valid. Valid style properties are: ' +
                                 ', '.join(defaults._STYLE_PROPERTIES))

        return '\n'.join(style_variables).join(style_properties)


def _convstr(obj):
    """Converts all types to strings or None"""
    return str(obj) if obj is not None else None
