import pandas as pd

from .repository.dataset_repo import get_dataset_repo
from .repository.geography_repo import get_geography_repo

_GEOGRAPHY_ID_FIELD = 'id'


class Geography(pd.Series):

    @property
    def _constructor(self):
        return Geography

    @property
    def _constructor_expanddim(self):
        return Geographies

    @staticmethod
    def get_by_id(geography_id):
        return get_geography_repo().get_by_id(geography_id)

    def datasets(self):
        return get_dataset_repo().get_by_geography(self[_GEOGRAPHY_ID_FIELD])

    def __eq__(self, other):
        return self.equals(other)

    def __ne__(self, other):
        return not self == other


class Geographies(pd.DataFrame):

    @property
    def _constructor(self):
        return Geographies

    @property
    def _constructor_sliced(self):
        return Geography

    def __init__(self, data):
        super(Geographies, self).__init__(data)
        self.set_index(_GEOGRAPHY_ID_FIELD, inplace=True, drop=False)

    @staticmethod
    def get_all():
        return get_geography_repo().get_all()

    @staticmethod
    def get_by_id(geography_id):
        return Geography.get_by_id(geography_id)

    def __eq__(self, other):
        return self.equals(other)

    def __ne__(self, other):
        return not self == other
