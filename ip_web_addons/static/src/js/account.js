$(document).ready(function () {

	// instantiate jquery ui tabs widget
    $(function() {
        if(jQuery.ui != undefined)
            $( "#tabs" ).tabs();
        else
            console.log("jQuery is not loaded so cannot setup tabs");
    });

    // set on_change for interval and end_date fields
    $('input.interval, input.end_date').change(function (){
    	// get elements, id and values
    	var element = $(this);
    	var auto_ship_id = element.closest("*[data-auto-ship-id]").attr('data-auto-ship-id');
    	var interval = $('*[data-auto-ship-id="' + auto_ship_id + '"] .interval').val();
    	var end_date = $('*[data-auto-ship-id="' + auto_ship_id + '"] .end_date').val();
    	var elem_number_remaining = $('*[data-auto-ship-id="' + auto_ship_id + '"] .number_remaining');

    	// make ajax call to calculate number remaining
    	$.ajax({
		    url: "/account/number-remaining/" + interval + '/' + end_date,
            dataType: 'JSON',
		}).done(function(response) {
	    	if(response.status == "fail")
                elem_number_remaining.html('');
            else if(response.status == "success")
                elem_number_remaining.html(response.data.number_remaining);
            else if(response.status == "error")
	    	    elem_number_remaining.html('');
		});
    });

    // set update button onclick
    $('a.update').click(function(){
    	// get elements, id and values
    	var element = $(this);
    	var auto_ship_id = element.closest("*[data-auto-ship-id]").attr('data-auto-ship-id');
    	var interval = $('*[data-auto-ship-id="' + auto_ship_id + '"] .interval').val();
    	var end_date = $('*[data-auto-ship-id="' + auto_ship_id + '"] .end_date').val();

    	// send update 
    	$.ajax({
		    url: "/account/auto-ship/update/" + auto_ship_id,
		    type: 'POST',
            dataType: 'json',
		    data: {interval: interval, end_date: end_date},
		}).done(function(response) {
	    	if(response.status == "fail")
                alert("The field " + Object.keys(response.data)[0] + " has a problem: " + response.data[Object.keys(response.data)[0]]);
            else if(response.status == "success")
                alert("Saved successfully");
            else if(response.status == "error")
                alert(response.message);
		}).fail(function(request, response){
			alert("There was a problem with the request");
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
