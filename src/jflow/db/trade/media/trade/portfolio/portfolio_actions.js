
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
		var poutpanel2 = $("<div></div>").addClass(options.portfolioOutPanelClass2).appendTo(poutpanel);
		var portfoliopanel = $(document.createElement("div"))
				.addClass(options.portfolioPanelClass).appendTo(poutpanel2);
		var	menubar = $(document.createElement("div"))
			.addClass(options.menubarClass).append(menulist)
			.appendTo(portfoliopanel);

		// Append table to a div container
		$('<div></div>').addClass(options.containerClass).appendTo(portfoliopanel)
			.append(options.ptable.table);
		
		options.htmls.toolspanel = toolspanel;
		options.htmls.toolTitle  = toolTitle;
		options.htmls.poutpanel  = poutpanel;
		options.htmls.menubar    = menulist;
	};
	
	$.portfolio.get_view = function($this) {
		return $('.select-display',$this).val();
	};
	
	$.portfolio.rcmenu.push({
		name: 'rename',
		available: function(elem, port) {
			var node = $.portfolio.get_node(elem);
			if(node) {
				return node.editable;
			}
			return false;
		},
		onclick: function(elem) {
			var row = $.portfolio.get_row(elem);
			if(row) {
				$.portfolio.editrow(row,'name',true);
			}
		}
	});
	
	$.portfolio.rcmenu.push({
		name: 'add',
		description: 'add folder',
		available: function(elem, port) {
			var node = $.portfolio.get_node(elem);
			if(node) {
				return node.canaddto;
			}
			return false;
		},
		onclick: function(elem) {
			var row = $.portfolio.get_row(elem);
			if(row) {
				$.portfolio.editrow(row,'name');
			}
		}
	});
	
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
			var N = 0;
			$.each(data, function(name,display) {
				N += 1;
				el.append($(document.createElement("option")).text(name).val(name));
			});
			options.log("Added "+N+" pagination types");
		},
		registerevents: function(port) {
			port.bind("display-end",$.portfolio.displayview);
		}
	});
	
	/**
	 * Action for editing and existing node or adding a new one
	 */
	$.portfolio.addAction({
		name: 'add-edit-node',
		menu: 'options',
		success: function(port,data) {
			var options = port[0].options;
			options.displays = data;
			var el = $('.select-display',port).html("");
			var N = 0;
			$.each(data, function(name,display) {
				N += 1;
				el.append($(document.createElement("option")).text(name).val(name));
			});
			options.log("Added "+N+" pagination types");
		},
		registerevents: function(port) {
			port.bind("display-end",$.portfolio.displayview);
		}
	});
	
	
	if($.djpcms) {
		
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
						requestParams: rp,
						fields: $.portfolio_fields
					};
					
					$.portfolio.setdebug($.djpcms.options.debug);
					el.portfolio(url,options);
					//$.portfolio.action(el,'display');
            	});
			}
		});
		
	}
	
	
})(jQuery);