# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   }
# META }

# MARKDOWN ********************

# # Tutorial: Discover relationships in a semantic model, using semantic link
# This tutorial illustrates how to interact with Power BI and detect relationships between tables, using the SemPy library while working in a Jupyter notebook. 

# MARKDOWN ********************

# ### In this tutorial, you learn how to:
# - Use components of semantic link's Python library ([SemPy](https://learn.microsoft.com/en-us/python/api/semantic-link-sempy)) that supports integration with Power BI and helps to automate data quality analysis. These components include:
#     - FabricDataFrame - a pandas-like structure enhanced with additional semantic information.
#     - Functions for pulling semantic models (Power BI datasets) from a Fabric workspace into your notebook.
# - Troubleshoot the process of relationship discovery for semantic models with multiple tables and interdependencies.

# MARKDOWN ********************

# ### Prerequisites
# 
# * A [Microsoft Fabric subscription](https://learn.microsoft.com/fabric/enterprise/licenses). Or sign up for a free [Microsoft Fabric (Preview) trial](https://learn.microsoft.com/fabric/get-started/fabric-trial).
# * Sign in to [Microsoft Fabric](https://fabric.microsoft.com/).
# * Go to the Data Science experience in Microsoft Fabric.
# * Select **Workspaces** from the left navigation pane to find and select your workspace. This workspace becomes your current workspace.
# * Download the _Customer Profitability Sample.pbix_ and _Customer Profitability Sample (auto).pbix_ datasets from the [fabric-samples GitHub repository](https://github.com/microsoft/fabric-samples/tree/main/docs-samples/data-science/datasets) and upload them to your workspace.
# * Open your notebook. You have two options:
#     * [Import this notebook into your workspace](https://learn.microsoft.com/en-us/fabric/data-engineering/how-to-use-notebook#import-existing-notebooks). You can import from the Data Science homepage.
#     * Alternatively, you can create [a new notebook](https://learn.microsoft.com/fabric/data-engineering/how-to-use-notebook#create-notebooks) to copy/paste code into cells.
# * In the Lakehouse explorer section of your notebook, add a new or existing lakehouse to your notebook. For more information on how to add a lakehouse, see [Attach a lakehouse to your notebook](https://learn.microsoft.com/en-us/fabric/data-science/tutorial-data-science-prepare-system#attach-a-lakehouse-to-the-notebooks).

# MARKDOWN ********************

# ## Set up the notebook
# 
# In this section, you set up a notebook environment with the necessary modules and data.
# 
# 1. Install `SemPy` from PyPI using the `%pip` in-line installation capability within the notebook:

# CELL ********************

%pip install semantic-link

# MARKDOWN ********************

# 2. Perform necessary imports of SemPy modules that you'll need later:

# CELL ********************

import sempy.fabric as fabric

from sempy.relationships import plot_relationship_metadata
from sempy.relationships import find_relationships
from sempy.fabric import list_relationship_violations

# MARKDOWN ********************

# 3. Import pandas for enforcing a configuration option that will help with output formatting:

# CELL ********************

import pandas as pd
pd.set_option('display.max_colwidth', None)

# MARKDOWN ********************

# ## Explore semantic models

# MARKDOWN ********************

# This tutorial uses a standard sample semantic model (Power BI dataset) [_Customer Profitability Sample.pbix_](https://github.com/microsoft/fabric-samples/blob/main/docs-samples/data-science/datasets/Customer%20Profitability%20Sample.pbix). For a description of the semantic model, see [Customer Profitability sample for Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/sample-customer-profitability).
# 
# Use SemPy's `list_datasets` function to explore semantic models in your current workspace:

# CELL ********************

fabric.list_datasets()

# MARKDOWN ********************

# For the rest of this notebook you'll use two versions of the Customer Profitability Sample semantic model:
# -  *Customer Profitability Sample*: the semantic model as it comes from Power BI samples with predefined table relationships
# -  *Customer Profitability Sample (auto)*: the same data, but relationships are limited to those that would be auto-detected by Power BI
#  

# MARKDOWN ********************

# ## Extract a sample semantic model with its predefined semantic model

# MARKDOWN ********************

# Load relationships that are predefined and stored within the _Customer Profitability Sample_ semantic model, using SemPy's `list_relationships` function. This function lists from the Tabular Object Model:

# CELL ********************

dataset = "Customer Profitability Sample"
relationships = fabric.list_relationships(dataset)
relationships

# MARKDOWN ********************

# Visualize the `relationships` DataFrame as a graph, using SemPy's `plot_relationship_metadata` function:

# CELL ********************

plot_relationship_metadata(relationships)

# MARKDOWN ********************

# This graph shows the "ground truth" for relationships between tables in this semantic model, as it reflects how they were defined in Power BI by a subject matter expert.

# MARKDOWN ********************

# ## Complement relationships discovery
# 
# If you started with relationships that were auto-detected by Power BI, you'd have a smaller set:

# CELL ********************

dataset = "Customer Profitability Sample (auto)"
autodetected = fabric.list_relationships(dataset)
plot_relationship_metadata(autodetected)

# CELL ********************


# MARKDOWN ********************

# Notice that Power BI's auto-detection missed many relationships. Moreover, two of the auto-detected relationships are semantically incorrect:
# 
# * `Executive[ID]` -> `Industry[ID]`
# * `BU[Executive_id]` -> `Industry[ID]`

# MARKDOWN ********************

# Discard the incorrectly identified relationships. But first, print out the relationships as a table:

# CELL ********************

autodetected

# MARKDOWN ********************

# Incorrect relationships to the `Industry` table appear in rows with index 3 and 4. Use this information to remove these rows.

# CELL ********************

autodetected.drop(index=[3,4], inplace=True)
autodetected

# MARKDOWN ********************

# Now you have correct, but incomplete relationships, as shown in the following visualization using `plot_relationship_metadata`:

# CELL ********************

plot_relationship_metadata(autodetected)

# MARKDOWN ********************

# Load all the tables from the semantic model, using SemPy's `list_tables` and `read_table` functions:

# CELL ********************

tables = {table: fabric.read_table(dataset, table) for table in fabric.list_tables(dataset)['Name']}

tables.keys()

# MARKDOWN ********************

# Find relationships between tables, using `find_relationships`, and review the log output to get some insights into how this function works:

# CELL ********************

suggested_relationships_all = find_relationships(
    tables,
    name_similarity_threshold=0.7,
    coverage_threshold=0.7,
    verbose=2
)

# MARKDOWN ********************

# Visualize newly discovered relationships:

# CELL ********************

plot_relationship_metadata(suggested_relationships_all)

# MARKDOWN ********************

# SemPy was able to detect all relationships! To limit the search to additional relationships that weren't identified previously, use the `exclude` parameter:

# CELL ********************

additional_relationships = find_relationships(
    tables,
    exclude=autodetected,
    name_similarity_threshold=0.7,
    coverage_threshold=0.7
)

additional_relationships

# MARKDOWN ********************

# ## Validate the relationships
# 
# To validate the relationships, you need to load the data from the _Customer Profitability Sample_ semantic model first:

# CELL ********************

dataset = "Customer Profitability Sample"
tables = {table: fabric.read_table(dataset, table) for table in fabric.list_tables(dataset)['Name']}

tables.keys()

# MARKDOWN ********************

# Once you have the data, you can check for overlap of primary and foreign key values by using the `list_relationship_violations` function. Supply the output of the `list_relationships` function as input to `list_relationship_violations`:

# CELL ********************

list_relationship_violations(tables, fabric.list_relationships(dataset))

# MARKDOWN ********************

# The relationship violations provide some interesting insights. For example, you see that one out of seven values in `Fact[Product Key]` is not present in `Product[Product Key]`, and this missing key is `50`.
# 
# Exploratory data analysis is an exciting process, and so is data cleaning. There's always something that the data is hiding, depending on how you look at it, what you want to ask, and so on. Semantic link provides you with new tools that you can use to achieve more with your data. 

# MARKDOWN ********************

# ## Related content
# 
# Check out other tutorials for semantic link / SemPy:
# 1. [Clean data with functional dependencies](https://github.com/microsoft/fabric-samples/blob/main/docs-samples/data-science/semantic-link-samples/data_cleaning_functional_dependencies_tutorial.ipynb)
# 1. [Analyze functional dependencies in a sample semantic model](https://github.com/microsoft/fabric-samples/blob/main/docs-samples/data-science/semantic-link-samples/powerbi_dependencies_tutorial.ipynb)
# 1. [Discover relationships in the _Synthea_ dataset, using semantic link](https://github.com/microsoft/fabric-samples/blob/main/docs-samples/data-science/semantic-link-samples/relationships_detection_tutorial.ipynb)
# 1. [Extract and calculate Power BI measures from a Jupyter notebook](https://github.com/microsoft/fabric-samples/blob/main/docs-samples/data-science/semantic-link-samples/powerbi_measures_tutorial.ipynb)

# MARKDOWN ********************

