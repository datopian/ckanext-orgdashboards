import logging
import os

from datetime import datetime
from urllib import urlencode
from urlparse import urlparse

from pylons import config

import ckan.plugins as p
import ckan.lib.helpers as h
import ckan.plugins.toolkit as toolkit

import ckan.logic as l
import ckan.model as model

from ckan.lib.base import request, response, render, abort
from ckan.common import OrderedDict, _, json, request, c, g, response
from ckan.logic.validators import resource_id_exists, package_id_exists

log = logging.getLogger(__name__)


# TODO: Re-organize and re-factor helpers

def _get_ctx():
    return {'model': model, 
            'session': model.Session,
            'user': 'sysadmin'}

def _get_action(action, context_dict, data_dict):
    return p.toolkit.get_action(action)(context_dict, data_dict)

def orgdashboards_get_newly_released_data(organization_name, limit=4):
    try:
        pkg_search_results = toolkit.get_action('package_search')(data_dict={
            'fq': ' organization:{}'.format(organization_name),
            'sort': 'metadata_modified desc',
            'rows': limit
        })['results']

    except toolkit.ValidationError, search.SearchError:
        return []
    else:
        pkgs = []
        for pkg in pkg_search_results:
            package = toolkit.get_action('package_show')(data_dict={
                'id': pkg['id']
            })
            modified = datetime.strptime(package['metadata_modified'].split('T')[0], '%Y-%m-%d')
            package['human_metadata_modified'] = modified.strftime("%d %B %Y")
            pkgs.append(package)
        return pkgs


def orgdashboards_convert_time_format(package):
    modified = datetime.strptime(package['metadata_modified'].split('T')[0], '%Y-%m-%d')
    return modified.strftime("%d %B %Y")


def orgdashboards_replace_or_add_url_param(name, value, params, controller, 
    action, context_name):
    for k, v in params:
        # Reset the page to the first one
        if k == 'page':
            params.remove((k, v))
            params.insert(0, ('page', '1'))
        if k != name:
            continue
        params.remove((k, v))

    params.append((name, value))

    if action == 'show_dashboard_by_domain':
        url = h.url_for(controller=controller, action=action)
    else:
        url = h.url_for(controller=controller, action=action, name=context_name)

    params = [(k, v.encode('utf-8') if isinstance(v, basestring) else str(v))
                  for k, v in params]
    return url + u'?' + urlencode(params)


def get_resourceview_resource_package(resource_view_id):
    if not resource_view_id:
        return None
    
    data_dict = {
        'id': resource_view_id
    }
    try:
        resource_view = toolkit.get_action('resource_view_show')({}, data_dict)
        
    except l.NotFound:
        return None
        

    data_dict = {
        'id': resource_view['resource_id']
    }
    resource = toolkit.get_action('resource_show')({}, data_dict)

    data_dict = {
        'id': resource['package_id']
    }
    
    try:
        package = toolkit.get_action('package_show')({}, data_dict)
        
    except l.NotFound:
        return None

    return [resource_view, resource, package]

def orgdashboards_get_organization_list():
    return _get_action('organization_list', {},
                      {'all_fields': True, 
                       'include_extras': True, 
                       'include_followers': True})

def orgdashboards_get_all_organizations(current_org_name):
    ''' Get all created organizations '''

    organizations = _get_action('organization_list', {}, {'all_fields': True})
    
    organizations = map(lambda item: 
                        {
                            'value': item['name'], 
                            'text': item['display_name']
                        }, 
                        organizations
                    )

    # Filter out the current organization in the list
    organizations = [x for x in organizations if x['value'] != current_org_name]

    organizations.insert(0, {'value': 'none', 'text': 'None'})

    return organizations

def orgdashboards_get_available_languages():   
    ''' Read the languages listed in a json file '''

    languages = []

    for locale in h.get_available_locales():
        languages.append({'value': locale, 'text': locale.english_name})

    languages.sort()

    languages.insert(0, {'value': 'none', 'text': 'None'})

    return languages

def get_organization_views(name, type='chart builder'):
    data = _get_action('organization_show',{},
                      {'id':name, 
                       'include_datasets': True})
        
    result = []
    package_names = data.pop('packages', [])
    if any(package_names):
        for _ in package_names:
            package = _get_action('package_show', {}, {'id': _['name']})
            if not package['num_resources'] > 0:
                continue
            
            if type == 'chart builder':
                resource_views = map(lambda p: _get_action('resource_view_list', {}, 
                                                          {'id': p['id']}), package['resources'])
                if any(resource_views):
                    map(lambda l: result.extend(filter(lambda i: i['view_type'].lower() == type, l)), resource_views)
                    
            elif type.lower() == 'maps':
                result.extend(filter(lambda r: r['format'].lower() in ['geojson', 'gjson'], package['resources']))
            
            else:
                pass
            # Raise not handled exception
            
    return result

def get_resource_views(package):
    result = []
    resource_views = map(lambda p: _get_action('resource_view_list', {}, 
                                              {'id': p['id']}), package['resources'])
    if any(resource_views):
        map(lambda l: result.extend(l), resource_views)
        
    return result
    

def get_dataset_resource_views(package_id):
    if not package_id_exists(package_id, _get_ctx()):
        return []
    
    dataset = _get_action('package_show', {}, {'id': package_id})
    return get_resource_views(dataset)
    
def get_dataset_chart_resource_views(package_id):
    if not package_id_exists(package_id, _get_ctx()):
        return []
    
    return filter(lambda i: i['view_type'] == 'Chart builder', 
                  get_dataset_resource_views(package_id))
    
class OrgViews(object):
    def __init__(self):
        self.charts_cache = {}
        self.maps_cache = {}
        
    def get_charts(self, name):
        allCharts = {}
        result = []
        for item in get_organization_views(name):
            result.append({'value': item['id'], 'text': item['title']})
            allCharts.update({name: result})

        return allCharts.get(name) or {}
    
    def get_maps(self, name):
        allMaps = {}
        result = [{'value': '', 'text': 'None'}]
        for item in get_organization_views(name, type='Maps'):
            is_private = self._is_dataset_private(item['package_id'])
            
            if is_private:
                continue

            if 'name' in item:
                text = item['name']
            elif 'description' in item:
                text = item['description']
            else:
                text = 'Unnamed resource'
            result.append({'value': item['id'], 'text': text})
            allMaps.update({name: result})

        return allMaps.get(name) or {}

    def _is_dataset_private(self, package_id):
        data_dict = {
            'id': package_id
        }
        package = _get_action('package_show', {}, data_dict)
        
        if 'private' in package and package['private'] == True:
            return True
        else:
            return False
        
org_views = OrgViews()

def orgdashboards_get_resource_url(id):
    if not resource_id_exists(id, _get_ctx()):
        return None
    
    data = _get_action('resource_show', {}, {'id': id})
    return data['url']

def orgdashboards_get_geojson_properties(resource_id):
    import requests
    
    url = orgdashboards_get_resource_url(resource_id)

    response = requests.get(url)    
    geojson = response.json()
        
    result = []
    for k, v in geojson.get('features')[0].get('properties').iteritems():
        result.append({'value':k, 'text': k})

    return result

def orgdashboards_resource_show_map_properties(id):
    return orgdashboards_get_geojson_properties(id)
           
def orgdashboards_convert_to_list(resources):
    if not resources.startswith('{'):
        return [resources]
    resources = resources[1:len(resources) - 1].split(',')
    for i in range(len(resources)):
        if resources[i].startswith('"'):
            resources[i] = resources[i][1:len(resources[i]) - 1]

    return resources


def orgdashboards_get_resource_names_from_ids(resource_ids):
    resource_names = []
    for resource_id in resource_ids:
        print resource_id
        resource_names.append(_get_action('resource_show', {}, {'id': resource_id})['name'])
    return resource_names


def orgdashboards_smart_truncate(text, length=800):
    if length > len(text):
        return text
    return text[:length].rsplit(' ', 1)[0]

def orgdashboards_get_secondary_language(organization_name):
    organization = _get_action('organization_show', {}, {'id': organization_name})

    if 'orgdashboards_secondary_language' in organization:
        return organization['orgdashboards_secondary_language']
    else:
        return 'none'

def orgdashboards_get_secondary_dashboard(organization_name):
    organization = _get_action('organization_show', {}, {'id': organization_name})

    if 'orgdashboards_secondary_dashboard' in organization:
        return organization['orgdashboards_secondary_dashboard']
    else:
        return 'none'

def orgdashboards_get_current_url(page, params, controller, action, name, exclude_param=''):

    if action == 'show_dashboard_by_domain':
        url = h.url_for(controller=controller, action=action)
    else:
        url = h.url_for(controller=controller, action=action, name=name)

    for k, v in params:
        if k == exclude_param:
            params.remove((k, v))

    params = [(k, v.encode('utf-8') if isinstance(v, basestring) else str(v))
              for k, v in params]

    if (params):
        url = url + u'?page=' + str(page) + '&' + urlencode(params)
    else:
        url = url + u'?page=' + str(page)

    return url

def orgdashboards_get_country_short_name(current_locale):
    for locale in h.get_available_locales():
        if current_locale == str(locale):
            return locale.english_name[:3]

def orgdashboards_get_organization_entity_name():
    return config.get('ckanext.orgdashboards.organization_entity_name', 
            'organization')

def orgdashboards_get_group_entity_name():
    return config.get('ckanext.orgdashboards.group_entity_name', 
            'group')

def orgdashboards_get_facet_items_dict(value):
    try:
        return h.get_facet_items_dict(value)
    except:
        return None

def orgdashboards_get_dashboard_url(org_name):

    org = _get_action('organization_show', {}, {'id': org_name})

    if 'orgdashboards_dashboard_url' in org and org['orgdashboards_dashboard_url'] != '':

        url = urlparse(org['orgdashboards_dashboard_url'])
        url = url.scheme + '://' + url.netloc

        return url
    else:
        return ''

def orgdashboards_get_config_option(key):
    return config.get(key)