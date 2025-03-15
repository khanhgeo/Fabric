# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   }
# META }

# MARKDOWN ********************

# # Tutorial: Clean data with functional dependencies
# 
# In this tutorial, you use functional dependencies for data cleaning. A functional dependency exists when one column in a semantic model (a Power BI dataset) is a function of another column. For example, a _zip code_ column might determine the values in a _city_ column. A functional dependency manifests itself as a one-to-many relationship between the values in two or more columns within a DataFrame. This tutorial uses the _Synthea_ dataset to show how functional relationships can help to detect data quality problems.


# MARKDOWN ********************

# ### In this tutorial, you learn how to:
# - Apply domain knowledge to formulate hypotheses about functional dependencies in a semantic model.
# - Get familiarized with components of semantic link's Python library ([SemPy](https://learn.microsoft.com/en-us/python/api/semantic-link-sempy)) that helps to automate data quality analysis. These components include:
#     - FabricDataFrame - a pandas-like structure enhanced with additional semantic information.
#     - Useful functions that automate the evaluation of hypotheses about functional dependencies and that identify violations of relationships in your semantic models.

# MARKDOWN ********************

# ### Prerequisites
# 
# * A [Microsoft Fabric subscription](https://learn.microsoft.com/fabric/enterprise/licenses). Or sign up for a free [Microsoft Fabric (Preview) trial](https://learn.microsoft.com/fabric/get-started/fabric-trial).
# * Sign in to [Microsoft Fabric](https://fabric.microsoft.com/).
# * Go to the Data Science experience in Microsoft Fabric.
# * Select **Workspaces** from the left navigation pane to find and select your workspace. This workspace becomes your current workspace.
# * Open your notebook. You have two options:
#     * [Import this notebook into your workspace](https://learn.microsoft.com/en-us/fabric/data-engineering/how-to-use-notebook#import-existing-notebooks). You can import from the Data Science homepage.
#     * Alternatively, you can create [a new notebook](https://learn.microsoft.com/fabric/data-engineering/how-to-use-notebook#create-notebooks) to copy/paste code into cells.
# * In the Lakehouse explorer section of your notebook, add a new or existing lakehouse to your notebook. For more information on how to add a lakehouse, see [Attach a lakehouse to your notebook](https://learn.microsoft.com/en-us/fabric/data-science/tutorial-data-science-prepare-system#attach-a-lakehouse-to-the-notebooks).


# MARKDOWN ********************

# ## Set up the notebook
# 
# In this section, you set up a notebook environment with the necessary modules and data.

# MARKDOWN ********************

# 1. Install `SemPy` from PyPI, using the `%pip` in-line installation capability within the notebook:

# CELL ********************

%pip install semantic-link

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# 2. Perform necessary imports of modules that you'll need later:

# CELL ********************

import pandas as pd
import sempy.fabric as fabric
from sempy.fabric import FabricDataFrame
from sempy.dependencies import plot_dependency_metadata
from sempy.samples import download_synthea

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# 3. Pull the sample data. For this tutorial, you use the _Synthea_ dataset of synthetic medical records (small version for simplicity):

# CELL ********************

download_synthea(which='small')

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Explore the data

# MARKDOWN ********************

# Initialize a ``FabricDataFrame`` with the content of the _providers.csv_ file:

# CELL ********************

providers = FabricDataFrame(pd.read_csv("synthea/csv/providers.csv"))
providers.head()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# Check for data quality issues with SemPy's `find_dependencies` function by plotting a graph of auto-detected functional dependencies:

# CELL ********************

deps = providers.find_dependencies()
plot_dependency_metadata(deps)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# The graph of functional dependencies shows that `Id` determines `NAME` and  `ORGANIZATION` (indicated by the solid arrows), which is expected, since `Id` is unique:

# CELL ********************

providers.Id.is_unique

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Analyze functional dependencies in depth

# MARKDOWN ********************

# The functional dependencies graph also shows that `ORGANIZATION` determines `ADDRESS` and `ZIP`, as expected. However, you might expect `ZIP` to also determine `CITY`, but the dashed arrow indicates that the dependency is only approximate, pointing towards a data quality issue.
# 
# There are other peculiarities in the graph. For example, `NAME` does not determine `GENDER`, `Id`, `SPECIALITY` or `ORGANIZATION`. Each of these might be worth investigating.
# 
# Take a deeper look at the approximate relationship between `ZIP` and `CITY`, by using SemPy's `list_dependency_violations` function to see a tabular list of violations:

# CELL ********************

providers.list_dependency_violations('ZIP', 'CITY')

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# If the number of violations is small, it can be helpful to draw a graph with SemPy's `plot_dependency_violations` visualization function:

# CELL ********************

providers.plot_dependency_violations('ZIP', 'CITY')

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# The plot of dependency violations shows values for `ZIP` on the left hand side, and values for `CITY` on the right hand side. An edge connects a zip code on the left with a city on the right if there is a row that contains these two values. The edges are annotated with the count of such rows. For example, there are two rows with zip code 02747-1242, one row with city "NORTH DARTHMOUTH" and the other with city "DARTHMOUTH", as shown in the previous plot and the following code:

# CELL ********************

providers[providers.ZIP == '02747-1242'].CITY.value_counts()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# The plot also shows that among the rows that have `CITY` as "DARTHMOUTH", nine rows have a `ZIP` of 02747-1262; one row has a `ZIP` of 02747-1242; and one row has a `ZIP` of 02747-2537:

# CELL ********************

providers[providers.CITY == 'DARTMOUTH'].ZIP.value_counts()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# There are other zip codes associated with "DARTMOUTH", but these aren't shown in the graph of dependency violations, as they don't hint at data quality issues. For example, the zip code "02747-4302" is uniquely associated to "DARTMOUTH" and doesn't show up in the graph of dependency violations:

# CELL ********************

providers[providers.ZIP == '02747-4302'].CITY.value_counts()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Summarize data quality issues detected with SemPy

# MARKDOWN ********************

# Going back to the graph of dependency violations, you can see that there are actually several interesting data quality issues present in this semantic model:
# 
# - Some city names are all uppercase. This issue is easy to fix using string methods.
# - Some city names have qualifiers (or prefixes), such as "North" and "East". For example, the zip code "2128" maps to "EAST BOSTON" once and to "BOSTON" once. A similar issue occurs between "NORTH DARTHMOUTH" and "DARTHMOUTH". You could try to drop these qualifiers or map the zip codes to the city with the most common occurrence.
# - There are typos in some cities, such as "PITTSFIELD" vs. "PITTSFILED" and "NEWBURGPORT vs. "NEWBURYPORT". In the case of "NEWBURGPORT" this typo could be fixed by using the most common occurrence. In the case of "PITTSFIELD", having only one occurrence each makes it much harder for automatic disambiguation without external knowledge or the use of a language model.
# - Sometimes, prefixes like "West" are abbreviated to a single letter "W". This could potentially be fixed with a simple replace, if all occurrences of "W" stand for "West".
# - The zip code "02130" maps to "BOSTON" once and "Jamaica Plain" once. This issue is not easy to fix, but if there was more data, mapping to the most common occurrence could be a potential solution.


# MARKDOWN ********************

# ## Clean data

# MARKDOWN ********************

# Fix the capitalization issues by changing all capitalization to title case:

# CELL ********************

providers['CITY'] = providers.CITY.str.title()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# Run the violation detection again to see that some of the ambiguities are gone (the number of violations is smaller):

# CELL ********************

providers.list_dependency_violations('ZIP', 'CITY')

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# At this point, you could refine your data more manually, but one potential data cleanup task is to drop rows that violate functional constraints between columns in the data, by using SemPy's `drop_dependency_violations` function. 
# 
# For each value of the determinant variable, `drop_dependency_violations` works by picking the most common value of the dependent variable and dropping all rows with other values. You should apply this operation only if you're confident that this statistical heuristic would lead to the correct results for your data. Otherwise you should write your own code to handle the detected violations as needed.
# 
# Run the `drop_dependency_violations` function on the `ZIP` and `CITY` columns:

# CELL ********************

providers_clean = providers.drop_dependency_violations('ZIP', 'CITY')

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# List any dependency violations between `ZIP` and `CITY`:

# CELL ********************

providers_clean.list_dependency_violations('ZIP', 'CITY')

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# The empty list shows that there are no more violations of the functional constraint **CITY -> ZIP**.

# MARKDOWN ********************

# ## Related content
# 
# Check out other tutorials for semantic link / SemPy:
# 1. [Analyze functional dependencies in a sample semantic model](https://github.com/microsoft/fabric-samples/blob/main/docs-samples/data-science/semantic-link-samples/powerbi_dependencies_tutorial.ipynb)
# 1. [Discover relationships in the _Synthea_ dataset using semantic link](https://github.com/microsoft/fabric-samples/blob/main/docs-samples/data-science/semantic-link-samples/relationships_detection_tutorial.ipynb)
# 1. [Discover relationships in a semantic model, using semantic link](https://github.com/microsoft/fabric-samples/blob/main/docs-samples/data-science/semantic-link-samples/powerbi_relationships_tutorial.ipynb)
# 1. [Extract and calculate Power BI measures from a Jupyter notebook](https://github.com/microsoft/fabric-samples/blob/main/docs-samples/data-science/semantic-link-samples/powerbi_measures_tutorial.ipynb)

# MARKDOWN ********************

