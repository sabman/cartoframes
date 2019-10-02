import pandas as pd
import geopandas as gpd
import uuid

from collections import defaultdict
from ..dataset.dataset import Dataset
from ..clients import bigquery_client
from ...utils.geom_utils import wkt_to_geojson, geojson_to_wkt
from ...exceptions import EnrichmentException
from ...auth import get_default_credentials
from ...utils.geom_utils import _compute_geometry_from_geom

_ENRICHMENT_ID = 'enrichment_id'
_WORKING_PROJECT = 'carto-do-customers'


def enrich(query_function, **kwargs):
    credentials = _get_credentials(kwargs['credentials'])
    user_dataset = credentials.username.replace('-', '_')
    bq_client = _get_bigquery_client(_WORKING_PROJECT, credentials)

    data_copy = _prepare_data(kwargs['data'], kwargs['data_geom_column'])
    tablename = _upload_dataframe(bq_client, user_dataset, data_copy, kwargs['data_geom_column'])

    query = _enrichment_query(user_dataset, tablename, query_function, **kwargs)

    return _execute_enrichment(bq_client, query, data_copy, kwargs['data_geom_column'])


def _get_credentials(credentials=None):
    return credentials or get_default_credentials()


def _get_bigquery_client(project, credentials):
    return bigquery_client.BigQueryClient(project, credentials)


def _prepare_data(data, data_geom_column):
    data_copy = __copy_data_and_generate_enrichment_id(data, _ENRICHMENT_ID, data_geom_column)
    data_copy[data_geom_column] = data_copy[data_geom_column].apply(wkt_to_geojson)
    return data_copy


def _upload_dataframe(bq_client, user_dataset, data_copy, data_geom_column):
    data_geometry_id_copy = data_copy[[data_geom_column, _ENRICHMENT_ID]]
    schema = {data_geom_column: 'GEOGRAPHY', _ENRICHMENT_ID: 'INTEGER'}

    id_tablename = uuid.uuid4().hex
    data_tablename = 'temp_{id}'.format(id=id_tablename)

    bq_client.upload_dataframe(data_geometry_id_copy, schema, data_tablename,
                               project=_WORKING_PROJECT, dataset=user_dataset)

    return data_tablename


def _enrichment_query(user_dataset, tablename, query_function, **kwargs):
    table_data_enrichment, table_geo_enrichment, variables_list = __get_tables_and_variables(kwargs['variables'])
    filters_str = __process_filters(kwargs['filters'])

    return query_function(_ENRICHMENT_ID, filters_str, variables_list, table_data_enrichment,
                          table_geo_enrichment, user_dataset, _WORKING_PROJECT, tablename, **kwargs)


def _execute_enrichment(bq_client, query, data_copy, data_geom_column):
    df_enriched = bq_client.query(query).to_dataframe()

    data_copy = data_copy.merge(df_enriched, on=_ENRICHMENT_ID, how='left').drop(_ENRICHMENT_ID, axis=1)
    data_copy[data_geom_column] = data_copy[data_geom_column].apply(geojson_to_wkt)

    return data_copy


def __copy_data_and_generate_enrichment_id(data, enrichment_id_column, geometry_column):

    has_to_decode_geom = True

    if isinstance(data, Dataset):
        if data.dataframe is None:
            has_to_decode_geom = False
            geometry_column = 'the_geom'
            data.download(decode_geom=True)

        data = data.dataframe
    elif isinstance(data, gpd.GeoDataFrame):
        has_to_decode_geom = False

    data_copy = data.copy()
    data_copy[enrichment_id_column] = range(data_copy.shape[0])

    if has_to_decode_geom:
        data_copy[geometry_column] = _compute_geometry_from_geom(data_copy[geometry_column])

    data_copy[geometry_column] = data_copy[geometry_column].apply(lambda geometry: geometry.wkt)

    return data_copy


def __process_filters(filters_dict):
    filters = ''
    # TODO: Add data table ref in fields of filters
    if filters_dict:
        filters_list = list()

        for key, value in filters_dict.items():
            filters_list.append('='.join(["{}".format(key), "'{}'".format(value)]))

        filters = ' AND '.join(filters_list)
        filters = 'WHERE {filters}'.format(filters=filters)

    return filters


def __get_tables_and_variables(variables):

    if isinstance(variables, pd.Series):
        variables_id = [variables['id']]
    elif isinstance(variables, pd.DataFrame):
        variables_id = variables['id'].tolist()
    else:
        raise EnrichmentException('Variable(s) to enrich should be an instance of Series or DataFrame')

    table_to_variables = __process_enrichment_variables(variables_id)
    table_data_enrichment = list(table_to_variables.keys()).pop()
    table_geo_enrichment = __get_name_geotable_from_datatable(table_data_enrichment)
    variables_list = list(table_to_variables.values()).pop()

    return table_data_enrichment, table_geo_enrichment, variables_list


def __process_enrichment_variables(variables):
    table_to_variables = defaultdict(list)

    for variable in variables:
        variable_split = variable.split('.')
        table, variable = variable_split[-2], variable_split[-1]

        table_to_variables[table].append(variable)

    return table_to_variables


def __get_name_geotable_from_datatable(datatable):
    datatable_split = datatable.split('_')
    geo_information = datatable_split[2:5]
    geotable = 'geography_{geo_information_joined}'.format(geo_information_joined='_'.join(geo_information))

    return geotable