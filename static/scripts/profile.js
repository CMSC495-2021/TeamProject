$(function(){
	$('#profileButton').click(function(){
    alert("Dots pressed!");
		// var user = $('#inputUsername').val();
		// var pass = $('#inputPassword').val();
		$.ajax({
			url: '/testUrl',
			data: $('form').serialize(),
			type: 'POST',
			success: function(response){
				console.log(response);
			},
			error: function(error){
				console.log(error);
			}
		});
	});
});