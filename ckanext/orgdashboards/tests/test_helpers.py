from nose.tools import assert_raises

from ckan.tests.helpers import reset_db
from ckan import plugins
from ckan.tests import factories
from ckan.plugins import toolkit
import ckan.lib.search as search

from ckanext.orgdashboards.tests.helpers import id_generator
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

    @classmethod
    def teardown_class(self):
        plugins.unload('image_view')
        plugins.unload('orgdashboards')

    def test_get_newly_released_data(self, **kwargs):
        context = {
            'user': factories._get_action_user_name(kwargs)
        }   

        organization_name = id_generator()

        data_dict = {
            'name': organization_name
        }

        orgnization_id = toolkit.get_action('organization_create')(
            context, 
            data_dict)['id']

        data_dict = {
            'name': 'test_dataset_0', 
            'owner_org': orgnization_id
        }

        toolkit.get_action('package_create')(context, data_dict)

        assert_raises(search.SearchError, 
                      helpers.orgdashboards_get_newly_released_data, 
                      organization_name='', 
                      limit=5)

        packages = helpers.orgdashboards_get_newly_released_data(
            organization_name=organization_name, 
            limit=5)

        assert packages[0]['name'] == 'test_dataset_0'

