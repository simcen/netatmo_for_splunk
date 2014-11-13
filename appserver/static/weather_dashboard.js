require(['jquery', 'underscore', 'splunkjs/mvc','splunkjs/mvc/utils','splunkjs/mvc/simplexml/ready!'], function($, _, mvc, utils){

	var submittedTokens = mvc.Components.getInstance('submitted');
	console.debug("submittedTokens", submittedTokens);

	var searchManager = mvc.Components.getInstance(mvc.Components.getInstance('pressure').managerid)
	var pressureData = searchManager.data('results', {
    	output_mode: 'json_rows',
    	count: 0
	});

	pressureData.on('data', function(results) { 
		if (!pressureData.hasData()) {
        	return;
    	}
    	var fields = _.map(results.collection().toJSON(), function(item) { return { pressure_area : item.pressure_area}; });
    	console.debug("fields", fields);
    	$("#pressure_icon").remove();
    	$("#pressure .panel-body").prepend('<div id="pressure_icon"><img src="/static/app/netatmo/' + fields[0].pressure_area +'.png" alt="'+ fields[0].pressure_area +' pressure area" /></div>');
	});

});