import datetime

from nose.tools import assert_raises

from ckan.tests.helpers import reset_db
from ckan import plugins
import ckan.lib.search as search

from ckanext.orgdashboards.tests.helpers import id_generator, create_mock_data
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

        assert_raises(search.SearchError,
                      helpers.orgdashboards_get_newly_released_data,
                      organization_name='',
                      limit=5)

        packages = helpers.orgdashboards_get_newly_released_data(
            organization_name=self.mock_data['organization_name'],
            limit=5)

        assert packages[0]['name'] == self.mock_data['dataset_name']

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
