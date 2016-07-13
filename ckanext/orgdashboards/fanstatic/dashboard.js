$(function () {
  $('.montrose-filters').on('change', function () {
    var url = $(this).val();
    if (url) {
      window.location = url + '#search-data';
    }
    return false;
  });

 $(document).ready(function(){
 	  $('#newly-released-data-btn').on('click', function(){
 	  	console.log('detected click');
 	  	if($('#newly-released-data').hasClass('hidden')){
 	  		$('#newly-released-data-btn').html('');
 	  		$('#newly-released-data').removeClass('hidden');
 	  		$('#newly-released-data-btn').html('<i class="fa fa-compress pull-right"></i>');

 	  	}
 	  	else{
 	  		$('#newly-released-data-btn').html('');
 	  		$('#newly-released-data').addClass('hidden');
 	  		$('#newly-released-data-btn').html('<i class="fa fa-expand pull-right"></i>');
 	  	}
 	  });
  });

});

function toggleResources(resourceId) {
  $('#' + resourceId).toggleClass('hidden');
}