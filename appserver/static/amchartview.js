require.config({
	paths: {
        "app": "../app"
    },
    shim: {
        "app/splunk6dev/amcharts/amcharts": {
            deps: [],
            exports: "AmCharts"
        },
        "app/splunk6dev/amcharts/serial": {
            deps: ["app/splunk6dev/amcharts/amcharts"],
            exports: "AmCharts.AmSerialChart"
        },
    }
});

define(function(require, exports, module) {
	
    var _ = require('underscore');
    var $ = require('jquery');
    var mvc = require('splunkjs/mvc');
    var SimpleSplunkView = require('splunkjs/mvc/simplesplunkview');
    var AmCharts = require('app/splunk6dev/amcharts/amcharts');
  	require('app/splunk6dev/amcharts/serial');

	var AmChartView = SimpleSplunkView.extend({
        className: "amchartview",

        // Set options for the visualization
        options: {
            data: "preview",  // The data results model from a search
        },
        output_mode: 'json',

       
        createView: function() { 
        	console.log("createView");
        	return { container: this.$el, } ;
        },

        updateView: function(viz, data) {

          console.log("updateView", data);

          this.$el.empty();

          var id = _.uniqueId("amchart");
          $('<div />').attr('id', id).height(this.settings.get('height')).width(this.settings.get('width')).appendTo(this.$el);
          //debugger;
	      var chart = AmCharts.makeChart('chartdiv', {
				"type": "serial",
			    "rotate": true,
			    "theme": "none",
			    "columnSpacing": 0.3,
			    "legend": {
			        "horizontalGap": 10,
			        "maxColumns": 1,
			        "position": "right",
					"useGraphSettings": true,
					"markerSize": 10
			    },
			    "valueAxes": [{
			        "axisAlpha": 0.3,   
			        "minimum": -10,
			    }],
			    "dataProvider": data,
			    "graphs": [{
			        "balloonText": "Gestern:[[value]]",
			        "fillAlphas": 0.8,
			        "lineAlpha": 0.2,
			        "title": "Gestern",
			        "type": "column",
			        "valueField": "yesterday",
			        "fillColors": "#cccccc",
			        "lineColor": "#cccccc",
			    }, {
			        "balloonText": "Vorgestern:[[value]]",
			        "fillAlphas": 0.8,
			        "lineAlpha": 0.2,
			        "title": "Vorgestern",
			        "type": "column",
			        "valueField": "tdby",
			        "fillColors": "#333333",
			        "lineColor": "#333333",
			    }, {
			        "balloonText": "Differenz:[[value]]",
			        "fillAlphas": 0.8,
			        "lineAlpha": 0.2,
			        "title": "Unterschied",
			        "type": "column",
			        "valueField": "difference",
			        "fillColors": "#cc3333",
			        "lineColor": "#cc3333",
			        "fillColorsField": this.settings.get('colorField'),
			    }],
			    "categoryField": "device",
			    "categoryAxis": {
			        "gridPosition": "start",
			        "axisAlpha": 0,
			        "gridAlpha": 0,
			        "position": "left"
			    },
			    
			});
			chart.write(id);
			console.debug("chart", chart);

        },

        // Override this method to format the data for the view
        formatData: function(data) {
        	console.log("formatData");

            var valueField1 = this.settings.get('valueField1');
            var valueField2 = this.settings.get('valueField2');
            var valueField3 = this.settings.get('valueField3');
            var categoryField = this.settings.get('categoryField');
            var colorField = this.settings.get('colorField');

            amData = []

             _(data).chain().map(function(result) {
             	return {
             		"device": result[categoryField],
			        "yesterday": result[valueField1],
			        "tdby": result[valueField2],
			        "difference": result[valueField3],
			        "color": result[colorField],
                };
             }).each(function(result) {
             	amData.push(result);
             });

            return amData;
        },

    });
    return AmChartView;
});