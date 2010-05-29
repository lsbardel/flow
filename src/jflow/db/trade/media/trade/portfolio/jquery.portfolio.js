/*
 * File:         jquery.portfolio.js
 * Version:      2.0
 * Description:  Portfolio Application for Asset & Hedge Fund Managers 
 * Author:       Luca Sbardella
 * Created:      05/June/2009
 * Modified:     29/May/2010 by Luca Sbardella
 * Language:     Javascript
 * License:      new BSD Licence
 * Organization: Dynamic Quant Limited
 * Contact:      luca@quantmind.com
 * 
 * 
 * Copyright (c) 2009-2010, Dynamic Quant Limited
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
	
	
	if($.djpcms) {
		/**
		 * Decorator for Portfolio Application in Djpcms.
		 */
		$.djpcms.addDecorator({
			id:"portfolio-application",
			decorate: function(elem,config) {
            	$(".portfolio-application",elem).each(function() {
					var el   = $(this);
					var url  = $('a',el).attr('href');
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
		
					el.portfolio(url);
            	});
			}
		});
		
	}
	
	/**
	 * Utility function to display an inline row for editing a subportfolio
	 * 
	 * @param	parent, portfolioNode, node which receive the inline row
	 */
	$.editPortfolio = function(parent) {
		var row    = $.portfolio.setEditRow(parent,true);
		var p      = parent.portfolio;
		var $this  = p.port;
		var elm    = $('<ul></ul>').appendTo(row.label)
		.css({'list-style-type':'none','display':'inline','float':'left'});
		var code   = $('<input type="text" maxlength="32"/>').val(p.code);
		var desc   = $('<input type="text" maxlength="200"/>');
		var edit   = $('<input class="default" type="submit" value="done"/>');
		var cancel = $('<input type="submit" value="cancel"/>');
		elm.append($('<li></li>').append(code));
		elm.append($('<li>description</li>'));
		elm.append($('<li></li>').append(desc));
		elm.append($('<li></li>').append(edit));
		elm.append($('<li></li>').append(cancel));
		lis = $('li',elm).css({'list-style-type':'none','display':'inline',
			'float':'left','padding-right':'3px'});
		
		row.fadeIn($this.options.defaultFade);
		
		function handle(sub) {
			$.portfolio.clearEditRow($this);
			if(sub) {
				row = $.portfolio.editNode({'code': code.val(), 'name':desc.val()}, parent);
			}
			else {
				parent.fadeIn($this.options.defaultFade);
			}
		}
		
		// Handle the click to Add new subfolder
		edit.click(function(e) {
			handle(true);
		});
		cancel.click(function(e) {
			handle(false);
		});
	};
	
	/**
	 * Utility function to display an inline row for adding a new subportfolio
	 * 
	 * @param	parent, portfolioNode, node which receive the inline row
	 */
	$.displayAddSubfolder = function(parent) {
		var row   = $.portfolio.setEditRow(parent);
		var p     = parent.portfolio;
		var $this = p.port;
		var elm = $('<ul></ul>').appendTo(row.label)
			.css({'list-style-type':'none','display':'inline','float':'left'});
		var input  = $('<input type="text" maxlength="32"/>');
		var add    = $('<input class="default" type="submit" value="add"/>');
		var cancel = $('<input type="submit" value="cancel"/>');
		elm.append($('<li></li>').append(input));
		elm.append($('<li></li>').append(add));
		elm.append($('<li></li>').append(cancel));
		lis = $('li',elm).css({'list-style-type':'none','display':'inline',
			'float':'left','padding':'0'});
		
		row.show();
		
		function handle(sub) {
			row.removeNode();
			if(sub) {
				row = $.portfolio.addFolder(input.val(), parent);
			}
		}
		
		// Handle the click to Add new subfolder
		add.click(function(e) {
			handle(true);
		});
		cancel.click(function(e) {
			handle(false);
		});
	};
	
	/**
	 * Create a right click menu element To add, delete and rename subfolders
	 */
	$.fn.rightClickMenu = function(portfolio_, options_) {
		var $this  = this;
		
		var defaults = {
				x: 20,
				y: 10,
				fade: 300,
				actionClass: 'rightClickAction',
				actions: []
		};
		
		/**
		 * Display the right-click menu at the portfolio element selected
		 * 
		 * @param x - float, the x coordinate
		 * @param y - float, the y coordinate
		 * @param el - jQuery Portfolio Node
		 * @return this
		 */
		function _display(x, y, el) {
			$this.current  = el;
			var p    = el.portfolio;
			$this.portfolio.log('displaing right-click menu for '+p.code);
			$.each(this.options.actions, function(i,v) {
				if(v.display(p)) {
					v.element.show();
				}
				else {
					v.element.hide();
				}
			});
			this.hide().css({top: y + this.options.y,left: x + this.options.x}).fadeIn(this.options.fade);
			return this;
		}
		
		/**
		 * Initailize the right-click menu
		 */
		function init_() {
			// API
			$this.options   = {};
			$this.portfolio = portfolio_;
			$this.current   = null;
			
			// Initialize
			$.extend(true, $this.options, defaults);
			$.extend(true, $this.options, options_);
			var menu    = {};
			var ul      = $('<ul></ul>').appendTo($this);
			var options = $this.options;
			var actions = options.actions;
			options.actions = {};
			
			// Loop over actions and create a list entry
			$.each(actions, function(i,v) {
				var act = $('<a name="' + v.code + '">' + v.name + '</a>').addClass(options.actionClass);
				v.element = $('<li></li>').appendTo(ul).append(act);
				options.actions[v.code] = v;
				act.click(function(e) {
					if($this.current) {
						v.click($this.current);
					}
				});
			});
		}
		
		// Initialize
		init_();
		
		
		// 	API
		this.display = _display;
		
		
		return this;
	};
	
	
	/**
	 * The portfolio class
	 * 
	 * This define a new object in the jQuery name-space which holds
	 * all the information for generating porfolio plugins.
	 */
	$.extend({
		portfolio: new function() {
			var floatingPanels = {};
			var parsers    	   = {};
			var extraTools     = {};
			var events         = {};
			var tableEvents    = {};
			var debug	       = false;
		
			// Right click menu defaults
			var rcoptions = {
				selectedClass: 'rclk',
				menuClass: 'portfolio-rightClickMenu',
				actions: []
			};
		
			// Portfolio defaults
			this.defaults = {
				show:          true,
				requestParams: {},
				responcetype:  'json',
				requestMethod: 'post',
				loadingClass:  'loading',
				displayLabel:  'Select fields',
				beforeAddFolder:  null,
				beforeEditFolder: null,
				beforeMoveNode:   null,
				beforeRemoveNode: null,
				defaultFade:	 300,
				rightClickMenu: rcoptions,
				//
				editable:	   false,
				parse:		   null,
				loadData:	   null,
				autoload:	   true,
				displayeffect: null,
				toolswidth: {min: "300px",
							max: "600px"},
				firstColumnIndent: 19,
				portfolioClass: "portfolio",
				portfolioOutPanelClass: "portfolio-panel-out",
				portfolioOutPanelClass2: "portfolio-panel-break",
				portfolioPanelClass: "portfolio-panel",
				toolsPrefix:        "portfolioTool",
				toolsLinkClass:     "portfolio-tool-link",
				toolsPanelClass:    "portfolio-tools",
				toolsHolderClass:   "tools-holder",
				toolsResizerClass:  "tools-resizer",
				expandToolsClass:   "expand",
				reduceToolsClass:   "reduce",
				holderClass:        "portfolio-holder",
				menubarClass:       "portfolio-menubar",
				containerClass:     "portfolio-table-container",
				tableClass:	        "portfoliotable",
				reloadClass:        "portfolio-reload",
				movableClass:       "movable",
				editableClass:      "editable",
				folderClass:	    "folder",
				togglerClass:       "expander",
				positionClass:		"position",
				labelClass:			"label",
				expandClass:		"expanded",
				hoverClass:			"hover",
				overDropClass:		"drag-drop-over",
				childPrefix:    	"child-of-",
				columnPrefix:   	"portfolio-column-",
				levelPrefix:		"level-",
				tableoptions:   	{},
				columnClass:	function(code) {return this.columnPrefix + code;},
				startLoading:	function($this) {$this.addClass(this.loadingClass);},
				stopLoading: 	function($this) {$this.removeClass(this.loadingClass);}
			};
			
			var defparser = {
					id: "default",
					is: function(s){return true;},
					format: function(s){return s;},
					attr: function(s){}
			};
		
			
			/**
			 * Logger function during debug
			 */
			function log(s) {
				if(debug) {
					if (typeof console != "undefined" && typeof console.debug != "undefined") {
						console.log(s);
					} else {
						//alert(s);
					}
				}
			}
			
			function _Freeze($this) {
				$this.options.frozen = true;
			}
			function _UnFreeze($this) {
				$this.options.frozen = false;
			}
			
			/**
			 * Create a new HTML row with data
			 * @param rowdata, Object, data to put into the new row
			 * @param $this, jQuery portfolio object
			 * @param ct, String or null, column tag
			 */ 
			function _createNewRow(rowdata, $this, ct) {
				var options = $this.options;
				var ctag    = ct ? ct : 'td';
				var row     = $(document.createElement("tr"));
				//if(ctag == 'td') {
				//	row.hide();
				//}
				
				// Create the columns
				$.each(options.header_columns, function(i,val) {
					var col = $(document.createElement(ctag)).addClass(val.classname);
					var pa  = val.parser; 
					pa.attr(col);
					row.append(col);
				});
				
				_writeData(row,rowdata,$this,ctag);
				return row;
			}
        
			/**
			 * Create a new portfolio Node
			 * @param parent jQuery.portfolioNode or null
			 * @param data JSON data to initialise the new Node
			 * @param $this, portfolio object
			 * @param hiding boolean or null,
			 *		  if true the node is created on the fly, otherwise it is the first load.
			 * @return a jQuery.portfolioNode
			 */
			function _createNode(parent, data, $this, hiding) {
				var row = _createNewRow(data, $this);
				
				var options = $this.options;
				
				//if(hiding) {
				//$this.showColumns($this.currentView(), row);
				//}
				$this.showColumns($this.currentView(), row);
			
				row = row.portfolioNode(options, parent, data, $this);
				
				//write data into columns
				//_writeData(row,data,$this);
    		
				if(hiding && row.portfolio.id) {
					_registerTableEvents($this,row);
				}
				
				return row;
			}
        
			/**
			 * Add a new folder
			 * @param name	String, new folder name
			 * @param pid	jquery portfolioNode,	 parent node
			 * @param $this	jquery portfolio object, portfolio to add folder to
			 * @return
			 */
			function _addFolder(name, parent) {
				var pid   = parent.portfolio.id;
				var $this = parent.portfolio.port;
				_Freeze($this);
				var pc    = $this.options.beforeAddFolder;
				if(pc) {
					pc(name, pid, $this);
				}
				else {
					_addNewFolder(null,$this);
				}
			}
        
			/**
			 * Called after _addFolder to fininalize the add method
			 * 
			 * @param data, Object, data for new portfolio node
			 * @param $this, portfolio object
			 * @return portfolioNode object or null
			 */
			function _addNewFolder(data, $this)  {
				var row = null;
				if(data && $this) {
					var pid = data.parent;
					var parent = $this.ptree.rowdict[pid];
					if(parent) {
						data.parent = parent;
						row = _createNode(parent,data,$this,true)
						.insertAfter(parent).fadeIn($this.options.defaultFade);
						parent.expand();
					}
				}
				_UnFreeze($this);
				return row;
			}
         	
         	//////////////////////////////////////////////////////////////////////////
         	//	EDIT NODES
         	//////////////////////////////////////////////////////////////////////////
         	
			/**
			 * Edit a node data
			 * 
			 * @param data	Object, data containing node information
			 * @param $this	portfolio which holds the node
			 */
         	function _editNode(data, node) {
				var $this = node.portfolio.port;
				_Freeze($this);
				var pc    = $this.options.beforeEditFolder;
				if(pc) {
					pc(node, data);
				}
				else {
					_finalizeEditNode(null,$this);
				}
         	}
         
         	/**
         	 * Finalize editing
         	 * 
         	 * @param data Object, edited data
         	 * @param $this, portfolio Object
         	 */
         	function _finalizeEditNode(data, $this) {
         		var el = null;
        		if(data && data.id) {
        			el = $this.ptree.rowdict[data.id];
        			if(el) {
        				el.portfolio.code = data.code ? data.code : el.portfolio.id;
        				_writeData(el,data,$this);
        				log("Folder " + el.portfolio.code + " changed");
        			}
        			else {
        				log("Could not find row in finalize edit node");
        			}
        		}
        		else {
        			log("Nothing done in finalize edit node");
        		}
        		_UnFreeze($this);
        		return el;
         	}
         
           	//////////////////////////////////////////////////////////////////////////
         	//	MOVE NODES
         	//////////////////////////////////////////////////////////////////////////
         	function _moveNode(node, target) {
         		var $this = node.portfolio.port;
				_Freeze($this);
				var pc    = $this.options.beforeMoveNode;
				if(pc) {
					pc(node, target);
				}
				else {
					_finalizeMoveNode(null,$this);
				}
         	}
         	function _finalizeMoveNode(node, target) {
         		if(node && target) {
         			node.setparent(target);
         			var p = node.portfolio.parent;
         			log(node.portfolio.code + " moved into " + p.portfolio.code);
         		}
         		else {
         			log(node.portfolio.code + " did not move. No target found");
         		}
        		_UnFreeze(node.portfolio.port);
        		return node;
         	}
         
         	//////////////////////////////////////////////////////////////////////////
         	//	REMOVE NODE
         	//////////////////////////////////////////////////////////////////////////	
         	/**
         	 * Remove a node from the tree
         	 * 
         	 * @param node, portfolioNode, node to be removed
         	 * @param keepChildren, boolean or null, if true the children won't be deleted
         	 */
         	function _removeNode(node,keepChildren) {
         		var $this = node.portfolio.port;
				_Freeze($this);
				var pc    = $this.options.beforeRemoveNode;
				if(pc) {
					pc(node, keepChildren);
				}
				else {
					_finalizeRemoveNode(null,keepChildren,$this);
				}
         	}
         	
         	function _finalizeRemoveNode(node, keepChildren, $this) {
         		if(node && keepChildren && node.portfolio.tree) {
         			var parent = node.portfolio.parent;
         			$.each(node.portfolio.tree, function(i,child) {
         				child.setparent(parent);
         			});
         			node.removeNode();
         			log(node.portfolio.code + " removed");
         		}
         		else {
         			log("Did not remove. No target found");
         		}
        		_UnFreeze($this);
        		return node;
         	}
         
         	/**
         	 * Write row data into the html table
         	 * 
         	 * @param row, portfolioNode
         	 * @param data, JSON Object
         	 * @param $this	portfolio object
         	 * @param ctag, String column tag (td or th)
         	 */
         	function _writeData(row, data, $this, ct) {
         		var ctag = ct ? ct : 'td';
        		var headers = $this.options.header_columns;
        		var rowdata = data ? data.row : null;
        		var val;
        		if(rowdata) {
        			$(ctag,row).each(function(i,v) {
        				var h  = headers[i];
        				var pa = h.parser;
        				var ht = row.label ? row.label : $(this);
        				//var ht = i ? $(this) : row.label;
        				if(rowdata.length > i) {
        					val = rowdata[i];
        					if(pa.is(val)) {
        						ht.html(pa.format(val));
        					}
        					else {
        						ht.html(val+'');
        					}
        				}
        				else {
        					ht.html('');
        				}
        			});
        		}
        	}
         	
         	function _clearEditRow($this) {
         		var er = $this.options.editRow;
         		if(er) {
         			var p = er.editing;
         			er.removeNode();
         			if(p) {
         				p.show();
         			}
         			$this.options.editRow = null;
         		}
         	}
         	
         	/**
         	 * Set a temporary row below parent
         	 * 
         	 * @param parent portfolioNode, node after which the row is inserted
         	 */
         	function _setEditRow(parent, hideparent) {
         		var $this = parent.portfolio.port;
         		_clearEditRow($this);
         		var opts  = {movable : true, editable : true, canaddto: true};
        		var row   = $.portfolio.createNode(parent,opts,$this,true);
        		if(hideparent) {
        			row.editing = parent.hide();
        		}
        		else {
        			parent.expand();
        		}
        		row.insertAfter(parent);
        		$this.options.editRow = row;
        		return row;
         	}
         	
        
        	function _registerEvents($this) {
        		$.each(events, function(k,v) {
        			log('Registering event '+k);
        			v.register($this);
        		});
        	}
        	
        	function _registerTableEvents($this,elems) {
        		$.each(tableEvents, function(k,v) {
        			log('Registering table event '+k);
        			v.register($this,elems);
        		});
        	}
        
        	/**
        	 * Display a portfolio tool
        	 * 
        	 * @param	$this, portfolio Object
        	 * @param	id, string,	tool id
        	 * @return  HTMLElement where to display the tool or null
        	 */
        	function _displayTool($this,id) {
        		var options = $this.options;
        		$('.'+options.toolsHolderClass, $this).hide();
        		var v   = options.htmls.divtools[id];
        		if(v) {
        			options.htmls.toolTitle.html(v.header);
        			v.el.show();
        			return v.el;
        		}
        		return null;
        	}
	
        	/**
        	 * Register portfolio tools
        	 * @param $this, jQuery object, portfolio to register tool to.
        	 * @param menubar
        	 * 
        	 * Loop over extraTools
        	 */
        	function _registerTools($this, menubar) {
        		var cn,el,id;
        		var options = $this[0].options;
        		var divtools = {};
        		var divlist  = [];
        		options.htmls.divtools = divtools;
			
        		$.each(extraTools, function(k,v) {
        			cn = v.menuClass;
        			log("Adding tool "+k);
    				id = options.toolsPrefix + '-' + divlist.length;
    				
    				// If a class is specified and innav is set to true,
    				// we create a link on the menubar
        			if(cn && v.innav)  {
        				v.link = $(document.createElement("a"))
        					.attr({'title':v.header,'id':id})
        					.addClass(cn).addClass(options.toolsLinkClass);
        				menubar.append($(document.createElement("li")).append(v.link));
        			}
        			v.el = $(document.createElement("div")).addClass(options.toolsHolderClass).hide();
        			var nel = v.setup(v.el,id);
        			if(nel) {v.el = nel;}
        			options.htmls.toolspanel.append(v.el);
        			divtools[id] = v;
        			divlist.push(v);
        		});
        	}
        	
        	function _registerFloating($this) {
        		$.each(floatingPanels, function(k,v) {
        			log('Registering floating panel '+k);
        			var p = v.register($this);
        			if(p) {
        				$this[0].options.floatingPanels[k] = p;
        			}
        		});
        	}
		 
		 function _addelement(el,holder) {
			 var id  = el.id.toLowerCase();
			 var p   = holder[id];
			 if(!p) {
				 el.id = id;
				 holder[id] = el;
			 }
		 }
		 
		 /**
		  * Preprocess portfolio headers
		  * @param headers Object, headers to process
		  * @return Object, preprocessed headers
		  */
		 function _processheaders(headers) {
			 var nchoices = [];
			 if(!headers.choices) {
				 var vals = {};
				 $.each(headers.elements, function(i,el) {
					 vals[el.code] = i;
				 });
				 nchoices.push({code:"default",
					 	 	    description:"",
					 		    name:"Default View",
					 		    values: vals});
			 }
			 else {
				 $.each(headers.choices, function(i,v) {
					 var vobj = {};
					 $.each(v.values, function(j,code) {
						 vobj[code] = j; 
					 });
					 v.values = vobj;
					 nchoices.push(v);
				 });
			 }
			 
			 return {elements: headers.elements,
				 	 choices:  nchoices};
		 }
		 
		 ////////////////////////////////////////////////////////////
		 //	BUILD ELEMENT CACHE
		 ////////////////////////////////////////////////////////////
		 function _buildCache($this) {
			 log("Building element's cache.");
			 var options  = $this.options;
			 var headers  = options.header_columns;
			 var colcache = {};
			 options.colcache = colcache;
				
			 $.each(headers, function(i,v) {
				 colcache[v.code] = $('.'+v.classname,$this);
			 });
		 }
		
	 	/**
	 	 * Add data to portfolio object table
	 	 * 
	 	 * @param $this, portfolio object
	 	 */
	 	function _finaliseLoad($this)  {
	 		 var options = $this.options;
	 		
	 		 if(options.tablesorter) {
	 			var tblopts   = {};
		 		 tblopts.debug = debug;
		 		 $.each(options.tableoptions, function(key, param) {
		 			 tblopts[key] = typeof param == "function" ? param() : param;
		 		 });
	 			 var tbl = $('table',$this);
	 			 tbl.tablesorter(tblopts);
	 		 }
		
	 		 // Create the column cache
	 		 _buildCache($this);
	 		 $this.changeView();
	 		_registerTableEvents($this);
	 		$('tbody',$this).fadeIn(options.defaultFade);
	 	}
	 
	 	/**
	 	 * Send request to server
	 	 * 
	 	 * @param $this	portfolio object
	 	 */
	 	function _request($this)  {
	 		var options  = $this[0].options;
	 		var url 	 = options.url;
	 		if(!url)  {return;}
	 		log("Preparing to send ajax request to " + url);
	 		var params   = {
	 				timestamp: +new Date()
	 		};
	 		$.each(options.requestParams, function(key, param) {
	 				params[key] = typeof param == "function" ? param() : param;
	 		}); 
	 		options.startLoading($this);
	 		$.ajax({url: url,
				type: options.requestMethod,
				data: $.param(params),
				dataType: options.responcetype,
				success: function(data) {
					log("Got the response from server. Parsing data.");
					var ok = true;
					if(options.parse)  {
						try {
							data = options.parse(data,$this);
						}
						catch(e) {
							ok = false;
							log("Failed to parse data. " + e);
						}
					}
					options.stopLoading($this);
					if(ok)  {
						_finaliseLoad($this,data);
					}
				}
				});
	 	}
	 
	 	/**
	 	 * ===============================================================================
	 	 * ===============================================================================
	 	 * CONSTRUCTOR
	 	 * 
	 	 * Initialize a portfolio object
	 	 * @param	urlOrData url to get data from or data object
	 	 * @param	options_, Object, portfolio specific options
	 	 * ==============================================================================
	 	 * ==============================================================================
	 	 * 
	 	 */
		function _initialize(urlOrData, options_)  {
			var isUrl  = typeof urlOrData == "string";
			var $this = $(this);
			//var phead = _processheaders(headers);
				
			var options = {
					url: isUrl ? urlOrData : null,
					data: isUrl ? null : urlOrData,
					floatingPanels: {},
					htmls: {},
					frozen: false,
					editrow: null,
					hideFloating: function() {
						$.each(this.floatingPanels, function(k,v) {
							v.hide();
						});
					}
			};
				
			$.extend(true, options, $.portfolio.defaults);
			$.extend(true, options, options_);
			$this[0].options = options;
			$this.addClass(options.holderClass);
			$this.fadeOut(options.defaultFade).html("");
				
			if($.portfolio.paginate) {
				$.portfolio.paginate($this);
			}
			
			/*
			// Loop over coluns and create the table headers
			$.each(options.header_columns, function(i,c) {
					var fo = parsers[c.formatter];
					c.parser = fo ? fo : defparser;
					//c.classname = options.columnClass(c.code);
					c.classname = options.columnClass(i+'');
					options.htmls.headrow.append($(document.createElement('th'))
							.html(c.name ? c.name : c.code)
							.addClass(c.classname));
			});
			log("Created " + options.header_columns.length + " table headers");
			*/
			
			// API
			$this.currentView = function() {
				var i = parseInt(this.options.htmls.displays.val(),10);
				return this.options.header_choices[i].values;
			};
				
			$this.changeView = function() {
				var v = this.currentView();
				this.showColumns(v);
			};
				
			$this.clearselected = function() {
				this.options.hideFloating();
				var rcm = $this.options.rightClickMenu;
				$('.'+rcm.selectedClass,this).removeClass(rcm.selectedClass);
			};
				
			$this.showColumns = function(codelist) {
				$.each(this.options.colcache, function(code, cache) {
					 var p = codelist[code];
					 if(p == null) {
						 cache.hide();
					 }
					 else {
						 cache.show();
					 }
				});
			};
				
			$this.log = log;
				
			// First build of the cache and set the first view
			//_buildCache($this);
			//$this.changeView();
				
			_registerFloating($this);
			_registerTools($this,options.htmls.menubar);
			_registerEvents($this);
			$this.fadeIn(options.defaultFade);
				
			if(options.autoload) {
				$.portfolio.loadData($this);
			}
				
			return $this;
		}
		
		
		///////////////////////////////////////////////////
		//	API FUNCTIONS
		///////////////////////////////////////////////////
		this.paginate		 	 = null;
		this.loadData    		 = _request;
		this.createNode 		 = _createNode;
		this.createNewRow		 = _createNewRow;
		this.addFolder			 = _addFolder;
		this.addNewFolder   	 = _addNewFolder;
		this.editNode			 = _editNode;
		this.finalizeEditNode	 = _finalizeEditNode;
		this.moveNode			 = _moveNode;
		this.finalizeMoveNode	 = _finalizeMoveNode;
		this.removeNode     	 = _removeNode;
		this.finalizeRemoveNode  = _finalizeRemoveNode;
		this.clearEditRow		 = _clearEditRow;
		this.setEditRow			 = _setEditRow;
		this.displayTool		 = _displayTool;
		this.addParser 			 = function(e){_addelement(e,parsers);};
		this.addEvent	    	 = function(e){_addelement(e,events);};
		this.addTool		 	 = function(e){_addelement(e,extraTools);};
		this.addTableEvent  	 = function(e){_addelement(e,tableEvents);};
		this.addFloatingPanel  	 = function(e){_addelement(e,floatingPanels);};
		this.construct      	 = _initialize;
		this.debug		   		 = function(){return debug;};
		this.setdebug		 	 = function(v){debug = v;};
	}
	});
	
	
	/**
	 * Extend the jQuery Object with the portfolio plugin 
	 */
	$.fn.extend({
        portfolio: $.portfolio.construct
	});
	
	
	
	
	
	
	/**
	 * Portfolio Node class
	 * This jQuery plugin handle the portfolio node structure.
	 * 
	 * @param	options_	Object,			   	  	Options
	 * @param	parent_ 	portfolioNode or null	The parent Node
	 * @param	el 			Object					Data element used to create the portfolio node
	 * @parms   $this		Object					The jquery portfolio holding the node
	 */
	$.fn.portfolioNode = function(options_, parent_, el, $this) {
		var holder    = this;
		var _colfirst = $($('td',this)[0]);
		var _label    = null;
		var options   = options_;
		var _rowdict  = parent_ ? parent_.rowdict : {};
		var rightMenu = null;
		var elemRightSelected = null;
		
		function log(s) {
			if(options.debug) {
				if (typeof console != "undefined" && typeof console.debug != "undefined") {
					console.log(s);
				} else {
					alert(s);
				}
			}
		}
		
		var _portfolio = {
			port:	  $this,
			parent:   parent_,
			tree:	  {},
			level:	  null,
			folder:   el.folder ? el.folder : false,
			movable:  el.movable ? el.movable : false,
			editable: el.editable ? el.editable : false,
			canaddto: el.canaddto ? el.canaddto : false,
			id:		  el.id ? el.id : null,
			code:	  el.code ? el.code : ''
		};
		
		function removeMenu() {
			if(rightMenu) {
				rightMenu.remove();
			}
			rightMenu = null;
			if(elemRightSelected) {
				elemRightSelected.removeClass(options.rightClickSelectedClass);
			}
		}
		
		function paddfirst(level) {
			return (level-1)*options.firstColumnIndent + 5;
		}
    	
		function _level(row,l) {
			var p = row.portfolio.parent;
			if(p) {
				return _level(p,l+1);
			}
			else  {
				return l;
			}
		}
		
		function _collapse(node, secondary) {
			if(node.portfolio.folder) {
				node.removeClass(options.expandClass);
				$.each(node.portfolio.tree, function(i,child) {
					_collapse(child,true);
					if(secondary) {
						child.hide();
					}
					else {
						//child.slideUp(options.defaultFade);
						child.hide();
					}
				});
			}
		}
		
		function _expand(node) {
			if(node.portfolio.folder) {
				node.show();
				node.addClass(options.expandClass);
				$.each(node.portfolio.tree, function(i,child) {
					//child.slideDown(options.defaultFade).show();
					child.show();
				});
			}
		}
		
		function _toggleBranch() {
    		if(this.hasClass(options.expandClass)) {
    			_collapse(this);
    		}
    		else {
    			_expand(this);
    		}
    	}
		
    	/**
    	 * Initialize node
    	 * @return null
    	 */
		function _init()  {
			var id = _portfolio.id;
			var pa = _portfolio.parent;
			
			holder.rowdict  = _rowdict;
			if(id) {
				_rowdict[id] = holder;
				holder.attr('id',id);
				if(pa) {
					log("Added new entry "+id+" to portfolio "+pa.portfolio.id);
					pa.portfolio.tree[id] = holder;
				}
				else {
					log("Added root entry "+id+" to portfolio");
				}
			}
				
			_label = $(document.createElement('span'))
					.html(_colfirst.html()).addClass(options.labelClass);
			if(el.editable | el.canaddto) {
				_label.addClass(options.editableClass);
			}
			if(el.movable) {
				_label.addClass(options.movableClass);
			}
			
			_colfirst.html("");
			if(el.folder) {
				_label.addClass(options.folderClass);
				_colfirst.append($(document.createElement('span'))
						.addClass(options.togglerClass)
						.css({"padding-left":options.firstColumnIndent+"px"}));
			}
			else if(id) {
				_label.addClass(options.positionClass);
			}
			
			_colfirst.append(_label);
		}
		
		function _addEvents(el)  {
			$('.'+options.togglerClass,el).click(function() {
	        	var html = $(this).parents('tr')[0];
	        	var node = _rowdict[html.id];
	        	_toggleBranch(node);
			});
			
		}
		
		function _removeNode() {
   		 	var parent = this.portfolio.parent;
   		 	if(parent) {
   		 		var children = this.portfolio.tree;
   		 		$.each(children, function(i,c) {
   		 			c.setparent(parent);
   		 		});
   		 	}
   		 	log("deleted node "+this.portfolio.id);
   		 	this.fadeOut(options.defaultFade).remove();
   		 	return this;
		}
		
		/**
		 * Set a new Node parent for node
		 * @param target the new parent node
		 * @return this node
		 */
		function _setparent(target) {
			if(typeof target =="string") {
				target = this.rowdict[target];
			}
			if(!target) {return this;}
			
			var id     = this.portfolio.id;
			var parent = this.portfolio.parent;
			if(parent == target) {return this;}
			
			if(parent) {
				// the node is registered with another parent, so remove it from
				// the old parent tree
				delete parent.portfolio.tree[id];
			}
			
			// Set the new parent
			this.portfolio.parent = target;
			target.portfolio.tree[id] = this;
			this.insertAfter(target);
			this.refresh();
			target.expand();
			if(parent) {
				log("Moved node "+id+" from parent "+parent.portfolio.id+" to "+target.portfolio.id);}
			return this;
		}
		
		// Initialize
		_init();
		
		
		// API
		this.portfolio     = _portfolio;
		this.label         = _label;
		this.colfirst      = _colfirst;
		this.removeNode    = _removeNode;
		this.toggleBranch  = _toggleBranch;
		this.setparent     = _setparent;
		
		/**
		 * Utility function
		 */
		this.refresh   = function(pnode) {
			this.removeClass(options.expandClass);
			if(pnode) {
				this.hide().insertAfter(pnode);
			}
			var lev  = _level(this,1);
			this.portfolio.level = lev;
    		var padd = paddfirst(lev);
    		this.colfirst.css({'padding-left': padd+'px'});
    		var node = this;
    		if(this.portfolio.folder) {
    			$.each(node.portfolio.tree, function(i,child) {
    				node = child.refresh(node);
    			});
    		}
    		return node;
		};
		
		this.expand = function() {
			_expand(this);
			return this;
		};
		
		this.refresh();
		
		return this;
	};
	
	
	/**
	 * Function: Parse server data to display aggregate positions
	 */
	$.parseAggregates = function(data, $this)  {
		var i,j,el,row,val;
		var options = $this.options;
		var pl      = data.result;
		var html    = "";
		$.each(data.result, function(key,rval) {
			row = "<tr>";
			for(i=0;i<rval.row.length;i++)  {
				val = rval.row[i];
				row += '<td class="' + options.header_columns[i].columnclass + '">' + val + "</td>";
			}
			html += row + "</tr>";
		});
		$('tbody',$this).html(html);
	};
	
	/**
	 * Parse data arriving from server and build a new portfolio.
	 * 
	 * @param data, object, data from server
	 * @param $this, portfolio jquery object
	 */
	$.parsePortfolio = function(data, $this)  {
		data = data.result;
		var options  = $this.options;
		var elements = data.elements;
		var root	 = data.root;
		var table    = $('table.'+options.tableClass,$this);
		var thead    = $('thead',table);
		
		$('tbody',table).remove();
		var bdy  	 = $('<tbody></tbody>').insertAfter(thead).hide();
		
		function parsePortfolioData(id,parent)  {
			var child;
			var el  = elements[id];
			var row = $.portfolio.createNode(parent, el, $this).hide();
			row.appendTo(bdy);
			if(el.tree) {
				$.each(el.tree, function(i,cid) {
					parsePortfolioData(cid,row);
				});
			}
			return row;
		}
		
		$this.ptree   = parsePortfolioData(root).expand();
	};
	
	
	
	
	
	
	var portf = $.portfolio;
	
	
	
	
	
	////////////////////////////////////////////////////////////////
	//	FLOATING PANELS
	////////////////////////////////////////////////////////////////
	
	/**
	 * \brief Add the right-click menu for adding/deleting/editing subportfolios
	 */
	portf.addFloatingPanel({
		id: "rclkmenu",
		register: function($this) {
			// Create right click menu
			var rcm = $this[0].options.rightClickMenu;
			if(rcm) {
				var rclkMenu = $(document.createElement('div')).hide()
					.addClass(rcm.menuClass).appendTo($this);
				return rclkMenu.rightClickMenu($this,rcm);
			}
			else {
				return null;
			}
		}
	});
	
	
	//////////////////////////////////////////////////////////////////////
	//		PORTFOLIO EVENTS
	//
	//	This events are registered when the portfolio plugin is created
	//////////////////////////////////////////////////////////////////////
	
	portf.addEvent({
		id:"clear",
		register: function($this) {
			$('body').click(function(e) {
				$this.clearselected();
			});
		}
	});
	
	portf.addEvent({
		id: "display-fields",
		register : function($this) {
			var options = $this[0].options;
			options.htmls.displays.change(function() {
				$this.trigger("view-pre-change",[this,$this]);
				$this.changeView();
				$this.trigger("view-changed",[this,$this]);
			});
		}
	});
	
	portf.addEvent({
		id: "reload",
		register: function($this) {
			var options = $this[0].options;
			$('.'+options.reloadClass,$this).click(function() {
				$this.trigger('pre-reload',[this, $this]);
				$.portfolio.loadData($this);
			});
		}
	});
	
	portf.addEvent({
		id:	"tool-resizer",
		register: function($this) {
			var options = $this[0].options;
			$('.'+options.toolsResizerClass, $this).click(function() {
				function setwidth(w) {
					options.htmls.toolspanel.width(w);
					options.htmls.poutpanel.css('margin-right',w);
				}
				var el = $(this);
				if(el.hasClass(options.expandToolsClass)) {
					setwidth(options.toolswidth.max);
					el.removeClass(options.expandToolsClass).addClass(options.reduceToolsClass);
				}
				else {
					setwidth(options.toolswidth.min);
					el.removeClass(options.reduceToolsClass).addClass(options.expandToolsClass);
				}
				$('.'+$this.options.toolsHolderClass).trigger('resize');
			});
		}
	});
	
	portf.addEvent({
		id: "open-tool",
		register: function($this) {
			var options = $this[0].options;
			$('.'+options.toolsLinkClass, $this).click(function() {
				var id  = $(this).attr('id');
				$.portfolio.displayTool($this,id);
			});
		}
	});
	
	
	////////////////////////////////////////////////////////////////
	//	TABLE EVENTS
	////////////////////////////////////////////////////////////////
	
	portf.addTableEvent({
		id: "toggler",
		register: function($this,elems) {
			var options = $this[0].options;
			if(!elems){elems = $this;}
			$('.'+options.togglerClass,elems).click(function() {
				var html = $(this).parents('tr')[0];
				var node = $this.ptree.rowdict[html.id];
				node.toggleBranch();
			});
		}
	});
	
	portf.addTableEvent({
		id: "hover",
		register: function($this,elems) {
			var options = $this[0].options;
			if(!elems){elems = $this;}
			$('tr',elems).hover(function() {
				$(this).addClass(options.hoverClass);
			},
			function(){
				$(this).removeClass(options.hoverClass);
			});
		} 
	});
	
	
	/**
	 * Register the right-click menu, and the drag and drop functionality
	 */
	portf.addTableEvent({
		id: "rightClickMenu-Drap-Drop",
		register: function($this,elems) {
			var options = $this[0].options;
			if(!elems){elems = $this;}
			
			if(!options.editable) {return;}
			
			var editables = $('.'+options.editableClass,elems);
			var movables  = $('.'+options.movableClass,elems);
			
			editables.rightMouseDown(function(e) {
				$this.clearselected();
				$(this).addClass(options.rightClickMenu.selectedClass);					
			})
			.rightMouseUp(function(e) {
				var elem = $(this);
				var html = elem.parents('tr')[0];
		        var node = $this.ptree.rowdict[html.id];
		        var pos  = this.offset();
		        var p    = options.floatingPanels.rclkmenu;
		        if(p) {
		        	p.display(pos.left,pos.top,node);
		        }
			});
			
			// Movable event on movable rows
			movables.draggable({
					  helper: "clone",
					  opacity: 0.75,
					  refreshPositions: true, // Performance?
					  revert: "invalid",
					  revertDuration: 300,
					  scroll: true
					});
			
			editables.each(function() {
				$(this).parents("tr").droppable({
				    accept: "."+options.movableClass,
				    drop: function(e, ui) {
					  	$(this).removeClass(options.overDropClass);
					  	var dragged = $(ui.draggable).parents("tr")[0];
					  	if(dragged.id && this.id && this.id != dragged.id) {
					  		var node   = $this.ptree.rowdict[dragged.id];
					  		var target = $this.ptree.rowdict[this.id];
					  		$.portfolio.moveNode(node,target);
					  	}
				    },
				    over: function(e, ui) {
				    	var dragged = ui.draggable.parents("tr")[0];
				        if(dragged.id && this.id && this.id != dragged.id) {
				        	$(this).addClass(options.overDropClass);
				        }
				    },
				    out: function(e, ui) {
				    	$(this).removeClass(options.overDropClass);
				    }
				  });
				});
			}
	});
	
	////////////////////////////////////////////////////////////////
	//		PARSERS
	////////////////////////////////////////////////////////////////
	portf.addParser({
		id: "text",
		is: function(s) {
			return true;
		},
		format: function(s) {
			return $.trim(s.toLowerCase());
		},
		type: "text",
		attr: function(s){}
	});
	
	portf.addParser({
		id: "percentage",
		align: 'right',
		precision: 2,
		attr: function(s){s.css({'text-align':this.align});},
		is: function(s) { 
			var c = parseFloat(s);
			if(isNaN(c))  {return false;}
			else {return true;}
			},
		format: function(s) {
			var c = parseFloat(s);
			if(isNaN(c))  {return s;}
			var mul = Math.pow(10,this.precision);
			var val = Math.round(100*mul*c)/mul;
			return val + '%';
		},
		type: "numeric"
	});
	
	portf.addParser({
		id: "currency",
		precision: 2,
		negativeClass: 'ccy-negative-value',
		align: 'right',
		attr: function(s){s.css({'text-align':this.align});},
		is: function(s) {
			var c = parseFloat(s);
			if(isNaN(c))  {
				return false;
			}
			else {
				return true;
			}
		},
		format: function(s) {
			var c = parseFloat(s);
			if(isNaN(c))  {return s;}
			el    = $(document.createElement("span"));
			isneg = false;
			if(c<0) {
				isneg = true;
				c     = Math.abs(c);
			}
			var cn  = parseInt(c,10);
			var de  = c - cn;
			if(de > 0) {
				var mul = Math.pow(10,this.precision);
				var atom = c/mul;
				if(atom > de)  {
					de = "";
				}
				else {
					atom += "";
					atom  = atom.split(".")[1];
					for(var i=0;atom.length;i++)  {
						if(parseInt(atom[i],10) > 0)  {
							break;
						}
					}
					mul = Math.pow(10,i+1);
					de  = parseFloat(parseInt(de*mul,10))/mul;
					ro  = "" + cn + de;
					ro  = ro.split(".");
					de  = "."+ro[1];
				}
			}
			else {
				de = "";
			}
			cn += "";
			var d,k;
			var N  = cn.length;
			var cs = "";
			for(var j=0;j<N;j++)  {
				cs += cn[j];
				k = N - j - 1;
				d = parseInt(k/3,10);
				if(3*d == k && k > 0) {
					cs += ',';
				}
			}
			cs += de;
			if(isneg) {
				el.addClass(this.negativeClass);
				cs = '-'+cs;
			}
			el.html(cs+'');
			return el;
		},
		type: "numeric"
	});
	
	//////////////////////////////////////////////////////////////////
	// PORTFOLIO PAGINATION
	//////////////////////////////////////////////////////////////////
	portf.paginate = function($this) {
		var options = $this[0].options;
		
		function _createMenuBar() {
			var ul = $("<ul></ul>");
			var li = $("<li></li>").appendTo(ul);
			if(options.displayLabel) {
				li.append($(document.createElement("label")).html(options.displayLabel));
			}
			var displays = $(document.createElement("select")).appendTo(li);
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
	
})(jQuery);
