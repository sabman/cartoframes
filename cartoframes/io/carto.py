"""Functions to interact with the CARTO platform"""

import pandas as pd

from ..core.cartodataframe import CartoDataFrame
from ..core.managers.context_manager import ContextManager
from ..utils.utils import is_sql_query


def read_carto(source, credentials=None, limit=None, retry_times=3, schema=None,
               drop_cartodb_id=True, drop_the_geom=True, drop_the_geom_webmercator=True):
    """
    Read a table or a SQL query from the CARTO account.

    Args:
        source (str): table name or SQL query.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            instance of Credentials (username, api_key, etc).
        limit (int, optional):
            The number of rows to download. Default is to download all rows.
        retry_times (int, optional):
            Number of time to retry the download in case it fails. Default is 3.
        schema (str, optional):prefix of the table. By default, it gets the
            `current_schema()` using the credentials.
        drop_cartodb_id (bool, optional): drop the "cartodb_id" column used as index.
        drop_the_geom (bool, optional): drop the "the_geom" column used as geometry.
        drop_the_goem_webmercator (bool, optional): drop the "the_geom_webmercator" column.

    Returns:
        :py:class:`CartoDataFrame <cartoframes.CartoDataFrame>`

    """
    if not isinstance(source, str):
        raise ValueError('Wrong source. You should provide a valid table_name or SQL query.')

    context_manager = ContextManager(credentials)

    df = context_manager.copy_to(source, schema, limit, retry_times, drop_the_geom_webmercator)

    return CartoDataFrame(df).convert(
        index_column='cartodb_id',
        geom_column='the_geom',
        drop_index=drop_cartodb_id,
        drop_geom=drop_the_geom
    )


def to_carto(dataframe, table_name, credentials=None, if_exists='fail'):
    """
    Read a table or a SQL query from the CARTO account.

    Args:
        dataframe (DataFrame): data frame to upload.
        table_name (str): name of the table to upload the data.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            instance of Credentials (username, api_key, etc).
        if_exists (str, optional): 'fail', 'replace', 'append'. Default is 'fail'.

    """
    if not isinstance(dataframe, pd.DataFrame):
        raise ValueError('Wrong dataframe. You should provide a valid DataFrame instance.')

    if not isinstance(table_name, str):
        raise ValueError('Wrong table name. You should provide a valid table name.')

    context_manager = ContextManager(credentials)

    cdf = CartoDataFrame(dataframe, copy=True).convert()

    context_manager.copy_from(cdf, table_name, if_exists)

    print('Success! Data uploaded correctly')


def has_table(table_name, credentials=None, schema=None):
    """
    Check if the table exists in the CARTO account.

    Args:
        table_name (str): name of the table.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            instance of Credentials (username, api_key, etc).
        schema (str, optional):prefix of the table. By default, it gets the
            `current_schema()` using the credentials.
    """
    if not isinstance(table_name, str):
        raise ValueError('Wrong table name. You should provide a valid table name.')

    context_manager = ContextManager(credentials)

    return context_manager.has_table(table_name, schema)


def delete_table(table_name, credentials=None):
    """
    Delete the table from the CARTO account.

    Args:
        table_name (str): name of the table.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            instance of Credentials (username, api_key, etc).
    """
    if not isinstance(table_name, str):
        raise ValueError('Wrong table name. You should provide a valid table name.')

    context_manager = ContextManager(credentials)

    return context_manager.delete_table(table_name)


def describe_table(table_name, credentials=None, schema=None):
    """
    Describe the table in the CARTO account.

    Args:
        table_name (str): name of the table.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            instance of Credentials (username, api_key, etc).
        schema (str, optional):prefix of the table. By default, it gets the
            `current_schema()` using the credentials.
    """
    if not isinstance(table_name, str):
        raise ValueError('Wrong table name. You should provide a valid table name.')

    context_manager = ContextManager(credentials)
    query = context_manager.compute_query(table_name, schema)

    return {
        'privacy': context_manager.get_privacy(table_name),
        'num_rows': context_manager.get_num_rows(query),
        'geom_type': context_manager.get_geom_type(query)
    }


def update_table(table_name, credentials=None, new_table_name=None, privacy=None):
    """
    Update the table information in the CARTO account.

    Args:
        table_name (str): name of the table.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            instance of Credentials (username, api_key, etc).
        new_table_name(str, optional): new name for the table.
        privacy (str, optional): privacy of the table: 'PRIVATE', 'PUBLIC', 'LINK'.
    """
    if not isinstance(table_name, str):
        raise ValueError('Wrong table name. You should provide a valid table name.')

    valid_privacy_values = ['PRIVATE', 'PUBLIC', 'LINK']
    if privacy not in valid_privacy_values:
        raise ValueError('Wrong privacy. Valid names are {}'.format(', '.join(valid_privacy_values)))

    context_manager = ContextManager(credentials)
    context_manager.update_table(table_name, privacy, new_table_name)

    print('Success! Table updated correctly')


def copy_table(table_name, new_table_name, credentials=None, if_exists='fail'):
    """
    Copy a table into a new table in the CARTO account.

    Args:
        table_name (str): name of the original table.
        new_table_name(str, optional): name for the new table.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            instance of Credentials (username, api_key, etc).
        if_exists (str, optional): 'fail', 'replace'. Default is 'fail'.
    """
    if not isinstance(table_name, str):
        raise ValueError('Wrong table name. You should provide a valid string.')

    if not isinstance(new_table_name, str):
        raise ValueError('Wrong new table name. You should provide a valid string.')
    pass

    context_manager = ContextManager(credentials)

    query = 'SELECT * FROM {}'.format(table_name)
    context_manager.create_table_from_query(new_table_name, query, if_exists)

    print('Success! Table copied correctly')


def create_table_from_query(query, new_table_name, credentials=None, if_exists='fail'):
    """
    Create a new table from an SQL query in the CARTO account.

    Args:
        query (str): SQL query
        new_table_name(str): name for the new table.
        credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
            instance of Credentials (username, api_key, etc).
        if_exists (str, optional): 'fail', 'replace'. Default is 'fail'.
    """
    if not is_sql_query(query):
        raise ValueError('Wrong query. You should provide a valid SQL query.')

    if not isinstance(new_table_name, str):
        raise ValueError('Wrong table name. You should provide a valid table name.')
    pass

    context_manager = ContextManager(credentials)

    context_manager.create_table_from_query(new_table_name, query, if_exists)

    print('Success! Table created correctly')