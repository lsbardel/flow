
(function($) {
	
	//////////////////////////////////////////////////////////////////
	// PORTFOLIO PAGINATION
	//////////////////////////////////////////////////////////////////
	$.portfolio.paginate = function($this) {
		var options = $this[0].options;
		
		function _createMenuBar() {
			var ul = $("<ul></ul>");
			var li = $("<li></li>").appendTo(ul);
			if(options.displayLabel) {
				li.append($(document.createElement("label")).html(options.displayLabel));
			}
			var displays = $(document.createElement("select")).appendTo(li).addClass('select-display');
			options.htmls.displays = displays; 
			ul.append($(document.createElement("li")).append($(document.createElement("a"))
					.attr({'title':'Reload'}).addClass(options.reloadClass)));
			ul.append($(document.createElement("li")).append($(document.createElement("a"))
					.attr({'title':'Expand sub-portfolios'}).addClass('tgport tog-out')));

			/*
			$.each(options.header_choices, function(i,el){
				var nv = {};
				$.each(el.values, function(ii,iel){
					nv[iel] = false;
				});
				el.columns = nv;
				displays.append($(document.createElement("option")).text(el.name).val(i));
			});
			*/
			
			return ul;
		}
	
		// Tool panel elements
		var menulist   = _createMenuBar();
		var toolspanel = $(document.createElement("div"))
			.addClass(options.toolsPanelClass).appendTo($this);
		var toolsheader = $(document.createElement("div"))
			.addClass(options.menubarClass).appendTo(toolspanel);
		var tul = $(document.createElement("ul")).appendTo(toolsheader);
		var expandTools = $(document.createElement("a"))
			.attr({'title':'expand'})
			.addClass(options.toolsResizerClass).addClass(options.expandToolsClass)
			.appendTo($(document.createElement("li")).appendTo(tul));
		var toolTitle = $(document.createElement("p"))
			.appendTo($(document.createElement("li")).appendTo(tul));
		var poutpanel = $(document.createElement("div"))
				.addClass(options.portfolioOutPanelClass).appendTo($this);
		var poutpanel2 = $(document.createElement("div"))
				.addClass(options.portfolioOutPanelClass2).appendTo(poutpanel);
		var portfoliopanel = $(document.createElement("div"))
				.addClass(options.portfolioPanelClass).appendTo(poutpanel2);
		var	menubar = $(document.createElement("div"))
			.addClass(options.menubarClass).append(menulist)
			.appendTo(portfoliopanel);

		// Create the table
		var tablecontainer = $(document.createElement("div"))
			.addClass(options.containerClass).appendTo(portfoliopanel);
		var tbl = $(document.createElement('table')).attr({'cellspacing':'1'})
			.addClass(options.tableClass).appendTo(tablecontainer);
		var headrow = $(document.createElement('tr'))
			.appendTo($(document.createElement('thead')).appendTo(tbl));
		tbl.append($(document.createElement('tbody')));
		
		options.htmls.toolspanel = toolspanel;
		options.htmls.toolTitle  = toolTitle;
		options.htmls.poutpanel  = poutpanel;
		options.htmls.headrow 	 = headrow;
		options.htmls.menubar    = menulist;
	};
	
	/**
	 * Action for loading column displays
	 */
	$.portfolio.addAction({
		name: 'display',
		autoload: true,
		success: function(port,data) {
			var options = port[0].options;
			options.displays = data;
			var el = $('.select-display',port).html("");
			$.each(data, function(name,display) {
				el.append($(document.createElement("option")).text(name).val(name));
			});
		}
	});
	
	
	if($.djpcms) {		
		/**
		 * Parse data arriving from server and build a new portfolio.
		 * 
		 * @param data, object, data from server
		 * @param $this, portfolio jquery object
		 */
		$.parseFinInsPortfolio = function(data, port)  {
			obj = port[0];
			var root = data;
			var options  = obj.options;
			var table    = $('table.'+options.tableClass,port);
			var thead    = $('thead',table);
			var make     = $.portfolio.createNode;
			$('tbody',table).remove();
			var bdy  	 = $('<tbody></tbody>').insertAfter(thead).hide();
			
			function parsePortfolioData(el, parent)  {
				var child;
				//var el  = elements[id];
				var row = make(parent, el, port).hide();
				row.appendTo(bdy);
				if(el.positions) {
					$.each(el.positions, function(i,cid) {
						parsePortfolioData(cid,row);
					});
				}
				return row;
			}
			
			port.ptree   = parsePortfolioData(root).expand();
		};
		
		/**
		 * Decorator for Portfolio Application in Djpcms.
		 */
		$.djpcms.addDecorator({
			id:"portfolio-application",
			decorate: function(elem,config) {
            	$(".portfolio-application",elem).each(function() {
					var el   = $(this);
					var aa   = $('a',el);
					var url  = aa.attr('href');
					var id   = aa.attr('id');
					var code = $('.code',el);
					var cmline;
					if(code.length) {
						cmline = {symbol: code.html()};
					}
					else {
						cmline = null;
					}
					el.html('');
					var info = $(".server-logger");
					var elems_ = null;
					if(info) {
						elems_ = {'info': info};
					}
					var rp = {};
					if(id) {
						rp.id = id;
					}
					var options = {
						parse: $.parseFinInsPortfolio,
						requestParams: rp,
						fields: $.portfolio_fields
					};
					
					$.portfolio.setdebug($.djpcms.options.debug);
					el.portfolio(url,options);
					$.portfolio.action(el,'display');
            	});
			}
		});
		
	}
	
	
})(jQuery);