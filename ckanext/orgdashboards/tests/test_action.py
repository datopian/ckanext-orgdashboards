import requests
import os

from ckan.tests.helpers import reset_db
from ckan import plugins
from ckan.tests import factories
from ckan.plugins import toolkit

from ckanext.orgdashboards.tests.helpers import create_mock_data


class TestCustomActions():
    
    @classmethod
    def setup_class(self, **kwargs):
        # Every time the test is run, the database is resetted
        reset_db()

        if not plugins.plugin_loaded('image_view'):
            plugins.load('image_view')

        if not plugins.plugin_loaded('orgdashboards'):
            plugins.load('orgdashboards')

        self.mock_data = create_mock_data()

    @classmethod
    def teardown_class(self):
        plugins.unload('image_view')
        plugins.unload('orgdashboards')

    def test_show_datasets(self):
        data_dict = {'id': self.mock_data['organization_name']}

        datasets = toolkit.get_action('orgdashboards_show_datasets')(
            self.mock_data['context'], data_dict)

        # Create 5 datasets
        for id in range(0, 5):
            factories.Dataset()

        for id in range(5, 0):
            assert datasets[id]['name'] == 'test_dataset_{id}'.format(id=id)

    def test_dataset_show_resources(self):
        data_dict = {'id': self.mock_data['dataset_name']}

        resources = toolkit.get_action('orgdashboards_dataset_show_resources')(
            self.mock_data['context'], data_dict)

        assert len(resources) == 1
        assert resources[0]['name'] == self.mock_data['resource_name']

    def test_resource_show_resource_views(self):
        data_dict = {
            'id': self.mock_data['resource_id'],
            'view_type': 'image_view'
        }

        resource_views = toolkit.\
            get_action('orgdashboards_resource_show_resource_views')(
                self.mock_data['context'], data_dict)

        assert len(resource_views) == 1
        assert resource_views[0]['title'] == self.mock_data['resource_view_title']

    def test_orgdashboards_resource_show_map_properties(self):
        sysadmin = factories.Sysadmin()
        resource = factories.Resource()
        file_path = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), 'data.geojson')

        data_dict = {
            'package_id': self.mock_data['dataset_name'],
            'name': resource['name'],
            'url': 'test_url'
        }

        # Upload resource
        response = requests.post(
            'http://localhost:5000/api/action/resource_create',
            data=data_dict,
            headers={"X-CKAN-API-Key": sysadmin['apikey']},
            files=[('upload', file(file_path))])

        resource_id = response.json()['result']['id']

        data_dict = {'id': resource_id}

        map_properties = toolkit.get_action(
            'orgdashboards_resource_show_map_properties')(
            self.mock_data['context'], data_dict)

        mock_map_properties = {
            'Block Operators ': 'Berlanga Holding ',
            'Areas of operation': 'Mottama',
            'Myanmar Block': 'M-8',
            'Address':
            '8 Temasek Boulevard, #08-01 Suntec Tower Three, Singapore 038988 '
        }

        assert len(map_properties) == 4

        for i, item in enumerate(mock_map_properties.iteritems()):
            assert map_properties[i]['value'] == item[0]
            assert map_properties[i]['text'] == item[1]

    def test_orgdashboards_get_map_main_property(self):
        data_dict = {
            'id': self.mock_data['organization_name'],
            'orgdashboards_map_main_property': 'test'
        }

        toolkit.get_action('organization_patch')(
            self.mock_data['context'], data_dict)

        data_dict = {'id': self.mock_data['organization_name']}

        map_main_property = toolkit.get_action(
            'orgdashboards_get_map_main_property')(
            self.mock_data['context'], data_dict)

        assert map_main_property == 'test'
