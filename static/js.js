window.onload = (function(){ 
  VK.init(function() { 
	VK.loadParams(document.location.href);
	var params = { 
		type: 'votes', 
		votes:3
	}; 
	$( "#pay" ).click(function() {
				VK.callMethod('showOrderBox', params); 
		});
	}, function() {
	}, '5.53')
});