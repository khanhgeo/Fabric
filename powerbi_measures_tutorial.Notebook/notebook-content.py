# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "environment": {
# META       "environmentId": "2e40da96-f6f6-b1fc-4f27-b1234b85c253",
# META       "workspaceId": "00000000-0000-0000-0000-000000000000"
# META     }
# META   }
# META }

# MARKDOWN ********************

# # Tutorial: Extract and calculate Power BI measures from a Jupyter notebook
# This tutorial illustrates how to use SemPy to calculate measures in semantic models (Power BI datasets).

# MARKDOWN ********************

# ### In this tutorial, you learn how to:
# - Evaluate Power BI measures programmatically via a Python interface of semantic link's Python library ([SemPy](https://learn.microsoft.com/en-us/python/api/semantic-link-sempy)), apply filtering, grouping, and so on.
# - Get familiarized with components of SemPy that help bridge the gap between AI and BI. These components include:
#     - FabricDataFrame - a pandas-like structure enhanced with additional semantic information.
#     - Useful functions that allow you to fetch semantic models, including raw data, configurations, and measures.

# MARKDOWN ********************

# ### Prerequisites
# 
# * A [Microsoft Fabric subscription](https://learn.microsoft.com/fabric/enterprise/licenses). Or sign up for a free [Microsoft Fabric (Preview) trial](https://learn.microsoft.com/fabric/get-started/fabric-trial).
# * Sign in to [Microsoft Fabric](https://fabric.microsoft.com/).
# * Go to the Data Science experience in Microsoft Fabric.
# * Select **Workspaces** from the left navigation pane to find and select your workspace. This workspace becomes your current workspace.
# * Download the [_Retail Analysis Sample PBIX.pbix_](https://download.microsoft.com/download/9/6/D/96DDC2FF-2568-491D-AAFA-AFDD6F763AE3/Retail%20Analysis%20Sample%20PBIX.pbix) dataset and upload it to your workspace.
# * Open your notebook. You have two options:
#     * [Import this notebook into your workspace](https://learn.microsoft.com/en-us/fabric/data-engineering/how-to-use-notebook#import-existing-notebooks). You can import from the Data Science homepage.
#     * Alternatively, you can create [a new notebook](https://learn.microsoft.com/fabric/data-engineering/how-to-use-notebook#create-notebooks) to copy/paste code into cells.
# * In the Lakehouse explorer section of your notebook, add a new or existing lakehouse to your notebook. For more information on how to add a lakehouse, see [Attach a lakehouse to your notebook](https://learn.microsoft.com/en-us/fabric/data-science/tutorial-data-science-prepare-system#attach-a-lakehouse-to-the-notebooks).


# MARKDOWN ********************

# ## Set up the notebook
# 
# In this section, you set up a notebook environment with the necessary modules and data.
# 
# 1. install `SemPy` from PyPI using the `%pip` in-line installation capability within the notebook:

# CELL ********************

# %pip install semantic-link

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# 2. Perform necessary imports of modules that you'll need later: 

# CELL ********************

import sempy.fabric as fabric

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# 3. You can connect to the Power BI workspace. List the semantic models in the workspace:

# CELL ********************

fabric.list_datasets()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# In this tutorial, you use the _Retail Analysis Sample PBIX_ semantic model:

# CELL ********************

dataset = "Retail Analysis Sample PBIX"

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# Start by listing measures in the semantic model, using SemPy's `list_measures` function as follows:

# CELL ********************

fabric.list_measures(dataset)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Evaluate measures

# MARKDOWN ********************

# ### Evaluate a raw measure

# MARKDOWN ********************

# In the following code, use SemPy's `evaluate_measure` function to calculate a preconfigured measure that is called "Average Selling Area Size". You can see the underlying formula for this measure in the output of the previous cell. 

# CELL ********************

fabric.evaluate_measure(dataset, measure="Average Selling Area Size")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### Evaluate a measure with `groupby_columns`

# MARKDOWN ********************

# You can group the measure output by certain columns by supplying the additional parameter `groupby_columns`:

# CELL ********************

fabric.evaluate_measure(dataset, measure="Average Selling Area Size", groupby_columns=["Store[Chain]", "Store[DistrictName]"])

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# In the previous code, you grouped by the columns `Chain` and `DistrictName` of the `Store` table in the semantic model.

# MARKDOWN ********************

# ### Evaluate a measure with filters

# MARKDOWN ********************

# You can also use the `filters` parameter to specify specific values that the result can contain for particular columns:

# CELL ********************

fabric.evaluate_measure(dataset, \
                        measure="Total Units Last Year", \
                        groupby_columns=["Store[Territory]"], \
                        filters={"Store[Territory]": ["PA", "TN", "VA"], "Store[Chain]": ["Lindseys"]})

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# Note that `Store` is the name of the table, `Territory` is the name of the column, and `PA` is one of the values that are allowed by the filter.

# MARKDOWN ********************

# ### Evaluate a measure across multiple tables

# MARKDOWN ********************

# These groups can span multiple tables in the semantic model.

# CELL ********************

fabric.evaluate_measure(dataset, measure="Total Units Last Year", groupby_columns=["Store[Territory]", "Sales[ItemID]"])

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### Evaluate multiple measures

# MARKDOWN ********************

# The function `evaluate_measure` allows you to supply identifiers of multiple measures and output the calculated values in the same DataFrame:

# CELL ********************

fabric.evaluate_measure(dataset, measure=["Average Selling Area Size", "Total Stores"], groupby_columns=["Store[Chain]", "Store[DistrictName]"])

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Use Power BI XMLA connector

# MARKDOWN ********************

# The default semantic model client is backed by Power BI's REST APIs. If there are any issues running queries with this client, it's possible to switch the back end to Power BI's XMLA interface using `use_xmla=True`. The SemPy parameters remain the same for measure calculation with XMLA.

# CELL ********************

fabric.evaluate_measure(dataset, \
                        measure=["Average Selling Area Size", "Total Stores"], \
                        groupby_columns=["Store[Chain]", "Store[DistrictName]"], \
                        filters={"Store[Territory]": ["PA", "TN", "VA"], "Store[Chain]": ["Lindseys"]}, \
                        use_xmla=True)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Related content
# 
# Check out other tutorials for semantic link / SemPy:
# 1. [Clean data with functional dependencies](https://github.com/microsoft/fabric-samples/blob/main/docs-samples/data-science/semantic-link-samples/data_cleaning_functional_dependencies_tutorial.ipynb)
# 1. [Analyze functional dependencies in a sample semantic model](https://github.com/microsoft/fabric-samples/blob/main/docs-samples/data-science/semantic-link-samples/powerbi_dependencies_tutorial.ipynb)
# 1. [Discover relationships in the _Synthea_ dataset, using semantic link](https://github.com/microsoft/fabric-samples/blob/main/docs-samples/data-science/semantic-link-samples/relationships_detection_tutorial.ipynb)
# 1. [Discover relationships in a semantic model, using semantic link](https://github.com/microsoft/fabric-samples/blob/main/docs-samples/data-science/semantic-link-samples/powerbi_relationships_tutorial.ipynb)

# MARKDOWN ********************

