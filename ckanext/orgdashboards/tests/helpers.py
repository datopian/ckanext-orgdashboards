''' Helper methods for tests '''

import string
import random

from ckan.tests import factories


def create_mock_data(organization_name, dataset_name, resource_name,
                     resource_view_title, **kwargs):
    mock_data = {}

    mock_data['organization'] = factories.Organization(name=organization_name)
    mock_data['organization_name'] = organization_name
    mock_data['organization_id'] = mock_data['organization']['id']

    mock_data['dataset'] = factories.Dataset(
        name=dataset_name,
        owner_org=mock_data['organization_id'])
    mock_data['dataset_name'] = dataset_name
    mock_data['package_id'] = mock_data['dataset']['id']

    mock_data['resource'] = factories.Resource(
        package_id=mock_data['package_id'],
        name=resource_name)
    mock_data['resource_name'] = resource_name
    mock_data['resource_id'] = mock_data['resource']['id']

    mock_data['resource_view'] = factories.ResourceView(
        resource_id=mock_data['resource_id'],
        title=resource_view_title)
    mock_data['resource_view_title'] = resource_view_title

    mock_data['context'] = {
        'user': factories._get_action_user_name(kwargs)
    }

    return mock_data


def id_generator(size=6, chars=string.ascii_lowercase + string.digits):
    ''' Create random id which is a combination of letters and numbers '''

    return ''.join(random.choice(chars) for _ in range(size))
