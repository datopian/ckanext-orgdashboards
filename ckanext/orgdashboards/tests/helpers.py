''' Helper methods for tests '''

import string
import random
import requests
import os

from pylons import config

from ckan.tests import factories

mock_map_properties = {
    'Block Operators ': 'Berlanga Holding ',
    'Areas of operation': 'Mottama',
    'Myanmar Block': 'M-8',
    'Address':
    '8 Temasek Boulevard, #08-01 Suntec Tower Three, Singapore 038988 '
}


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
    mock_data['resource_view_id'] = mock_data['resource_view']['id']

    mock_data['context'] = {
        'user': factories._get_action_user_name(kwargs)
    }

    return mock_data


def id_generator(size=6, chars=string.ascii_lowercase + string.digits):
    ''' Create random id which is a combination of letters and numbers '''

    return ''.join(random.choice(chars) for _ in range(size))


def upload_json_resource(dataset_name, resource_name):
    sysadmin = factories.Sysadmin()
    resource = factories.Resource(name=resource_name)
    file_path = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), 'data.geojson')
    site_base_url = get_site_base_url()

    data_dict = {
        'package_id': dataset_name,
        'name': resource['name'],
        'url': 'test_url',
        'format': 'geojson'
    }

    # Upload resource
    response = requests.post(
        '{0}/api/action/resource_create'.format(site_base_url),
        data=data_dict,
        headers={'X-CKAN-API-Key': sysadmin['apikey']},
        files=[('upload', file(file_path))])

    return response.json()['result']


def get_site_base_url():
    return config.get('ckan.site_url', 'http://localhost:5000')
