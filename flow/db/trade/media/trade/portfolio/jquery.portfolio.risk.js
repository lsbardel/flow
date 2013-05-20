/*
 * File:         jquery.portfolio.risk.js
 * Version:      1.0
 * Description:  Handle portfolio risk-performance views
 * Author:       Luca Sbardella
 * Created:      24/08/2009
 * Modified:     24/08/2009 by Luca Sbardella
 * Language:     Javascript
 * License:      new BSD Licence
 * Organization: Dynamic Quant Limited
 * Contact:      luca@quantmind.com
 * 
 * Copyright (c) 2009, Dynamic Quant Limited
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without modification,
 * are permitted provided that the following conditions are met:
 * 
 *  * Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimer.
 *  * Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 *  * Neither the name of the Dynamic Quant Limited nor the names of its contributors
 *    may be used to endorse or promote products derived from this software without
 *    specific prior written permission.
 *    
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
 * IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
 * INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 * BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
 * OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY
 * OF SUCH DAMAGE.
 * 
 */


(function($) {
	
	
	$.extend({portfolioRisk: new function() {
		
		this.defaults = {
			classname: 'portfolio-risk',
			precision: 2,
			plot: {
				colors: ["#205497",
				         "#2D8633",
				         "#B84000",
				         "#d18b2c",
				         "#92B6E8",
				         "#EBEB00",
				         "#850000"],
				height: 400,
				classname: 'portfolio-risk-plot'
				}
		};
		
		function Count(obj) {
			var L = 0;
			$.each(obj,function() {
				L+=1;
			});
			return L;
		}
		
		function formatpercent(s,precision) {
			var c = parseFloat(s);
			if(isNaN(c))  {return s;}
			var mul = Math.pow(10,precision);
			var val = Math.round(100*mul*c)/mul;
			return val;
		}
		
		function plotRisk($this) {
			var data = $this.riskdata;
			if(!data) {return;}
			var m1    = $this.menu1();
			var m2    = $this.menu2();
			var div   = $('.'+$this.options.plot.classname,$this);
			div.children().remove();
			var alloc1 = data.allocations[m1];
			var alloc  = alloc1.allocations[m2];
			$.portfolioRisk.barplot($this,alloc1,alloc,div);
		}
		
		function _googleBarPlot($this,alloc1,alloc,div) {
			var dpl     = alloc.data;
			var prec    = $this.options.precision;
			var legend_ = 'none';
			if(alloc.multiple) {
				legend_ = 'bottom';
			}
			var gc    = $(div).googleplot({height:$this.options.plot.height,
										   colors:$this.options.plot.colors,
										   title:alloc1.name,
										   titleY:'% of Total NAV',
										   axisFontSize: 12,
										   legendFontSize: 12,
										   titleFontSize: 14,
										   legend:legend_});
			var formatter = new google.visualization.TableNumberFormat({suffix: '%'});
			//var pdata = gc.gdata; 
			gc.gdata.addRows(Count(dpl));
			gc.gdata.addColumn('string', '');
			
			var ncolumns = 1;
			if(alloc.multiple) {
				var columns = {};
				$.each(dpl,function(c,v) {
					$.each(v,function(a,v) {
						columns[a] = true;
					});
				});
				ncolumns = 0;
				$.each(columns, function(k,v) {
					ncolumns += 1;
					gc.gdata.addColumn('number', k);
				});
				var i = 0;
				$.each(dpl,function(c,vd) {
					var j = 0;
					gc.gdata.setValue(i, j, c);
					$.each(columns, function(a) {
						j+=1;
						var vv = vd[a];
						gc.gdata.setValue(i, j, vv ? formatpercent(vv,prec) : 0);
					});
					i += 1;
				});
			}
			else {
				gc.gdata.addColumn('number', alloc1.name);
				var i = 0;
				$.each(dpl,function(c,v) {
					gc.gdata.setCell(i, 0, c);
					gc.gdata.setCell(i, 1, formatpercent(v,prec));
					i += 1;
				});
			}
			for(var c=1;c<=ncolumns;c+=1) {
				formatter.format(gc.gdata,c);
			}
			var view = new google.visualization.DataView(gc.gdata);
			gc.gchart.draw(view,gc.options);
		}
	
		
		 /**
		  * Refresh Portfolio risk view
		  * 
		  * @param	$this	jQuery PortfolioRisk element
		  * @param	riskdata	Object or none. Risk data	
		  * @return	none
		  */
		function _refresh($this, riskdata) {
			if(riskdata) {
				$this.riskdata = riskdata;
			}
			plotRisk($this); 
		}
	
		 /**
		  * Constructor
		  */
		function _initialize(options_) {
			var $this = this;
			$this.options = {};
			
			$.extend(true, $this.options, $.portfolioRisk.defaults);
			$.extend(true, $this.options, options_);
			
			$this.addClass($this.options.classname);
			if($.portfolioRisk.paginate) {
				$.portfolioRisk.paginate($this);
			}
			
			$this.resize(function(e) {
				_refresh($this);
			});
			return $this;
		}
		
		//	API
		this.construct = _initialize;
		this.refresh   = _refresh;
		this.googleBarPlot = _googleBarPlot;
	}});
	
	/**
	 * jQuery portfolioRisk plugin
	 */
	$.fn.extend({portfolioRisk: $.portfolioRisk.construct});
	
	
	
	var pRisk = $.portfolioRisk;
	
	pRisk.barplot = $.portfolioRisk.googleBarPlot;
	
	/**
	 * Portfolio risk pagination
	 */
	pRisk.paginate = function($this) {
		var menu = $('<select></select>').appendTo($this);
		menu.append($(document.createElement("option")).text("NAV").val("0"));
		menu.append($(document.createElement("option")).text("Notional").val("1"));
		menu.append($(document.createElement("option")).text("Volatility C1").val("2"));
		menu.append($(document.createElement("option")).text("Aggregate Volatility").val("3"));
		var submenu = $('<select></select>').appendTo($this);
		submenu.append($(document.createElement("option")).text("Sub-portfolios").val("0"));
		submenu.append($(document.createElement("option")).text("Currencies").val("1"));
		submenu.append($(document.createElement("option")).text("Combined").val("2"));
		
		$this.menu1 = function() {
			return parseInt(menu.val());
		}
		$this.menu2 = function() {
			return parseInt(submenu.val());
		}
		menu.change(function(){$.portfolioRisk.refresh($this);});
		submenu.change(function(){$.portfolioRisk.refresh($this);});
		
		var plotdiv = $('<div></div>').appendTo($this).addClass($this.options.plot.classname);
	}

})(jQuery);
