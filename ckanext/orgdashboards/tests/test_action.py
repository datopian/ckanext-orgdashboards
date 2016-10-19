from ckan.tests.helpers import reset_db
from ckan import plugins
from ckan.tests import factories
from ckan.plugins import toolkit

from ckanext.orgdashboards.tests.helpers import (id_generator,
                                                 create_mock_data,
                                                 upload_json_resource,
                                                 mock_map_properties)


class TestCustomActions():

    @classmethod
    def setup_class(self, **kwargs):
        # Every time the test is run, the database is resetted
        reset_db()

        if not plugins.plugin_loaded('image_view'):
            plugins.load('image_view')

        if not plugins.plugin_loaded('orgdashboards'):
            plugins.load('orgdashboards')

        organization_name = id_generator()
        dataset_name = id_generator()
        resource_name = id_generator()
        resource_view_title = id_generator()

        self.mock_data = create_mock_data(
            organization_name=organization_name,
            dataset_name=dataset_name,
            resource_name=resource_name,
            resource_view_title=resource_view_title)

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
        resource_found = False

        resources = toolkit.get_action('orgdashboards_dataset_show_resources')(
            self.mock_data['context'], data_dict)

        assert len(resources) > 0

        for item in resources:
            if item['name'] == self.mock_data['resource_name']:
                resource_found = True

        assert resource_found is True

    def test_resource_show_resource_views(self):
        data_dict = {
            'id': self.mock_data['resource_id'],
            'view_type': 'image_view'
        }
        resource_view_found = False

        resource_views = toolkit.\
            get_action('orgdashboards_resource_show_resource_views')(
                self.mock_data['context'], data_dict)

        assert len(resource_views) > 0

        for item in resource_views:
            if item['title'] == self.mock_data['resource_view_title']:
                resource_view_found = True

        assert resource_view_found is True

    def test_resource_show_map_properties(self):
        resource = upload_json_resource(
            self.mock_data['dataset_name'],
            resource_name=id_generator())
        resource_id = resource['id']

        data_dict = {'id': resource_id}

        map_properties = toolkit.get_action(
            'orgdashboards_resource_show_map_properties')(
            self.mock_data['context'], data_dict)

        assert len(map_properties) == 4

        for i, item in enumerate(mock_map_properties.iteritems()):
            assert map_properties[i]['value'] == item[0]
            assert map_properties[i]['text'] == item[1]

    def test_get_map_main_property(self):
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
