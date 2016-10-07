from ckan.tests.helpers import reset_db
from ckan import plugins
from ckan.tests import factories
from ckan.plugins import toolkit


class TestCustomActions():

    org_name = 'test_org'
    dataset_name = 'test_dataset'
    resource_name = 'test_resource'

    @classmethod
    def setup_class(self, **kwargs):
        reset_db()

        self.context = {
            'user': factories._get_action_user_name(kwargs)
        }

        data_dict = {'name': self.org_name}

        toolkit.get_action('organization_create')(self.context, data_dict)

        for id in range(0, 5):
            data_dict = {
                'name': '{dataset_name}_{id}'.format(
                    dataset_name=self.dataset_name, id=id),
                'owner_org': self.org_name
            }

            toolkit.get_action('package_create')(self.context, data_dict)

        plugins.load('orgdashboards')

    def test_show_datasets(self):
        data_dict = {'id': self.org_name}

        datasets = toolkit.get_action('orgdashboards_show_datasets')(
            self.context, data_dict)

        for id in range(5, 0):
            assert datasets[id]['name'] == '{dataset_name}_{id}'.format(
                dataset_name=self.dataset_name, id=id)

    def test_dataset_show_resources(self):
        data_dict = {
            'name': self.dataset_name,
            'owner_org': self.org_name
        }

        toolkit.get_action('package_create')(self.context, data_dict)

        data_dict = {
            'package_id': self.dataset_name,
            'url': 'http://google.com',
            'name': self.resource_name
        }

        toolkit.get_action('resource_create')(self.context, data_dict)

        data_dict = {'id': self.dataset_name}

        resources = toolkit.get_action('orgdashboards_dataset_show_resources')(
            self.context, data_dict)

        assert len(resources) == 1
        assert resources[0]['name'] == self.resource_name

    def test_resource_show_resource_views(self):
        resource_view_title = 'test_view_title'

        data_dict = {
            'package_id': self.dataset_name,
            'url': 'http://google.com',
            'name': self.resource_name
        }

        resource = toolkit.get_action('resource_create')(
            self.context, data_dict)

        resource_id = resource['id']

        data_dict = {
            'resource_id': resource_id,
            'title': resource_view_title,
            'view_type': 'image_view'
        }

        toolkit.get_action('resource_view_create')(
            self.context, data_dict)

        data_dict = {'id': self.resource_name}

        resource_views = toolkit.\
            get_action('orgdashboards_resource_show_resource_views')(
                self.context, data_dict)

        assert len(resource_views) == 0
        # assert resource_views[0]['title'] == resource_view_title
