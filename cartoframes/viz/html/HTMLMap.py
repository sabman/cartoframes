from warnings import warn
from jinja2 import Environment, PackageLoader
from .. import constants
from ..basemaps import Basemaps


class HTMLMap(object):
    def __init__(self, template_path='templates/viz/basic.html.j2'):
        self.width = None
        self.height = None
        self.srcdoc = None
        self._env = Environment(
            loader=PackageLoader('cartoframes', 'assets/templates'),
            autoescape=True
        )

        self._env.filters['quot'] = _quote_filter
        self._env.filters['iframe_size'] = _iframe_size_filter
        self._env.filters['clear_none'] = _clear_none_filter

        self.html = None
        self._template = self._env.get_template(template_path)

    def set_content(
        self, size, layers, bounds, viewport=None, basemap=None,
            default_legend=None, show_info=None, theme=None, _carto_vl_path=None,
            _airship_path=None, title='CARTOframes', is_embed=False,
            is_static=False):

        self.html = self._parse_html_content(
            size, layers, bounds, viewport, basemap, default_legend,
            show_info, theme, _carto_vl_path, _airship_path, title, is_embed, is_static)

    def _parse_html_content(
        self, size, layers, bounds, viewport, basemap=None, default_legend=None,
            show_info=None, theme=None, _carto_vl_path=None, _airship_path=None, title=None, is_embed=False,
            is_static=False):

        token = ''
        basecolor = ''

        if basemap is None:
            # No basemap
            basecolor = 'white'
            basemap = ''
        elif isinstance(basemap, str):
            if basemap not in [Basemaps.voyager, Basemaps.positron, Basemaps.darkmatter]:
                # Basemap is a color
                basecolor = basemap
                basemap = ''
        elif isinstance(basemap, dict):
            token = basemap.get('token', '')
            if 'style' in basemap:
                basemap = basemap.get('style')
                if not token and basemap.get('style').startswith('mapbox://'):
                    warn('A Mapbox style usually needs a token')
            else:
                raise ValueError(
                    'If basemap is a dict, it must have a `style` key'
                )

        if _carto_vl_path is None:
            carto_vl_path = constants.CARTO_VL_URL
        else:
            carto_vl_path = _carto_vl_path + constants.CARTO_VL_DEV

        if _airship_path is None:
            airship_components_path = constants.AIRSHIP_COMPONENTS_URL
            airship_bridge_path = constants.AIRSHIP_BRIDGE_URL
            airship_module_path = constants.AIRSHIP_MODULE_URL
            airship_styles_path = constants.AIRSHIP_STYLES_URL
            airship_icons_path = constants.AIRSHIP_ICONS_URL
        else:
            airship_components_path = _airship_path + constants.AIRSHIP_COMPONENTS_DEV
            airship_bridge_path = _airship_path + constants.AIRSHIP_BRIDGE_DEV
            airship_module_path = _airship_path + constants.AIRSHIP_MODULE_DEV
            airship_styles_path = _airship_path + constants.AIRSHIP_STYLES_DEV
            airship_icons_path = _airship_path + constants.AIRSHIP_ICONS_DEV

        camera = None
        if viewport is not None:
            camera = {
                'center': _get_center(viewport),
                'zoom': viewport.get('zoom'),
                'bearing': viewport.get('bearing'),
                'pitch': viewport.get('pitch')
            }

        has_legends = any(layer['legend'] for layer in layers) or default_legend
        has_widgets = any(len(layer['widgets']) != 0 for layer in layers)

        return self._template.render(
            width=size[0] if size is not None else None,
            height=size[1] if size is not None else None,
            layers=layers,
            basemap=basemap,
            basecolor=basecolor,
            mapboxtoken=token,
            bounds=bounds,
            camera=camera,
            has_legends=has_legends,
            has_widgets=has_widgets,
            default_legend=default_legend,
            show_info=show_info,
            theme=theme,
            carto_vl_path=carto_vl_path,
            airship_components_path=airship_components_path,
            airship_module_path=airship_module_path,
            airship_bridge_path=airship_bridge_path,
            airship_styles_path=airship_styles_path,
            airship_icons_path=airship_icons_path,
            title=title,
            is_embed=is_embed,
            is_static=is_static
        )

    def _repr_html_(self):
        return self.html


def _safe_quotes(text, escape_single_quotes=False):
    """htmlify string"""
    if isinstance(text, str):
        safe_text = text.replace('"', "&quot;")
        if escape_single_quotes:
            safe_text = safe_text.replace("'", "&#92;'")
        return safe_text.replace('True', 'true')
    return text


def _quote_filter(value):
    return _safe_quotes(value.unescape())


def _iframe_size_filter(value):
    if isinstance(value, str):
        return value

    return '%spx;' % value


def _clear_none_filter(value):
    return dict(filter(lambda item: item[1] is not None, value.items()))


def _get_center(center):
    if 'lng' not in center or 'lat' not in center:
        return None

    return [center.get('lng'), center.get('lat')]
