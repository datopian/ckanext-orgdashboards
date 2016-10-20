import requests

from routes import url_for

from ckan.tests.helpers import reset_db
from ckan import plugins

from ckanext.orgdashboards.tests.helpers import (id_generator,
                                                 create_mock_data,
                                                 get_site_base_url)


class TestController():

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

    def test_dashboard(self):
        controller =\
            'ckanext.orgdashboards.controllers.dashboard:DashboardsController'
        action = 'organization_dashboard'
        name = self.mock_data['organization_name']
        site_base_url = get_site_base_url()

        route = url_for(
            controller=controller,
            action=action,
            name=name)

        response = requests.get(site_base_url + route)

        assert response.ok is True
        assert response.status_code == 200
