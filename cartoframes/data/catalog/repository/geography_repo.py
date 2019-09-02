from data.catalog.repository.repo_client import RepoClient


def get_geography_repo():
    return GeographyRepository()


class GeographyRepository(object):

    def __init__(self):
        self.client = RepoClient()

    def get_all(self):
        return [self._to_geography(result) for result in self.client.get_geographies()]

    def get_by_id(self, geography_id):
        result = self.client.get_geographies('id', geography_id)[0]
        return self._to_geography(result)

    def get_by_country(self, iso_code):
        # TODO
        pass

    @staticmethod
    def _to_geography(result):
        return {
            'id': result['id'],
            'name': result['name'],
            'provider_id': result['provider_id'],
            'country': result['country_iso_code3'],
            'version': result['version'],
            'is_public': result['is_public_data']
        }
