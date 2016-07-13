(function () {
  'use strict';
  var api = {
    get: function (action, params, api_ver=3) {
      var base_url = ckan.sandbox().client.endpoint;
      params = $.param(params);
      var url = base_url + '/api/' + api_ver + '/action/' + action + '?' + params;
      return $.getJSON(url);
    },
    post: function (action, data, api_ver=3) {
      var base_url = ckan.sandbox().client.endpoint;
      var url = base_url + '/api/' + api_ver + '/action/' + action;
      return $.post(url, JSON.stringify(data), "json");
    }
  };

  $(document).ready(function () {
    var url = window.location.pathname;
    var name = url.substr(url.lastIndexOf('/') + 1);

    // Fetch and populate datasets dropdowns

    api.get('orgdashboards_show_datasets', {id: name}).done(function (data) {
      var inputs = $('[id*=chart_dataset_]');
      $.each(data.result, function (idx, elem) {
        inputs.append(new Option(elem.title, elem.name));
      });

      // Dataset event handlers
      var dataset_name;
      inputs.on('change', function () {
        var elem = $(this);
        dataset_name = elem.find(":selected").val();
        var dataset_select_id = elem.attr('id');
        var resource_select_id = dataset_select_id.replace('dataset', 'resource');
        var resourceview_select_id = resource_select_id.replace('resource', 'resource_view');

        // Empty all child selects
        if ($('#' + resource_select_id + ' option').length > 0)
          $('#' + resource_select_id).find('option').not(':first').remove();

        $('#' + resourceview_select_id + '_preview').empty();

        // Fetch and populate resources drop down
        api.get('orgdashboards_dataset_show_resources', {id: dataset_name}).done(
          function (data) {

            var opts = $('#' + resource_select_id);
            $.each(data.result, function (idx, elem) {
              opts.append(new Option(elem.name, elem.id));
            });

            $('.' + resource_select_id).removeClass('hidden');
          });
      });

      // Resource event handlers

      var resource_id;
      var resource_inputs = $('[id*=chart_resource_]');
      resource_inputs.on('change', function () {

        var elem = $(this);
        resource_id = elem.find(":selected").val();
        var resource_select_id = elem.attr('id');
        var resourceview_select_id = resource_select_id.replace('resource', 'resourceview');

        if ($('#' + resourceview_select_id + ' option').length > 0)
          $('#' + resourceview_select_id).find('option').not(':first').remove();

        $('#' + resourceview_select_id + '_preview').html();

        api.get('orgdashboards_resource_show_resource_views', {id: resource_id}).done(
          function (data) {

            var opts = $('#' + resourceview_select_id);
            $.each(data.result, function (idx, elem) {
              opts.append(new Option(elem.title, elem.id));
            });

            $('.' + resourceview_select_id).removeClass('hidden');
          });
      });


      // Resource views event handlers

      var resourceview_inputs = $('[id*=chart_resourceview_]');
      resourceview_inputs.on('change', function () {

        var elem = $(this);
        var resourceview_id = elem.find(":selected").val();

        var resourceview_select_id = elem.attr('id');
        var chart_nr = resourceview_select_id.substr(resourceview_select_id.lastIndexOf('_') + 1);

        $('#org_dashboard_chart_' + chart_nr).val(resourceview_id)

        var base_url = ckan.sandbox().client.endpoint;
        var src = base_url + '/dataset/' + dataset_name + '/resource/' + resource_id + '/view/' + resourceview_id;

        ckan.sandbox().client.getTemplate('iframe.html', {source: src})
          .done(function (data) {

            $('#' + resourceview_select_id + '_preview').html();
            $('#' + resourceview_select_id + '_preview').html(data);
          });
      });
    });


    // Map select event handler

    function changeMainPropertyValues() {

      if ($('#org_dashboard_map_main_property option').length > 0)
        $('#org_dashboard_map_main_property').empty();

      // Get resource id
      var resource_id = $('#org_dashboard_map option:selected').val();
      var params = {id: resource_id};
      api.get('org_dashboard_resource_show_map_properties', params)
        .done(function (data) {

          var opts = $('#org_dashboard_map_main_property');
          $.each(data.result, function (idx, elem) {
            opts.append(new Option(elem.value, elem.value));
          });
          $('.org_dashboard_map_main_property').removeClass('hidden');

        });
    }

    if ($('#org_dashboard_map').val()) {
      changeMainPropertyValues();
    }

    $('#org_dashboard_map').on('change', function () {
      changeMainPropertyValues();
    });

    //Base color change event handler
    var secondary_element = $('#org_dashboard_secondary_color'),
        lighter_color;
    $('#org_dashboard_base_color').change(function () {
      lighter_color = ColorLuminance('#' + this.value, 0.4);
      secondary_element.val(lighter_color.substr(1));
      secondary_element.css({'background-color': lighter_color});
    });

    function ColorLuminance(hex, lum) {

      // validate hex string
      hex = String(hex).replace(/[^0-9a-f]/gi, '');
      if (hex.length < 6) {
        hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
      }
      lum = lum || 0;

      // convert to decimal and change luminosity
      var rgb = "#", c, i;
      for (i = 0; i < 3; i++) {
        c = parseInt(hex.substr(i * 2, 2), 16);
        c = Math.round(Math.min(Math.max(0, c + (c * lum)), 255)).toString(16);
        rgb += ("00" + c).substr(c.length);
      }

      return rgb;
    }

  });
})($);