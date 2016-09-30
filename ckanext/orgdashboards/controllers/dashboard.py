import logging
from logging import getLogger
from urllib import urlencode

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.lib.plugins as lib_plugins

from ckan.common import OrderedDict, _, json, request, c, g, response
from ckan.controllers.package import (PackageController,
                                      url_with_params,
                                      _encode_params)

from pylons import config
from paste.deploy.converters import asbool

import ckan.logic as logic
import ckan.lib.base as base
import ckan.lib.maintain as maintain
import ckan.lib.helpers as h
import ckan.model as model
import ckan.plugins as p
import ckan.lib.render

log = logging.getLogger(__name__)

render = base.render
abort = base.abort
redirect = base.redirect

NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
check_access = logic.check_access
get_action = logic.get_action
tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params
flatten_to_string_key = logic.flatten_to_string_key

lookup_package_plugin = ckan.lib.plugins.lookup_package_plugin

logger = getLogger(__name__)

class DashboardsController(PackageController):
    def organization_dashboard(self, name):
        org = get_action('organization_show')({}, {'id': name, 'include_extras': True})

        if 'orgdashboards_is_active' in org and org['orgdashboards_is_active'] == '0':
            return plugins.toolkit.render('dashboards/snippets/not_active.html')

        from ckan.lib.search import SearchError

        package_type = 'dataset'

        try:
            context = {'model': model, 'user': c.user or c.author,
                       'auth_user_obj': c.userobj}
            check_access('site_read', context)
        except NotAuthorized:
            abort(401, _('Not authorized to see this page'))

        # unicode format (decoded from utf8)
        q = c.q = request.params.get('q', u'')
        c.query_error = False
        page = self._get_page_number(request.params)

        try:
            limit = int(org['orgdashboards_datasets_per_page'])
        except KeyError, ValueError:
            limit = int(config.get('ckanext.orgdashboards.datasets_per_page'), 6)

        # most search operations should reset the page counter:
        params_nopage = [(k, v) for k, v in request.params.items()
                         if k != 'page']

        def drill_down_url(alternative_url=None, **by):
            return h.add_url_param(alternative_url=alternative_url,
                                   controller='package', action='search',
                                   new_params=by)

        c.drill_down_url = drill_down_url

        def remove_field(key, value=None, replace=None):
            return h.remove_url_param(key, value=value, replace=replace,
                                      controller='package', action='search')

        c.remove_field = remove_field

        sort_by = request.params.get('sort', None)
        params_nosort = [(k, v) for k, v in params_nopage if k != 'sort']

        def _sort_by(fields):
            """
            Sort by the given list of fields.

            Each entry in the list is a 2-tuple: (fieldname, sort_order)

            eg - [('metadata_modified', 'desc'), ('name', 'asc')]

            If fields is empty, then the default ordering is used.
            """
            params = params_nosort[:]

            if fields:
                sort_string = ', '.join('%s %s' % f for f in fields)
                params.append(('sort', sort_string))
            return search_url(params, package_type)

        c.sort_by = _sort_by
        if not sort_by:
            c.sort_by_fields = []
        else:
            c.sort_by_fields = [field.split()[0]
                                for field in sort_by.split(',')]

        def pager_url(q=None, page=None):
            params = list(params_nopage)
            params.append(('page', page))
            return search_url(params, package_type)

        c.search_url_params = urlencode(_encode_params(params_nopage))

        try:
            c.fields = []
            # c.fields_grouped will contain a dict of params containing
            # a list of values eg {'tags':['tag1', 'tag2']}
            c.fields_grouped = {}
            search_extras = {}
            fq = ''
            for (param, value) in request.params.items():
                if param not in ['q', 'page', 'sort'] \
                        and len(value) and not param.startswith('_'):
                    if not param.startswith('ext_'):
                        c.fields.append((param, value))
                        fq += ' %s:"%s"' % (param, value)
                        if param not in c.fields_grouped:
                            c.fields_grouped[param] = [value]
                        else:
                            c.fields_grouped[param].append(value)
                    else:
                        search_extras[param] = value

            context = {'model': model, 'session': model.Session,
                       'user': c.user or c.author, 'for_view': True,
                       'auth_user_obj': c.userobj}

            if package_type and package_type != 'dataset':
                # Only show datasets of this particular type
                fq += ' +dataset_type:{type}'.format(type=package_type)
            else:
                # Unless changed via config options, don't show non standard
                # dataset types on the default search page
                if not asbool(
                        config.get('ckan.search.show_all_types', 'False')):
                    fq += ' +dataset_type:dataset'

            facets = OrderedDict()

            default_facet_titles = {
                'organization': _('Organizations'),
                'groups': _('Groups'),
                'tags': _('Tags'),
                'res_format': _('Formats'),
                'license_id': _('Licenses'),
            }

            for facet in g.facets:
                if facet in default_facet_titles:
                    facets[facet] = default_facet_titles[facet]
                else:
                    facets[facet] = facet

            # Add 'author' facet
            facets['author'] = _('Authors')

            # Facet titles
            for plugin in p.PluginImplementations(p.IFacets):
                facets = plugin.dataset_facets(facets, package_type)

            c.facet_titles = facets

            fq += ' +organization:"{}"'.format(name)

            data_dict = {
                'q': q,
                'fq': fq.strip(),
                'facet.field': facets.keys(),
                'rows': limit,
                'start': (page - 1) * limit,
                'sort': sort_by,
                'extras': search_extras
            }

            query = get_action('package_search')(context, data_dict)

            # Override the "author" list, to include full name authors
            query['search_facets']['author']['items'] = self._get_full_name_authors(context, name)

            c.sort_by_selected = query['sort']

            c.page = h.Page(
                collection=query['results'],
                page=page,
                url=pager_url,
                item_count=query['count'],
                items_per_page=limit
            )
            c.facets = query['facets']
            c.search_facets = query['search_facets']
            c.page.items = query['results']
        except SearchError, se:
            log.error('Dataset search error: %r', se.args)
            c.query_error = True
            c.facets = {}
            c.search_facets = {}
            c.page = h.Page(collection=[])
        c.search_facets_limits = {}
        for facet in c.search_facets.keys():
            try:
                limit = int(request.params.get('_%s_limit' % facet,
                                               g.facets_default_number))
            except ValueError:
                abort(400, _('Parameter "{parameter_name}" is not '
                             'an integer').format(
                    parameter_name='_%s_limit' % facet))
            c.search_facets_limits[facet] = limit

        maintain.deprecate_context_item(
            'facets',
            'Use `c.search_facets` instead.')

        self._setup_template_variables(context, {},
                                       package_type=package_type)
        

        return plugins.toolkit.render('dashboards/index.html', extra_vars={'organization': org,
                                                                           'dataset_type': package_type})
        
    def orgdashboards_render_tpl(self, name, extra_vars=None):
        from ckan.lib.base import render_jinja2
        return render_jinja2(name, extra_vars)


    def _get_resourceview_resource_package(self, resource_view_id):
        data_dict = {
            'id': resource_view_id
        }
        resource_view = toolkit.get_action('resource_view_show')({}, data_dict)

        data_dict = {
            'id': resource_view['resource_id']
        }
        resource = toolkit.get_action('resource_show')({}, data_dict)

        data_dict = {
            'id': resource['package_id']
        }
        package = toolkit.get_action('package_show')({}, data_dict)

        return [resource_view, resource, package]

    def _get_full_name_authors(self, context, name):

        # "rows" is set to a big number because by default Solr will
        # return only 10 rows, and we need all datasets
        all_packages_dict = {
            'fq': '+dataset_type:dataset +organization:' + name,
            'rows': 10000000
        }

        # Find all datasets for the current organization (country)
        datasets_query = get_action('package_search')(context, 
                                                     all_packages_dict)

        full_name_authors = set()
        authors_list = []

        for dataset in datasets_query['results']:
            full_name_authors.add(dataset['author'])

        for author in full_name_authors:
            authors_list.append({
                'name': author, 
                'display_name': author, 
                'count': 1
            })

        return authors_list