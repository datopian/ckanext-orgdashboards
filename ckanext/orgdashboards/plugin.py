import logging

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.lib.plugins as lib_plugins
import ckanext.orgdashboards.helpers as helpers
from ckan.lib.plugins import DefaultTranslation
from ckan import model as m
from sqlalchemy import and_

from routes.mapper import SubMapper
from pylons import config

log = logging.getLogger(__name__)

class OrgDashboardsPlugin(plugins.SingletonPlugin, 
    lib_plugins.DefaultOrganizationForm, DefaultTranslation):
    
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IGroupForm, inherit=True)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IFacets, inherit=True)
    plugins.implements(plugins.ITranslation)

    ## IRoutes

    def before_map(self, map):
        # Define dashboard controller routes

        organization_entity_name = config.get(
            'ckanext.orgdashboards.organization_entity_name', 
            'organization')
        
        ctrl = 'ckanext.orgdashboards.controllers.dashboard:DashboardsController'
        map.connect('/', controller=ctrl, action='show_dashboard_by_domain')

        map.connect('/' + organization_entity_name + '/{name}/dashboard', controller=ctrl,
                    action='preview_dashboard')
            
        return map

    ## IGroupForm

    def is_fallback(self):
        return False
    
    def group_types(self):
        return ['organization']

    def form_to_db_schema_options(self, options):
        ''' This allows us to select different schemas for different
        purpose eg via the web interface or via the api or creation vs
        updating. It is optional and if not available form_to_db_schema
        should be used.
        If a context is provided, and it contains a schema, it will be
        returned.
        '''
        schema = options.get('context', {}).get('schema', None)
        if schema:
            return schema

        if options.get('api'):
            if options.get('type') == 'create':
                return self.form_to_db_schema_api_create()
            else:
                return self.form_to_db_schema_api_update()
        else:
            return self.form_to_db_schema()

    def form_to_db_schema_api_create(self):
        schema = super(OrgDashboardsPlugin, self).form_to_db_schema_api_create()
        schema = self._modify_group_schema(schema)
        return schema

    def form_to_db_schema_api_update(self):
        schema = super(OrgDashboardsPlugin, self).form_to_db_schema_api_update()
        schema = self._modify_group_schema(schema)
        return schema

    def form_to_db_schema(self):
        schema = super(OrgDashboardsPlugin, self).form_to_db_schema()
        schema = self._modify_group_schema(schema)
        return schema

    def _modify_group_schema(self, schema):

        # Import core converters and validators
        _convert_to_extras = toolkit.get_converter('convert_to_extras')
        _ignore_missing = toolkit.get_validator('ignore_missing')
        
        default_validators = [_ignore_missing,_convert_to_extras]

        schema.update({
            'orgdashboards_header': default_validators,
            'orgdashboards_footer': default_validators,
            'orgdashboards_description': default_validators,
            'orgdashboards_copyright': default_validators,
            'orgdashboards_dashboard_url': [_ignore_missing,_convert_to_extras,_domain_validator],
            'orgdashboards_lang_is_active': default_validators,
            'orgdashboards_base_color': default_validators,
            'orgdashboards_secondary_color': default_validators,
            'orgdashboards_is_active': default_validators,
            'orgdashboards_datasets_per_page': default_validators,
            'orgdashboards_charts': default_validators,
            'orgdashboards_map': default_validators,
            'orgdashboards_map_main_property': default_validators,
            'orgdashboards_main_color': default_validators,
            'orgdashboards_new_data_color': default_validators,
            'orgdashboards_all_data_color': default_validators,
            'orgdashboards_secondary_dashboard': default_validators,
            'orgdashboards_secondary_language': default_validators,
            'orgdashboards_survey_enabled': default_validators,
            'orgdashboards_survey_text': default_validators,
            'orgdashboards_survey_link': default_validators
        })
        
        charts = {}
        for _ in range(1, 7):
            charts.update({'orgdashboards_chart_{idx}'.format(idx=_): default_validators,
                           'orgdashboards_chart_{idx}_subheader'.format(idx=_): default_validators})
            
        schema.update(charts)
        return schema

    def db_to_form_schema(self):

        # Import core converters and validators
        _convert_from_extras = toolkit.get_converter('convert_from_extras')
        _ignore_missing = toolkit.get_validator('ignore_missing')
        _ignore = toolkit.get_validator('ignore')
        _not_empty = toolkit.get_validator('not_empty')

        schema = super(OrgDashboardsPlugin, self).form_to_db_schema()

        default_validators = [_convert_from_extras, _ignore_missing]
        schema.update({
            'orgdashboards_header': default_validators,
            'orgdashboards_footer': default_validators,
            'orgdashboards_description': default_validators,
            'orgdashboards_copyright': default_validators,
            'orgdashboards_lang_is_active': default_validators,
            'orgdashboards_dashboard_url': [_convert_from_extras, _ignore_missing,_domain_validator],
            'orgdashboards_base_color': default_validators,
            'orgdashboards_secondary_color': default_validators,
            'orgdashboards_is_active': default_validators,
            'orgdashboards_datasets_per_page': default_validators,
            'orgdashboards_charts': default_validators,
            'orgdashboards_map': default_validators,
            'orgdashboards_map_main_property': default_validators,
            'orgdashboards_main_color': default_validators,
            'orgdashboards_new_data_color': default_validators,
            'orgdashboards_all_data_color': default_validators,
            'orgdashboards_secondary_dashboard': default_validators,
            'orgdashboards_secondary_language': default_validators,
            'orgdashboards_survey_enabled': default_validators,
            'orgdashboards_survey_text': default_validators,
            'orgdashboards_survey_link': default_validators,
            'num_followers': [_not_empty],
            'package_count': [_not_empty],
        })
        
        charts = {}
        for _ in range(1, 7):
            charts.update({'orgdashboards_chart_{idx}'.format(idx=_): default_validators,
                           'orgdashboards_chart_{idx}_subheader'.format(idx=_): default_validators})
            
        schema.update(charts)
        return schema
    
    ## IActions

    def get_actions(self):

        module_root = 'ckanext.orgdashboards.logic.action'
        action_functions = _get_logic_functions(module_root)

        return action_functions

    def get_helpers(self):
        return {
            'orgdashboards_get_newly_released_data':
                helpers.orgdashboards_get_newly_released_data,
            'orgdashboards_convert_time_format':
                helpers.orgdashboards_convert_time_format,
            'orgdashboards_replace_or_add_url_param':
                helpers.orgdashboards_replace_or_add_url_param,
            'orgdashboards_get_organization_list':
                helpers.orgdashboards_get_organization_list,
            'orgdashboards_get_chart_resources':
                helpers.get_resourceview_resource_package,
            'orgdashboards_get_org_map_views': 
                helpers.org_views.get_maps,
            'orgdashboards_get_resource_url':
                helpers.orgdashboards_get_resource_url,
            'orgdashboards_get_geojson_properties': 
                helpers.orgdashboards_get_geojson_properties,
            'orgdashboards_get_resource_view_url':
                lambda id, dataset: '/dataset/{0}/resource/{1}'\
                                    .format(dataset, id),
            'orgdashboards_get_all_organizations':
                helpers.orgdashboards_get_all_organizations,
            'orgdashboards_get_available_languages':
                helpers.orgdashboards_get_available_languages,
            'orgdashboards_convert_to_list':
                helpers.orgdashboards_convert_to_list,
            'orgdashboards_get_resource_names_from_ids':
                helpers.orgdashboards_get_resource_names_from_ids,
            'orgdashboards_smart_truncate':
                helpers.orgdashboards_smart_truncate,
            'orgdashboards_get_secondary_language':
                helpers.orgdashboards_get_secondary_language,
            'orgdashboards_get_current_url':
                helpers.orgdashboards_get_current_url,
            'orgdashboards_get_country_short_name':
                helpers.orgdashboards_get_country_short_name,
            'orgdashboards_get_secondary_dashboard':
                helpers.orgdashboards_get_secondary_dashboard,
            'orgdashboards_resource_show_map_properties':
                helpers.orgdashboards_resource_show_map_properties,
            'orgdashboards_get_organization_entity_name':
                helpers.orgdashboards_get_organization_entity_name,
            'orgdashboards_get_group_entity_name':
                helpers.orgdashboards_get_group_entity_name,
            'orgdashboards_get_facet_items_dict':
                helpers.orgdashboards_get_facet_items_dict
        }
        
    ## IConfigurer
    
    def update_config(self, config):
        toolkit.add_template_directory(config, 'templates')
        toolkit.add_resource('fanstatic', 'orgdashboards')
        toolkit.add_public_directory(config, 'public')
        
def _get_logic_functions(module_root, logic_functions = {}):
    module = __import__(module_root)
    for part in module_root.split('.')[1:]:
        module = getattr(module, part)

    for key, value in module.__dict__.items():
        if not key.startswith('_') and  (hasattr(value, '__call__')
                    and (value.__module__ == module_root)):
            logic_functions[key] = value
            
    return logic_functions
        
def _domain_validator(key, data, errors, context):

    session = context['session']
    group_name = data[('name',)]

    if not data[key]:
        return

    query = session.query(m.Group) \
        .join((m.GroupExtra, m.Group.id == m.GroupExtra.group_id)) \
        .filter(and_(m.GroupExtra.key == 'orgdashboards_dashboard_url',
                     m.GroupExtra.value == data[key],
                     m.Group.name != group_name))

    result = query.first()

    if result:
        errors[key].append(
            toolkit._('Domain name already exists in database'))