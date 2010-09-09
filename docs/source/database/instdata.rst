.. _instrument-data:

Instrument data
===============

The instdata module provides various models for storing instruments and their associated data within the database.
This data is specific to the type of instrument as well as market data.

.. _dataid:

DataId:
-------

This the root identifier for all other models within this package.
It is the recommended means of accessing related models within the package.
For example to get a handle on a particular instrument you would call the ``instrument()`` method::
	
	>>>us_future_id = DataId.objects.get(code = 'TUM0')
	>>>us_future = us_future_id.instrument()
	
It is used in most queries. As a result it includes a number of denormalised datafields to assist performance.
Care should be taken when updating underlying models that the data stays consistent.
	
.. _vendor:
	
Vendor:
-------

This model provides a means of differentiating different data providers.
To get access to the actual implementation of a vendor use the method :meth:`interface()`.
For example::
	
	>>>yahoo_vendor = Vendor.objects.get(code='YAHOO')
	>>>yahoo_impl   = yahoo_vendor.interface()
	>>>yahoo_impl.get_history(...) #This method may be specific to that vendor
	
.. _vendorid:

VendorId:
---------

This is the identifier for a specific identifier for a particular :ref:`dataid` and :ref:`vendor`

.. _datafield:

Data Field:
-----------

This is provides the field identifier for storing market data related to a particular :ref:`dataid`
The attribute :attr:`format` defines the type of data that the field represents and consequently the table where the data will be stored.
You can access the relevant Market data class by using the method :meth:`get_mkt_data_cls`.
For example::

	>>>rating_field = DataField.objects.get(code='RATING')
	>>>rating_field.format
	>>>'string'
	>>>mkt_data_tbl = rating_field.get_mkt_data_cls()
	>>>mkt_data_tbl
	>>> XXXX
	
	

.. _vendordatafield:

Vendor Data Field:
------------------

This model allows one to specify the name of a given :ref:`datafield` for a specific :ref:`vendor`.
This is particularly useful for situations where different vendors have different names for a particular field.


Management Tools
========================

There are several management tools for the instrument database.

addccy
-----------
Add currencies objects to the DataId model::

	python manage.py addccy -d blb
	
add all the currencies and set their default vendor to blb.

loadecb
-------------
Another utility used for loading currency data into database. The data is extracted from the ECB web site::

	python manage.py loadecb
	
Make sura you run the `addccy` command before loading data.

  
	
	
	
	
		 
	


	
	
	
	
	
	
	