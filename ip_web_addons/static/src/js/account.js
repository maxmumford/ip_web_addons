$(document).ready(function () {

	// instantiate jquery ui tabs widget
    $(function() {
        $( "#tabs" ).tabs();
    });

    // set on_change for interval and end_date fields
    $('input.interval, input.end_date').change(function (){
    	// get elements, id and values
    	var element = $(this);
    	var auto_ship_id = element.closest("*[data-auto-ship-id]").attr('data-auto-ship-id');
    	var interval = $('*[data-auto-ship-id="' + auto_ship_id + '"] .interval').val();
    	var end_date = $('*[data-auto-ship-id="' + auto_ship_id + '"] .end_date').val();
    	var elem_number_remaining = $('*[data-auto-ship-id="' + auto_ship_id + '"] .number_remaining');

    	// validate
    	interval = $.isNumeric(interval) ? interval : 0;
    	end_date = end_date.length > 0 ? end_date : null;

    	if(interval < 1 || end_date == null) {
    		elem_number_remaining.html('');
    		return;
    	}

    	// make ajax call to calculate number remaining
    	$.ajax({
		    url: "/account/number-remaining/" + interval + '/' + end_date
		}).done(function(number_remaining) {
	    	// set number remaining field
	    	elem_number_remaining.html(number_remaining);
		});
    });

    // set update button onclick
    $('a.update').click(function(){
    	// get elements, id and values
    	var element = $(this);
    	var auto_ship_id = element.closest("*[data-auto-ship-id]").attr('data-auto-ship-id');
    	var interval = $('*[data-auto-ship-id="' + auto_ship_id + '"] .interval').val();
    	var end_date = $('*[data-auto-ship-id="' + auto_ship_id + '"] .end_date').val();

    	// validate
    	interval = $.isNumeric(interval) ? interval : 0;
    	end_date = end_date.length > 0 ? end_date : null;

    	if(interval < 1 || end_date == null) {
    		elem_number_remaining.html('');
    		return;
    	}

    	// send update 
    	$.ajax({
		    url: "/account/auto-ship/update/" + auto_ship_id,
		    type: 'POST',
		    data: {interval: interval, end_date: end_date},
		}).done(function(response) {
	    	alert(response);
		}).fail(function(request, response){
			alert("There was an error while saving - please check the form fields");
		});
    });

    // set delete button onclick
    $('a.delete').click(function(){
    	// get elements and id
    	var element = $(this);
    	var parent = element.closest("*[data-auto-ship-id]");
    	var auto_ship_id = parent.attr('data-auto-ship-id');

    	// send deactivation request 
    	$.ajax({
		    url: "/account/auto-ship/delete/" + auto_ship_id,
		    async: false
		}).done(function(response) {
	    	window.location.href = '/account/#auto-ships';
	    	location.reload();
		}).fail(function(request, response){
			alert("There was an error while deactivating, please get in contact so we can fix the problem");
		});
    });
 	
});
