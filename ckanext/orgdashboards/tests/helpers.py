from ckan.tests import factories


def create_mock_data(**kwargs):
    mock_data = {}

    mock_data['organization'] = factories.Organization()
    mock_data['organization_name'] = mock_data['organization']['name']
    mock_data['organization_id'] = mock_data['organization']['id']

    mock_data['dataset'] = factories.Dataset(owner_org=mock_data['organization_id'])
    mock_data['dataset_name'] = mock_data['dataset']['name']
    mock_data['package_id'] = mock_data['dataset']['id']

    mock_data['resource'] = factories.Resource(package_id=mock_data['package_id'])
    mock_data['resource_name'] = mock_data['resource']['name']
    mock_data['resource_id'] = mock_data['resource']['id']

    mock_data['resource_view'] = factories.ResourceView(
        resource_id=mock_data['resource_id'])
    mock_data['resource_view_title'] = mock_data['resource_view']['title']

    mock_data['context'] = {
        'user': factories._get_action_user_name(kwargs)
    }

    return mock_data