from mock import MagicMock
from pylons import config

from ckanext.orgdashboards import plugin


class TestPlugin():

    @classmethod
    def setup_class(self, **kwargs):
        # Create the plugin
        self._plugin = plugin.OrgDashboardsPlugin()

    def test_before_map(self):
        mapper = MagicMock()

        self._plugin.before_map(mapper)

        organization_entity_name = config.get(
            'ckanext.orgdashboards.organization_entity_name',
            'organization')

        ctrl =\
            'ckanext.orgdashboards.controllers.dashboard:DashboardsController'

        # Check that the mapper has been called correctly
        mapper.connect.assert_called_with(
            '/' + organization_entity_name + '/{name}/dashboard',
            controller=ctrl,
            action='preview_dashboard')

    def test_is_fallback(self):
        is_fallback = self._plugin.is_fallback()

        assert is_fallback is False

    def test_group_types(self):
        group_types = self._plugin.group_types()

        assert group_types == ['organization']

    def test_form_to_db_schema_options(self):
        options = MagicMock()

        self._plugin.form_to_db_schema_options(options)

        options.get.assert_called_with('context', {})
        options.get('context', {}).get.assert_called_with('schema', None)
