$(document).ready(function () {

	$('.address-submit').click(function(){
		var form = $(this).closest('form');
		var data = form.serializeObject();

		// fix select2
		data.disease_ids = form.find('select[name=disease_ids]').val();
		if(Array.isArray(data.disease_ids))
			data.disease_ids = data.disease_ids.join();

    	$.ajax({
		    url: "/account/address/update",
            dataType: 'JSON',
            type: 'POST',
            data: data,
		}).done(function(response) {
	    	if(response.status == "fail")
                alert("The field " + Object.keys(response.data)[0] + " has a problem: " + response.data[Object.keys(response.data)[0]]);
            else if(response.status == "success")
                alert("Saved");
            else if(response.status == "error"){
            	alert("There was an error! Please refresh the page and try again, or come back later");
	    	    console.log(response);
            }

		});
	});

	$('.select2').select2();
 	
});
