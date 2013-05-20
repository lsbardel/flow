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
			var actions        = {};
			var debug	       = false;
		
			// Portfolio defaults
			this.defaults = {
				show:          	   true,
				requestParams:     {},
				responcetype:  	   'json',
				requestMethod:     'get',
				loadingClass:  	   'loading',
				fields:			   {},
				displayLabel:  	   'Select fields',
				beforeAddFolder:   null,
				beforeEditFolder:  null,
				beforeMoveNode:    null,
				beforeRemoveNode:  null,
				defaultFade:	   300,
				//
				editable:	   false,
				loadData:	   null,
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
         	 * Write row data into the html table
         	 * 
         	 * @param row, portfolioNode
         	 * @param data, JSON Object
         	 * @param $this	portfolio object
         	 * @param ctag, String column tag (td or th)
         	 */
         	function _writeData(row, data, $this, ct) {
         		var ctag = ct ? ct : 'td';
        		var headers = $this[0].options.header_columns;
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
			
			/**
			 * Create a new HTML row with data
			 * @param rowdata, Object, data to put into the new row
			 * @param $this, jQuery portfolio object
			 * @param ct, String or null, column tag
			 */ 
			function _createNewRow(rowdata, $this, ct) {
				var options = $this.options;
				var ctag    = ct ? ct : 'td';
				var row     = $("<tr></tr>");
				
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
			 * Create a new edit row for adding/editing portfolio nodes.
			 * The action "add-edit-node" must be implemented
			 * 
			 * @param row HTMLElement
			 * @param field String name of field to edit
			 * @param edit boolean if true the node is edited otherwise another node is added
			 */
			function _editrow(row, field, edit) {
				var node	= row.node;
				if(!node) {return;}
				var port	= node.portfolio;
				var options = node.options;
				if(options.editrow) {return;}
				var fields  = $.portfolio.fields(port);
				var td		= $('<td colspan='+fields.length+'></td>')
				var erow    = $('<tr class="edit"></tr>').append(td).insertAfter(row);
				var elm     = $('<ul></ul>').appendTo(td)
				.css({'list-style-type':'none','display':'inline','float':'left'});
				var code   = $('<input type="text" maxlength="32"/>');
				var desc   = $('<input type="text" maxlength="200"/>');
				var done   = $('<input class="default" type="submit" value="done"/>');
				var cancel = $('<input type="submit" value="cancel"/>');
				elm.append($('<li></li>').append(code));
				elm.append($('<li>description</li>'));
				elm.append($('<li></li>').append(desc));
				elm.append($('<li></li>').append(done));
				elm.append($('<li></li>').append(cancel));
				lis = $('li',elm).css({'list-style-type':'none','display':'inline',
					'float':'left','padding-right':'3px'});
				
				// Handle the click to Add new subfolder
				function close_() {
					if(options.editrow) {
						options.editrow.remove();
						options.editrow = null;
						if(edit) {
							node.fadeIn(options.defaultFade);
						}
					}
				}
				
				done.click(function(e) {
					var data = {name: code.val(),
								description:desc.val(),
								editing: edit || false,
								id: node.id};
					var a = $.portfolio.action(port,'add-edit-node', data);
					if(!a) {close_();}	
				});
				cancel.click(function(e) {
					close_();
				});
				
				erow.insertAfter(row).hide();
				options.editrow = erow;
				if(edit) {
					code.val(node.data[field]);
					row.hide();
				}
				else {
					node.expand();
				}
				erow.fadeIn(options.defaultFade);
			};
        
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
	 	 * Send requests (actions) to server
	 	 * 
	 	 * @param $this	portfolio object
	 	 * @param a Object action
	 	 */
	 	function _request($this, a, data)  {
	 		var options  = $this[0].options;
	 		var data	 = data || {};
	 		var url 	 = a.url ? a.url : options.url;
	 		if(!url)  {return;}
	 		log("Sending ajax request " + a.name + " to " + url);
	 		var params   = {
	 			timestamp: +new Date(),
	 			action: a.name
	 		};
	 		$.each(options.requestParams, function(key, param) {
	 			params[key] = typeof param == "function" ? param() : param;
	 		});
	 		$.each(data, function(key,param) {
	 			params[key] = param;
	 		});
	 		$this.trigger(a.name+"-start",$this);
	 		options.startLoading($this);
	 		$.ajax({url: url,
				type: options.requestMethod,
				data: $.param(params),
				dataType: options.responcetype,
				success: function(data) {
	 				log("Got the response from request " + a.name + ". Parsing data.");
	 				try {
	 					a.success($this,data);
	 				}
	 				catch(e) {
	 					log("Failed to parse " + a.name + " data. " + e);
	 				}
	 				$this.trigger(a.name+"-end",$this);
					options.stopLoading($this);
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
			var elem  = $this[0];
				
			var options = {
					url: isUrl ? urlOrData : null,
					data: isUrl ? null : urlOrData,
					floatingPanels: {},
					htmls: {},
					frozen: false,
					editrow: null,
					cacheview: {},
					displays: {},
					hideFloating: function() {
						$.each(this.floatingPanels, function(k,v) {
							v.hide();
						});
					}
			};
			options["log"] = log;
				
			$.extend(true, options, $.portfolio.defaults);
			$.extend(true, options, options_);
			elem.options = options;
			$this.addClass(options.holderClass);
			$this.fadeOut(options.defaultFade).html("");
			
			// Create the main portfoilio table
			var tbl = $('<table></table>').attr({'cellspacing':'1'}).addClass(options.tableClass);
			options.ptable = {
					table: tbl,
					thead: $('<thead></thead>').appendTo(tbl),
					tbody: $('<tbody></tbody>').appendTo(tbl)
				};
		
			if($.portfolio.paginate) {
				$.portfolio.paginate($this);
			}
				
			$.each(floatingPanels, function(k,v) {
    			log('Registering floating panel '+k);
    			var p = v.register($this);
    			if(p) {
    				options.floatingPanels[k] = p;
    			}
    		});
			
			_registerTools($this,options.htmls.menubar);
			_registerEvents($this);
			$this.fadeIn(options.defaultFade);
			
			$.each(actions, function(n,a) {
				if(typeof a.registerevents == "function") {
					a.registerevents($this);
				}
			});
			
			$.portfolio.action($this, function(a) {return a.autoload;});	
			return $this;
		}
		
		
		///////////////////////////////////////////////////
		//	API FUNCTIONS
		///////////////////////////////////////////////////
		this.paginate		 	 = null;
		this.editrow			 = _editrow;
		this.loadData    		 = _request;
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
		
		/**
		 * Clear the portfolio element
		 */
		this.clear = function(port) {
			var options = port[0];
			options.tree = {};
			options.cacheview = {};
			options.loaded = false;
		}
		
		this.createNode = function(parent, data, $this, ct) {
			var ctag    = ct ? ct : 'td';
			return new $.portfolioNode({"ctag":ctag},parent,data,$this,log);
		};
		
		this.get_row = function(elem) {
			var row = $(elem).parents('tr');
			if(row.length) {
				return row[0];
			}
			else {return null;}
		}
		
		this.get_node = function(elem) {
			var html = this.get_row(elem)
			if(html) {
				return html.node;
			}
		};
		
		/**
		 * Utility function which returns an array of fields displayed in the portfolio table
		 * 
		 * @param port jQuery portfolio object
		 * @return array of fields
		 */
		this.fields = function(port) {
			var view = this.get_view(port);
			return port[0].options.displays[view];
		};
		
		/**
		 * Render new portfolio display if not available, otherwise
		 * render what is avilable in the cache
		 */
		this.display = function(el, view, fields) {
			var port      = $(el);
			var options   = port[0].options;
			var view_data = options.cacheview[view];
			var thead	  = options.ptable.thead;
			var tbody     = options.ptable.tbody;
			
			if(!view_data) {
				var  display_node = $.portfolio.display_node;
				var _header = '<tr>';
				$.each(fields,function(i,name) {
					_header += '<th>'+name+'</th>';
				});
				_header += '</tr>';
				
				options.root.newview(view, fields,tbody);
				
				view_data = {body: tbody.html(),
							 header: _header};
				options.cacheview[view] = view_data;
				thead.html(view_data.header);
			}
			else {
				thead.html(view_data.header);
				tbody.html(view_data.body);
			}
			_registerTableEvents(port);
		};
		
		/**
		 * Add new action to the portfolio. Action are interaction with the server via AjAX
		 */
		this.addAction = function(action) {
			actions[action.name] = action;
		};
		
		this.rcmenu = [];
			
		/**
		 * Perform a remote action on the server
		 * 
		 * @param $this - jQuery portfolio object
		 * @param name - String action name
		 * @param data - Object extra parameters/data to send to server
		 * @return the number of action performed
		 */
		this.action = function($this, name, data) {
			if(typeof name == "function") {
				var N = 0;
				$.each(actions, function(n,a) {
					if(name(a)) {
						N += 1;
						_request($this,a,data);
					}
				});
				return N;
			}
			else if(name) {
				var a = actions[name];
				if(a) {
					_request($this,a,data);
					return 1;
				}
			}
			return 0;
		}
		
	}
		
	});
	
	
	/**
	 * Extend the jQuery Object with the portfolio plugin 
	 */
	$.fn.extend({
        portfolio: $.portfolio.construct
	});
	
	
	$.portfolio.displayview = function(event,el) {
		var $this = $(el);
		var options = el.options;
		if(options.loaded) {return;}
		var view = $.portfolio.get_view($this);
		if(view) {
			var fields = options.displays[view];
			if(fields) {
				options.log("displaying view " + view);
				options.loaded = true;
				$.portfolio.display(el,view,fields);
			}
		}
	};
	
	
	/**
	 * Action for loading portfolios.
	 * It creates the root node and the portfoli tree
	 */
	$.portfolio.addAction({
		name: 'load',
		autoload: true,
		success: function(port,data) {
			var obj		 = port[0];
			var root 	 = data;
			var options  = obj.options;
			var log		 = options.log;
			var tree	 = {};
			options.tree = tree;
			make		 = $.portfolio.createNode;
			var count	 = 0;
			
			function parsePortfolioData(el, parent)  {
				count  += 1
				var node = make(parent, el, port);
				if(!node.id) {
					node.id = 'id-' + count;
				}
				tree[node.id] = node;
				log("Added new entry "+node.id+" to portfolio");
				if(el.positions) {
					$.each(el.positions, function(i,cid) {
						parsePortfolioData(cid,node);
					});
				}
				return node;
			}
			options.root = parsePortfolioData(root);
		},
		registerevents: function(port) {
			port.bind("load-start",function(event,el) {
				$.portfolio.clear($(el));
			});
			port.bind("load-end",$.portfolio.displayview);
		}
	});
	
	
	
	/**
	 * Portfolio Node class
	 * This jQuery plugin handle the portfolio node structure.
	 * 
	 * @param	options_	Object,			   	  	Options
	 * @param	parent_ 	portfolioNode or null	The parent Node
	 * @param	el 			Object					Data element used to create the portfolio node
	 * @parms   port		Object					The jquery portfolio holding the node
	 */
	$.portfolioNode = function(options_, parent_, el, port, log) {
		var me		   = this;
		var options	   = port[0].options;
		var noptions   = options_;
		var tree       = options.tree;
		var rightMenu  = null;
		var elemRightSelected = null;
		
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
    	
		function _level(node,l) {
			var p = node.parent;
			if(p) {
				return _level(p,l+1);
			}
			else  {
				return l;
			}
		}
		
		function _hide(node) {
			$.each(node.rows, function(name,row) {
				row.hide();
			});
		}
		
		function _show(node) {
			$.each(node.rows, function(name,row) {
				row.show();
			});
		}
		
		function _collapse(node) {
			if(!node.folder) {return;}
			node.expanded = false;
			$.each(node.children, function(i,child) {
				child.hide();
			});
			$.each(node.rows, function(name,row) {
				row.removeClass(options.expandClass);
			});
		}
		
		function _expand(node) {
			if(!node.folder) {return;}
			node.expanded = true;
			$.each(node.rows, function(name,row) {
				row.show();
				row.addClass(options.expandClass);
			});
			$.each(node.children, function(i,child) {
				child.show();
			});
		}
		
		/**
		 * Create a new node row for a view
		 * 
		 * @param fiels Array of field to display
		 * @body jQuery object for the tbody of the portfolio table
		 * @level recursive node level
		 */
		function _new_row(node, view, fields, body, level, hide) {
			var lev     = level || 1;
			node.level  = lev;
			row 	    = $('<tr></tr>').attr({'id':node.id}).css({'display':'table-row'});
			row[0].node = node;
			if(hide) {row.hide();}
			node.rows[view]   = row;
			$.each(fields,function(i,field) {
				row.append(node.get(i,field));
			});
			body.append(row);
			$.each(node.children, function(id,child) {
				_new_row(child, view, fields, body, lev+1, true);
			});
		};
		
		/**
		 * Obtain html string for a given key and position
		 * 
		 * @param i integer indicating column position
		 * @param key String indicating column header name
		 * @return String
		 */
		function _get(i,key) {
			var val   = this.data[key] || '';
			var c = $('<td></td>');
			if(i) {
				return c.html(''+val);
			}
			c.addClass('first');
			var padd    = paddfirst(this.level);
			var options = this.options;
			var label = $('<span></span>').html(val).addClass(options.labelClass);
			if(this.editable | this.canaddto) {
				label.addClass(options.editableClass);
			}
			if(this.movable) {
				label.addClass(options.movableClass);
			}
			if(this.folder) {
				label.addClass(options.folderClass);
				c.append($('<span></span>').addClass(options.togglerClass)
						.css({"padding-left":options.firstColumnIndent+"px"}));
			}
			else {
				label.addClass(options.positionClass);
			}
			return c.append(label).css({'padding-left': padd+'px'});
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
		
		// API
		this.options		= options;
		this.portfolio  	= port;
		this.children		= {};
		this.parent			= parent_,
		this.level			= _level(this,1);
		this.data			= el;
		this.folder			= el.folder ? el.folder : false;
		this.movable    	= el.movable ? el.movable : false;
		this.editable		= el.editable ? el.editable : false;
		this.canaddto		= el.canaddto ? el.canaddto : false;
		this.id				= el.id ? el.id : null;
		this.rows			= {};
		this.expanded		= false;
		
		this.newview		= function(view, fields, body) {_new_row(this, view, fields, body); return this;}
		this.get	      	= _get;
		this.removeNode    	= _removeNode;
		this.toggleBranch  	= function(){if(this.expanded) {_collapse(this);} else {_expand(this);}};
		this.expand			= function(){_expand(this);};
		this.show			= function(){_show(this);}
		this.hide			= function(){_hide(this);}
		this.setparent     	= _setparent;
		
		this.expand = function() {
			_expand(this);
			return this;
		};
		
		if(this.parent) {
			this.parent.children[this.id] = this;
		}
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
			var options = $this[0].options;
			var acts = $.portfolio.rcmenu;
			if(!acts.length) {return null;}
			return $('<div></div>').rightClickMenu($this, {actions: acts});
		}
	});
	
	
	//////////////////////////////////////////////////////////////////////
	//		PORTFOLIO EVENTS
	//
	//	This events are registered when the portfolio plugin is created
	//////////////////////////////////////////////////////////////////////
	
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
				var node = options.tree[html.id];
				if(node) {
					node.toggleBranch();
				}
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
	
	
	portf.addTableEvent({
		id: "rightClickMenu",
		register: function($this,elems) {
			var options = $this[0].options;
			if(!elems){elems = $this;}
			var pannel    = options.floatingPanels.rclkmenu;
			if(!pannel) {return;}
			var pels = $('span.label',elems);
			pannel.register(pels);
		}
	});
	
	
	/**
	 * Register the right-click menu, and the drag and drop functionality
	 */
	portf.addTableEvent({
		id: "Drag-Drop",
		register: function($this,elems) {
			var options = $this[0].options;
			if(!elems){elems = $this;}
			
			if(!options.editable) {return;}
			
			var editables = $('.'+options.editableClass,elems);
			var movables  = $('.'+options.movableClass,elems);
			
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
	
	
})(jQuery);
