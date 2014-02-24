require.config({
	paths: {
        "app": "../app"
    },
    shim: {
        "app/netatmo/amcharts/amcharts": {
            deps: [],
            exports: "AmCharts"
        },
        "app/netatmo/amcharts/serial": {
            deps: ["app/netatmo/amcharts/amcharts"],
            exports: "AmCharts.AmSerialChart"
        },
    }
});

define(function(require, exports, module) {
	
    var _ = require('underscore');
    var $ = require('jquery');
    var mvc = require('splunkjs/mvc');
    var SimpleSplunkView = require('splunkjs/mvc/simplesplunkview');
    var AmCharts = require('app/netatmo/amcharts/amcharts');
  	require('app/netatmo/amcharts/serial');

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
                                        "useMarkerColorForLabels": true,
					"markerSize": 10
			    },
			    "valueAxes": [{
			        "axisAlpha": 0.3,   
			        "minimum": -10,
			    }],
			    "dataProvider": data,
			    "graphs": [{
			        "balloonText": this.settings.get('valueField1')+":[[value]]",
			        "fillAlphas": 0.8,
			        "lineAlpha": 0.2,
			        "title": this.settings.get('valueField1'),
			        "type": "column",
			        "valueField": "valueField1",
			        "fillColors": "#cccccc",
			        "lineColor": "#cccccc",
			    }, {
			        "balloonText": this.settings.get("valueField2")+":[[value]]",
			        "fillAlphas": 0.8,
			        "lineAlpha": 0.2,
			        "title": this.settings.get('valueField2'),
			        "type": "column",
			        "valueField": "valueField2",
			        "fillColors": "#333333",
			        "lineColor": "#333333",
			    }, {
			        "balloonText": this.settings.get("valueField3")+":[[value]]",
			        "fillAlphas": 0.8,
			        "lineAlpha": 0.2,
			        "title": this.settings.get('valueField3'),
			        "type": "column",
			        "valueField": "difference",
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
			        "valueField1": result[valueField1],
			        "valueField2": result[valueField2],
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
