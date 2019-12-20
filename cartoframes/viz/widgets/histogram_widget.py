from ..widget import Widget


def histogram_widget(value, title='', description='', footer='', read_only=False, buckets=20):
    """Helper function for quickly creating a histogram widget.

    Histogram widgets display the distribution of a numeric attribute, in buckets, to group
    ranges of values in your data.
    By default, you can hover over each bar to see each bucket's values and count, and also
    filter your map's data within a given range

    Args:
        value (str): Column name of the numeric or date value
        title (str, optional): Title of widget.
        description (str, optional): Description text widget placed under widget title.
        footer (str, optional): Footer text placed on the widget bottom
        buckets (number, optional): Number of histogram buckets. Set to 20 by default.
        read_only (boolean, optional): Interactively filter a range of numeric values by
            selecting them in the widget. Set to "False" by default.

    Returns:
        cartoframes.viz.Widget: Widget with type='histogram'

    Example:

        .. code::

            from cartoframes.viz import Map, Layer, histogram_widget

            Map(
                Layer(
                    'seattle_collisions',
                    widgets=[
                        histogram_widget(
                            'vehcount',
                            title='Number of Vehicles Involved',
                            description='Select a range of values to filter',
                            buckets=9
                        )
                    ]
                )
            )
    """

    return Widget('histogram',
                  value=value,
                  title=title,
                  description=description,
                  footer=footer,
                  read_only=read_only,
                  buckets=buckets)
