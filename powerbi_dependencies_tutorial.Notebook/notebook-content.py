# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   }
# META }

# MARKDOWN ********************

# # Tutorial: Analyze functional dependencies in a sample semantic model
# 
# In this tutorial, you build upon prior work done by a Power BI analyst and stored in the form of semantic models (Power BI datasets). By using SemPy in the Synapse Data Science experience within Microsoft Fabric, you analyze functional dependencies that exist in columns of a DataFrame. This analysis helps to discover non-trivial data quality issues in order to gain more accurate insights.


# MARKDOWN ********************

# ### In this tutorial, you learn how to:
# - Apply domain knowledge to formulate hypotheses about functional dependencies in a semantic model.
# - Get familiarized with components of semantic link's Python library ([SemPy](https://learn.microsoft.com/en-us/python/api/semantic-link-sempy)) that supports integration with Power BI and helps to automate data quality analysis. These components include:
#     - FabricDataFrame - a pandas-like structure enhanced with additional semantic information.
#     - Useful functions for pulling semantic models from a Fabric workspace into your notebook.
#     - Useful functions that automate the evaluation of hypotheses about functional dependencies and that identify violations of relationships in your semantic models.

# MARKDOWN ********************

# ### Prerequisites
# 
# * A [Microsoft Fabric subscription](https://learn.microsoft.com/fabric/enterprise/licenses). Or sign up for a free [Microsoft Fabric (Preview) trial](https://learn.microsoft.com/fabric/get-started/fabric-trial).
# * Sign in to [Microsoft Fabric](https://fabric.microsoft.com/).
# * Go to the Data Science experience in Microsoft Fabric.
# * Select **Workspaces** from the left navigation pane to find and select your workspace. This workspace becomes your current workspace.
# * Download the _Customer Profitability Sample.pbix_ dataset from the [fabric-samples GitHub repository](https://github.com/microsoft/fabric-samples/blob/main/docs-samples/data-science/datasets/Customer%20Profitability%20Sample.pbix) and upload it to your workspace.
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

# 2. Perform necessary imports of modules that you'll need later:

# CELL ********************

import sempy.fabric as fabric
from sempy.dependencies import plot_dependency_metadata

# MARKDOWN ********************

# ## Load and preprocess the data

# MARKDOWN ********************

# This tutorial uses a standard sample semantic model [Customer Profitability Sample.pbix](https://github.com/microsoft/fabric-samples/tree/main/docs-samples/data-science/datasets). For a description of the semantic model, see [Customer Profitability sample for Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/sample-customer-profitability).
# 
# Load the Power BI data into FabricDataFrames, using SemPy's `read_table` function:

# CELL ********************

dataset = "Customer Profitability Sample"
customer = fabric.read_table(dataset, "Customer")
customer.head()

# MARKDOWN ********************

# Load the `State` table into a FabricDataFrame:

# CELL ********************

state = fabric.read_table(dataset, "State")
state.head()

# MARKDOWN ********************

# While the output looks like a pandas DataFrame, you actually initialized a data structure called a ``FabricDataFrame`` that supports some useful operations on top of pandas.

# CELL ********************

type(customer)

# MARKDOWN ********************

# Join the `customer` and `state` DataFrames:

# CELL ********************

customer_state_df = customer.merge(state, left_on="State", right_on="StateCode",  how='left')
customer_state_df.head()

# MARKDOWN ********************

# ## Identify functional dependencies

# MARKDOWN ********************

# A functional dependency manifests itself as a one-to-many relationship between the values in two (or more) columns within a DataFrame. These relationships can be used to automatically detect data quality problems. 
# 
# Run SemPy's `find_dependencies` function on the merged DataFrame to identify any existing functional dependencies between values in the columns:

# CELL ********************

dependencies = customer_state_df.find_dependencies()
dependencies

# MARKDOWN ********************

# Visualize the identified dependencies by using SemPy's ``plot_dependency_metadata`` function:

# CELL ********************

plot_dependency_metadata(dependencies)

# MARKDOWN ********************

# As expected, the functional dependencies graph shows that the `Customer` column determines some columns like `City`, `Postal Code`, and `Name`. 
# 
# Surprisingly, the graph doesn't show a functional dependency between `City` and `Postal Code`, probably because there are many violations in the relationships between the columns. You can use SemPy's ``plot_dependency_violations`` function to visualize violations of dependencies between specific columns.

# MARKDOWN ********************

# ## Explore the data for quality issues

# CELL ********************

customer_state_df.plot_dependency_violations('Postal Code', 'City')

# MARKDOWN ********************

# The plot of dependency violations shows values for `Postal Code` on the left hand side, and values for `City` on the right hand side. An edge connects a `Postal Code` on the left with a `City` on the right if there is a row that contains these two values. The edges are annotated with the count of such rows. For example, there are two rows with postal code 20004, one with city "North Tower" and the other with city "Washington".
# 
# Moreover, the plot shows a few violations and many empty values.

# CELL ********************

customer_state_df['Postal Code'].isna().sum()

# MARKDOWN ********************

# 50 rows have NA for postal code. 
# 
# Next, drop rows with empty values. Then, find dependencies using the `find_dependencies` function. Notice the additional parameter `verbose=1` that offers a glimpse into the internal workings of SemPy:

# CELL ********************

customer_state_df2=customer_state_df.dropna()
customer_state_df2.find_dependencies(verbose=1)

# MARKDOWN ********************

# The conditional entropy for `Postal Code` and `City` is 0.049. This value can be explained by the fact there are functional dependency violations. Before you fix the violations, raise the threshold on conditional entropy from the default value of `0.01` to `0.05`, just to see the dependencies. Lower thresholds result in fewer dependencies (or higher selectivity).

# CELL ********************

plot_dependency_metadata(customer_state_df2.find_dependencies(threshold=0.05))

# MARKDOWN ********************

# If you apply domain knowledge of which entity determines values of other entities, this dependencies graph seems accurate. 
# 
# Now, explore more data quality issues that were detected. For example, `City` and `Region` are joined by a dashed arrow, which indicates that the dependency is only approximate. This could imply that there is a partial functional dependency.

# CELL ********************

customer_state_df.list_dependency_violations('City', 'Region')

# MARKDOWN ********************

# Take a closer look at each of the cases where a non-empty `Region` value causes a violation:

# CELL ********************

customer_state_df[customer_state_df.City=='Downers Grove']

# MARKDOWN ********************

# Downers Grove is a [city in Illinois](https://en.wikipedia.org/wiki/Downers_Grove,_Illinois), not Nebraska.

# CELL ********************

customer_state_df[customer_state_df.City=='Fremont']

# MARKDOWN ********************

# There is a city called [Fremont in California](https://en.wikipedia.org/wiki/Fremont,_California). However, for Texas, the search engine returns [Premont](https://en.wikipedia.org/wiki/Premont,_Texas), not Fremont!

# MARKDOWN ********************

# It's also suspicious to see violations of the dependency between `Name` and `Country/Region`, as signified by the dotted line in the original graph of dependency violations (before dropping the rows with empty values).

# CELL ********************

customer_state_df.list_dependency_violations('Name', 'Country/Region')

# MARKDOWN ********************

# It appears that one customer, 'SDI Design' is present in two regions - United States and Canada. This may not be a semantic violation, but may just be an uncommon case. Still, it's worth taking a close look:

# CELL ********************

customer_state_df[customer_state_df.Name=='SDI Design']

# MARKDOWN ********************

# Further inspection shows that it's actually two different customers (from different industries) with the same name.
# 
# Exploratory data analysis is an exciting process, and so is data cleaning. There's always something that the data is hiding, depending on how you look at it, what you want to ask, and so on. Semantic link provides you with new tools that you can use to achieve more with your data. 

# MARKDOWN ********************

# ## Related content
# 
# Check out other tutorials for semantic link / SemPy:
# 1. [Clean data with functional dependencies](https://github.com/microsoft/fabric-samples/blob/main/docs-samples/data-science/semantic-link-samples/data_cleaning_functional_dependencies_tutorial.ipynb)
# 1. [Discover relationships in the _Synthea_ dataset using semantic link](https://github.com/microsoft/fabric-samples/blob/main/docs-samples/data-science/semantic-link-samples/relationships_detection_tutorial.ipynb)
# 1. [Discover relationships in a semantic model, using semantic link](https://github.com/microsoft/fabric-samples/blob/main/docs-samples/data-science/semantic-link-samples/powerbi_relationships_tutorial.ipynb)
# 1. [Extract and calculate Power BI measures from a Jupyter notebook](https://github.com/microsoft/fabric-samples/blob/main/docs-samples/data-science/semantic-link-samples/powerbi_measures_tutorial.ipynb)

# MARKDOWN ********************

