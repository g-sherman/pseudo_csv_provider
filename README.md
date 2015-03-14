QGIS data providers are written in C++, however it is possible to simulate a data provider in Python using a memory layer 
and some code to interface with your data.

Why would you want to do this? Typically you should use the QGIS data providers, but here are some reasons why you may want to give it a go:

* There is no QGIS data provider
* The generic access available through OGR doesn't provide all the features you need
* You have no desire to write a provider in C++
* No one will write a C++ provider for you, for any amount of money

If you go this route you are essentially creating a bridge that connects QGIS
and your data store, be it flat file, database, or some other binary format. If
Python can "talk" to your data store, you can write a pseudo-provider.


To illustrate the concept, we'll create a provider for CSV files that allows you
to create a layer and have full editing capabilities using QGIS and the Python
`csv` module.


The provider will:

* Create a memory layer from a CSV file
* Create fields in the layer based on integer, float, or string values in the CSV
* Write changes back to the CSV file
* Require the CSV file to have an X and Y field 
* Support only Point geometries

