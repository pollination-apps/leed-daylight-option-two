"""Visualization metadata for LEED Daylight Option II."""
from ladybug.datatype.generic import GenericType
from ladybug.datatype.illuminance import Illuminance
from ladybug.legend import LegendParameters
from ladybug.color import Colorset


def _leed_daylight_option_two_vis_metadata():
    """Return visualization metadata for LEED Daylight Option II."""
    ill_lpar = LegendParameters(min=300, max=3000, colors=Colorset.ecotect())
    pass_fail_lpar = LegendParameters(min=0, max=1, colors=Colorset.ecotect())

    metric_info_dict = {
        'illuminance-9am': {
            'type': 'VisualizationMetaData',
            'data_type': Illuminance('Illuminance 9am').to_dict(),
            'unit': 'lux',
            'legend_parameters': ill_lpar.to_dict()
        },
        'illuminance-3pm': {
            'type': 'VisualizationMetaData',
            'data_type': Illuminance('Illuminance 3pm').to_dict(),
            'unit': 'lux',
            'legend_parameters': ill_lpar.to_dict()
        },
        'pass-fail-9am': {
            'type': 'VisualizationMetaData',
            'data_type': GenericType('Pass/Fail 9am', '').to_dict(),
            'unit': '',
            'legend_parameters': pass_fail_lpar.to_dict()
        },
        'pass-fail-3pm': {
            'type': 'VisualizationMetaData',
            'data_type': GenericType('Pass/Fail 3pm', '').to_dict(),
            'unit': '',
            'legend_parameters': pass_fail_lpar.to_dict()
        },
        'pass-fail-combined': {
            'type': 'VisualizationMetaData',
            'data_type': GenericType('Pass/Fail', '').to_dict(),
            'unit': '',
            'legend_parameters': pass_fail_lpar.to_dict()
        }
    }

    return metric_info_dict
