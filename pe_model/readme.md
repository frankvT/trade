.\pe_model

readme.txt
FvT 03/2025
# ReadMe

This repository contains Python code to run a simple partial equilibrium (pe) model of trade 
for a 'large' country. This means that world prices are not a gfoven for the importer who can 
impact world prices by varying its level of imports, for example by setting tariffs.

The model can used to illustrate the economic effects of tariffs, including on the various 
components of Domestic and World welfare. In particular it illustrates the idea of an 'optimal tariff' that
maximizes overall domestic welfare when the terms of trade effects of 'large' country model are taken into account.


The model can be configured in JSON files (see below) to allow for combinations of the following features: 
- types of functions: linear or linear in logarithms (i.e. constant elasticities)
- types of tariffs: specific (money per volume)  or ad-valorem (money per value)

In addition, the parameters for demand and supply functions can be fully set by the user.

The Python code follows a functional programming approach and exploits the fact that functions are 
first class objects that can be passed around. 

Installation:
Copy the model in a suitable directory

## Run:
a) within your favourite IDE or VS Code
b) from shell command line: pythyon runmodel.py
					or:
							python pe_model.py 

The script runmodel.py is a good starting point to develop simulations with the model. 
It shows how to calculate the 'optimal tariff' and creates a number of plots and text outputs.

## Requirements:
python 3.11.9
numpy 1.26.4
scipy 1.13.1
matplotlib 3.8.4
json 2.0.9

## Tree structure

+ .\pe_model	
    + basefuncs.py							Template definition of functions used
    + docs								Documents explaining more of the background economics
    + figures								Holds figures produced
        + linear_Consumer welfare.svg					By default the first part of the filename is the stem of the parameter file used
        + ...
    + init.json								JSON file holding constants for names of input and output files and directories
    + init.py								Reads JSON file init.json and provides constants to other modules 
    + kitchen.py							Various useful cutlery ands plates
    + params								Contains input paramter files in json format
        + linear.json							linear model 
        + linlog.json							linear in logarithms, i.e. constant elasticity
        + params_default.json
    + pe_model.py							The main code for pe_model 
    + plots.py								Code to plot results 
    + runmodel.py							Driver code to run model and simulate experiments
    + tariffs.py							Definition of tariff classes used in model
    + text									Holds text output produced
        + linear_out.txt						By default the first part of the filename is the stem of the parameter file used
        + ....