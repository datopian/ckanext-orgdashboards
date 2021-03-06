$(function () {
  $('.orgdashboards-filters').on('change', function () {
    var url = $(this).val();
    if (url) {
      window.location = url + '#search-data';
    }
    return false;
  });

 $(document).ready(function(){

     var disclaimerText = $('.hero-info .media-body');
     var disclaimerContainer = $('.media.hero-info');

     $('#newly-released-data-btn').on('click', function () {
         console.log('detected click');
         if ($('#newly-released-data').hasClass('hidden')) {
             $('#newly-released-data-btn').html('');
             $('#newly-released-data').removeClass('hidden');
             $('#newly-released-data-btn').html('<i class="fa fa-compress pull-right"></i>');

         }
         else {
             $('#newly-released-data-btn').html('');
             $('#newly-released-data').addClass('hidden');
             $('#newly-released-data-btn').html('<i class="fa fa-expand pull-right"></i>');
         }
     });

     // Click handler for the disclaimer icon.
     $('.hero-info > .media-left').click(function onMapDisclaimerClick(event) {
         var bodyWidth = $('body').outerWidth();
         var topPosition;

         if (disclaimerText.hasClass('hidden')) {
             topPosition = bodyWidth <= 976 ? '790px' : '295px';

             disclaimerText.removeClass('hidden');
             disclaimerContainer.css({
                 'width': '300px',
                 'padding': '10px',
             });
         } else {
             topPosition = bodyWidth <= 976 ? '905px' : '410px';

             disclaimerText.addClass('hidden');
             disclaimerContainer.css({
                 'width': '54px',
                 'padding': '2px',
             });
         }
     });

     _setActiveLanguage();

     // Enable toggling of Extension descriptions
     $('.dashboard-description .more-link').click(function (e) {
         e.preventDefault(); // Prevents other scripts from triggering window.scroll();
         $(this).parent().parent().parent().children('.description-short').toggleClass('hidden');
         $(this).parent().parent().parent().children('.description-full').toggleClass('hidden');
     });

     if ($('#survey_popup').length) {
         var cookie = Cookies.get('survey_popup');
         var survey_popup_link = $('.survey_link').attr('href');
         var pathname = window.location.pathname;
         var paths = pathname.split('/');
         var country = paths.reverse()[1];
         var survey_popup = $('#survey_popup').popup({
             type: 'overlay',
             outline: true,
             scrolllock: true,
             transition: 'all 0.3s',
             closeelement: '#survey_popup_close',
             blur: false,
             onclose: function () {
                 Cookies.set('survey_popup', country + survey_popup_link, { expires: 365 });
             }
         });

         if (!cookie || cookie !== country + survey_popup_link) {
            $('#survey_popup').removeClass('hidden');
            survey_popup.popup('show');

            Cookies.set('survey_popup', country + survey_popup_link, { expires: 365 });

             $('#survey_link_button').click(function() {
                 $('#survey_popup').popup('hide');
             });
         }
     }

    _setFocusOnSelectFormControls();
  });

});

function toggleResources(resourceId) {
  $('#' + resourceId).toggleClass('hidden');
}

/*
 * Set the active language in the language picker
 * based on the active locale
 */
function _setActiveLanguage() {
  var languageSelector = $('.language-selector');
  var currentLanguage = $('html').attr('lang');
  var languageElement;
  
  if (currentLanguage === 'en') {
    languageElement = languageSelector.find('li')[0];
  } else {
    languageElement = languageSelector.find('li')[1];
  }

  if (languageElement) {
    languageElement.className = 'active';
  }
}

function _setFocusOnSelectFormControls() {
  var baseColor = $('.all-data > .data-block-header')[0].style.background;
  var rule = ['border-color: ' + baseColor + ';',
              'outline: 0;', 
              'box-shadow: inset 0 1px 1px rgba(0, 0, 0, .075), 0 0 3px ' + baseColor + ';'].join('');
  var organization = window.location.pathname.split('/').reverse()[1];

  // Check whether there is already a rule set for the current organization
  if (!_ruleExists('.' + organization + ':focus')) {
    _addCssRule('select.form-control:focus', rule);
  }
}

function _addCssRule(selector, rule) {
  if (document.styleSheets) {
    if (!document.styleSheets.length) {
      var head = document.getElementsByTagName('head')[0];
      head.appendChild(bc.createEl('style'));
    }

    var i = document.styleSheets.length-1;
    var ss = document.styleSheets[i];
    var l = 0;

    if (ss.cssRules) {
      l = ss.cssRules.length;
    } else if (ss.rules) {
      // IE
      l = ss.rules.length;
    }

    if (ss.insertRule) {
      ss.insertRule(selector + ' {' + rule + '}', l);
    } else if (ss.addRule) {
      // IE
      ss.addRule(selector, rule, l);
    }
  }
};

function _ruleExists(selector) {
  var rules = [];

  $.each(document.styleSheets, function(value, key) {
    if (key.href && key.href.indexOf('style.css') > -1) {
      rules = key.rules;
      return false;
    }
  });

  for (var i = 0; i < rules.length; i++) {
    if (rules[i].selectorText === selector) {
      return true;
    }
  }
}
