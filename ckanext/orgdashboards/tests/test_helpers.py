import datetime

from nose.tools import assert_raises

from ckan.tests.helpers import reset_db
from ckan import plugins
import ckan.lib.search as search
from ckan.tests import factories

from ckanext.orgdashboards.tests.helpers import (id_generator,
                                                 create_mock_data,
                                                 upload_json_resource,
                                                 mock_map_properties)
from ckanext.orgdashboards import helpers


class TestHelpers():

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

    def test_get_newly_released_data(self, **kwargs):
        dataset_found = False

        assert_raises(search.SearchError,
                      helpers.orgdashboards_get_newly_released_data,
                      organization_name='',
                      limit=5)

        packages = helpers.orgdashboards_get_newly_released_data(
            organization_name=self.mock_data['organization_name'],
            limit=5)

        assert len(packages) > 0

        for item in packages:
            if item['name'] == self.mock_data['dataset_name']:
                dataset_found = True

        assert dataset_found is True

    def test_convert_time_format(self):
        formatted_date = helpers.orgdashboards_convert_time_format(
            self.mock_data['dataset'])

        today = datetime.date.today()

        assert formatted_date == today.strftime("%d %B %Y")

    def test_replace_or_add_url_param(self):
        organization_name = self.mock_data['organization_name']
        author = 'Aleksandar Jovanov'
        controller =\
            'ckanext.orgdashboards.controllers.dashboard:DashboardsController'
        action = 'organization_dashboard'
        name = 'tags'
        value = 'nature'

        url = helpers.orgdashboards_replace_or_add_url_param(
            name=name,
            value=value,
            params=[],
            controller=controller,
            action=action,
            context_name=organization_name)

        assert url == '/organization/{0}/dashboard?{1}={2}'.format(
            organization_name, name, value)

        url = helpers.orgdashboards_replace_or_add_url_param(
            name=name,
            value=value,
            params=[('page', '2'), ('author', author)],
            controller=controller,
            action=action,
            context_name=organization_name)

        new_url = '/organization/{0}/dashboard?page=1&author={1}&{2}={3}'\
            .format(organization_name,
                    '+'.join(author.split(' ')),
                    name,
                    value)

        assert url == new_url

    def test_get_resourceview_resource_package(self):
        chart_resources = helpers.get_resourceview_resource_package(
            self.mock_data['resource_view_id'])

        resource_view = chart_resources[0]
        resource = chart_resources[1]
        package = chart_resources[2]

        assert resource_view['title'] == self.mock_data['resource_view_title']
        assert resource['name'] == self.mock_data['resource_name']
        assert package['name'] == self.mock_data['dataset_name']

    def test_get_organization_list(self):
        organization_list = helpers.orgdashboards_get_organization_list()

        assert len(organization_list) > 0

        for item in organization_list:
            assert 'is_organization' in item

    def test_get_all_organizations(self):

        # Create another organization.
        factories.Organization(name='another_organization')

        organizations = helpers.orgdashboards_get_all_organizations(
            self.mock_data['organization_name'])

        assert len(organizations) > 0

        assert organizations[0]['text'] == 'None'
        assert organizations[0]['value'] == 'none'

        assert organizations[1]['text'] == 'Test Organization'
        assert organizations[1]['value'] == 'another_organization'

    def test_get_available_languages(self):
        languages = helpers.orgdashboards_get_available_languages()

        assert len(languages) > 0

        assert languages[0]['text'] == 'None'
        assert languages[0]['value'] == 'none'

        assert {'text': 'English', 'value': 'en'} in languages

    def test_get_maps(self):
        resource_name = id_generator()
        resource = upload_json_resource(
            self.mock_data['dataset_name'],
            resource_name)
        maps = helpers.org_views.get_maps(self.mock_data['organization_name'])
        resource_found = False

        assert len(maps) > 0

        for item in maps:
            if item['text'] == resource_name and\
               item['value'] == resource['id']:
                resource_found = True

        assert resource_found is True

    def test_get_resource_url(self):
        url = helpers.orgdashboards_get_resource_url(
            self.mock_data['resource_id'])

        assert url == self.mock_data['resource']['url']

    def test_get_geojson_properties(self):
        resource_name = id_generator()
        resource = upload_json_resource(
            self.mock_data['dataset_name'],
            resource_name)
        map_properties = helpers.orgdashboards_get_geojson_properties(
            resource['id'])

        assert len(map_properties) == 4

        for i, item in enumerate(mock_map_properties.iteritems()):
            assert map_properties[i]['value'] == item[0]
            assert map_properties[i]['text'] == item[1]
