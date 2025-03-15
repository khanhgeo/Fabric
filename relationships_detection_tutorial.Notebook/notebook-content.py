# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   }
# META }

# MARKDOWN ********************

# # Tutorial: Discover relationships in the _Synthea_ dataset using semantic link

# MARKDOWN ********************

# This tutorial illustrates how to detect relationships in the public _Synthea_ dataset, using semantic link. 
# 
# When you're working with new data or working without an existing data model, it can be helpful to discover relationships automatically. This relationship detection can help you to:
# 
#    * understand the model at a high level,
#    * gain more insights during exploratory data analysis,
#    * validate updated data or new, incoming data, and
#    * clean data.
# 
# Even if relationships are known in advance, a search for relationships can help with better understanding of the data model or identification of data quality issues. 
# 
# In this tutorial, you begin with a simple baseline example where you experiment with only three tables so that connections between them are easy to follow. Then, you'll show a more complex example with a larger table set.

# MARKDOWN ********************

# ### In this tutorial, you learn how to: 
# - Use components of semantic link's Python library (SemPy) that supports integration with Power BI and helps to automate data  analysis. These components include:
#     - FabricDataFrame - a pandas-like structure enhanced with additional semantic information.
#     - Functions for pulling semantic models (Power BI datasets) from a Fabric workspace into your notebook.
#     - Functions that automate the discovery and visualization of relationships in your semantic models.
# - Troubleshoot the process of relationship discovery for semantic models with multiple tables and interdependencies.

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
# 
# 1. Install `SemPy` from PyPI using the `%pip` in-line installation capability within the notebook:

# CELL ********************

%pip install semantic-link

# MARKDOWN ********************

# 2. Perform necessary imports of SemPy modules that you'll need later:

# CELL ********************

import pandas as pd

from sempy.samples import download_synthea
from sempy.relationships import (
    find_relationships,
    list_relationship_violations,
    plot_relationship_metadata
)

# MARKDOWN ********************

# 3. Import pandas for enforcing a configuration option that will help with output formatting:

# CELL ********************

import pandas as pd
pd.set_option('display.max_colwidth', None)

# MARKDOWN ********************

# 4. Pull the sample data. For this tutorial, you'll use the _Synthea_ dataset of synthetic medical records (small version for simplicity):

# CELL ********************

download_synthea(which='small')

# MARKDOWN ********************

# ## Detect relationships on a small subset of _Synthea_ tables

# MARKDOWN ********************

# Select three tables from a larger set:
# * `patients` specifies patient information.
# * `encounters` specifies the patients that had medical encounters (e.g. a medical appointment, procedure) 
# * `providers` specifies which medical providers attended to the patients. 
# 
# The `encounters` table resolves a many-to-many relationship between `patients` and `providers` and can be described as an [associative entity](https://wikipedia.org/wiki/Associative_entity):

# CELL ********************

patients = pd.read_csv('synthea/csv/patients.csv')
providers = pd.read_csv('synthea/csv/providers.csv')
encounters = pd.read_csv('synthea/csv/encounters.csv')

# MARKDOWN ********************

# Find relationships between the tables using  SemPy's ``find_relationships`` function:

# CELL ********************

suggested_relationships = find_relationships([patients, providers, encounters])
suggested_relationships

# MARKDOWN ********************

# Visualize the relationships DataFrame as a graph, using SemPy's `plot_relationship_metadata` function.
# The function lays out the hierarchy from left to right, which corresponds to "from" and "to" tables in the output. In other words, the independent "from" tables on the left use their foreign keys to point to their "to" dependency tables on the right. Each entity box shows columns that participate on either the "from" or "to" side of a relationship.

# CELL ********************

plot_relationship_metadata(suggested_relationships)

# MARKDOWN ********************

# By default, relationships are generated as "m:1" (not as "1:m") or "1:1". The "1:1" relationships can be generated one or both ways, depending on if the ratio of mapped values to all values exceed `coverage_threshold` in just one or both directions. Later in this tutorial, you'll cover the less frequent case of "m:m" relationships.

# MARKDOWN ********************

# ## Troubleshoot relationship detection issues
# 
# The baseline example shows a successful relationship detection on clean _Synthea_ data. In practice, the data is rarely clean, which will prevent successful detection. There are several techniques that can be useful when the data isn't clean.
# 
# This section of the tutorial will address relationship detection when the semantic model contains dirty data. To begin, you'll manipulate the original DataFrames to obtain "dirty" data.

# CELL ********************

# create a dirty 'patients' dataframe by dropping some rows using head() and duplicating some rows using concat()
patients_dirty = pd.concat([patients.head(1000), patients.head(50)], axis=0)

# create a dirty 'providers' dataframe by dropping some rows using head()
providers_dirty = providers.head(5000)

# the dirty dataframes have fewer records than the clean ones
print(len(patients_dirty))
print(len(providers_dirty)) 

# MARKDOWN ********************

# For comparison, print sizes of the original tables:

# CELL ********************

print(len(patients))
print(len(providers))

# MARKDOWN ********************

# Find relationships between the tables using  SemPy's ``find_relationships`` function:

# CELL ********************

find_relationships([patients_dirty, providers_dirty, encounters])

# MARKDOWN ********************

# As shown in the previous output, no relationships have been detected due to the errors that you had introduced earlier to create the "dirty" semantic model.

# MARKDOWN ********************

# ### Use validation
# 
# Validation is the best tool for troubleshooting relationship detection failures because:
# 
#    * It reports clearly why a particular relationship does not follow the Foreign Key rules and therefore cannot be detected.
#    * It runs very fast with large semantic models because it focuses only on the declared relationships and does not perform a search.
# 
# Validation can use any DataFrame with columns similar to the one generated by `find_relationships`. In the following code, the `suggested_relationships` DataFrame refers to `patients` rather than `patients_dirty`, but you can alias the DataFrames with a dictionary:

# CELL ********************

dirty_tables = {
    "patients": patients_dirty,
    "providers" : providers_dirty,
    "encounters": encounters
}

errors = list_relationship_violations(dirty_tables, suggested_relationships)
errors

# MARKDOWN ********************

# ### Loosen search criteria
# 
# In more murky scenarios, you can try loosening your search criteria. This method increases the possibility of false positives. 
# Set `include_many_to_many=True` and evaluate if it helps:

# CELL ********************

find_relationships(dirty_tables, include_many_to_many=True, coverage_threshold=1)

# MARKDOWN ********************

# The results show that the relationship from `encounters` to `patients` was detected, but there are two problems:
# 
#    * The relationship indicates a direction from `patients` to `encounters` which is an inverse of the expected. This is because all
#      `patients` happened to be covered by `encounters` (`Coverage From` is 1.0) while `encounters` are only partially covered
#      by `patients` (`Coverage To` = 0.85), since patients rows are missing.
#    * There is an accidental match on a low cardinality `GENDER` column, which happens to match by name and value in both tables,
#      but it is not an "m:1" relationship of interest. The low cardinality is indicated by `Unique Count From` and
#      `Unique Count To` columns.

# MARKDOWN ********************

# Rerun ``find_relationships`` to look only for "m:1" relationships, but with a lower ``coverage_threshold=0.5``:

# CELL ********************

find_relationships(dirty_tables, include_many_to_many=False, coverage_threshold=0.5)

# MARKDOWN ********************

# The result shows the correct direction of the relationships from `encounters` to `providers`. However, the relationship from `encounters` to `patients` is not detected, because `patients` is not unique, so it cannot be on the "One" side of "m:1" relationship.
#      
# Loosen both `include_many_to_many=True` and `coverage_threshold=0.5`:

# CELL ********************

find_relationships(dirty_tables, include_many_to_many=True, coverage_threshold=0.5)

# MARKDOWN ********************

# Now both relationships of interest are visible, but there is a lot more noise:
# 
#    * The low cardinality match on `GENDER` is present.
#    * A higher cardinality "m:m" match on `ORGANIZATION` appeared, making it apparent that `ORGANIZATION` is likely
#      a column de-normalized to both tables.

# MARKDOWN ********************

# ### Match column names
# 
# By default, SemPy will consider as matches only attributes that show name similarity, taking advantage of the fact that
# database designers usually name related columns the same way. This helps to avoid spurious relationships, which occur most frequently with low cardinality integer keys. For example, if there are `1,2,3,...,10` product categories and `1,2,3,...,10` order status code, they'll be confused with each other when only looking at value mappings without taking column names into account. Spurious relationships should not be a problem with GUID-like keys.
# 
# SemPy looks at a similarity between column names and table names. The matching is approximate and case insensitive. It ignores the most frequently encountered "decorator" substrings such as "id", "code", "name", "key", "pk", "fk". As a result, the most typical match cases are:
# 
#    * an attribute called 'column' in entity 'foo' will be matched with an attribute called 'column' (also 'COLUMN' or 'Column') in entity 'bar'.
#    * an attribute called 'column' in entity 'foo' will be matched with an attribute called 'column_id' in 'bar'.
#    * an attribute called 'bar' in entity 'foo' will be matched with an attribute called 'code' in 'bar'.
# 
# By matching column names first, the detection runs faster.
# 
# To understand which columns are selected for further evaluation, use the `verbose=2` option
# (`verbose=1` lists only the entities being processed).
# 
# The `name_similarity_threshold` parameter determines how columns will be compared. The threshold of 1 indicates that you're interested in 100% match only:

# CELL ********************

find_relationships(dirty_tables, verbose=2, name_similarity_threshold=1.0);

# MARKDOWN ********************

# Running at 100% similarity fails to account for small differences between names. In your example, the tables have a plural form with "s" suffix, which results in no exact match. This is handled very well with the default `name_similarity_threshold=0.8`. Notice that the Id for plural form `patients` is now compared to singular `patient` without adding too many other spurious comparisons to the execution time:

# CELL ********************

find_relationships(dirty_tables, verbose=2, name_similarity_threshold=0.8);

# MARKDOWN ********************

# Changing `name_similarity_threshold` to 0 is the other extreme, and it indicates that you want to compare all columns. This is rarely necessary and will result in increased execution time and spurious matches that will need to be reviewed. Observe the amount of comparisons in the verbose output:

# CELL ********************

find_relationships(dirty_tables, verbose=2, name_similarity_threshold=0);

# MARKDOWN ********************

# ### Summary of troubleshooting tips
# 
# 1. Start from exact match for "m:1" relationships (that is, the default `include_many_to_many=False` and `coverage_threshold=1.0`). This is usually what you want. 
# 2. Use a narrow focus on smaller subsets of tables.
# 3. Use validation to detect data quality issues.
# 4. Use `verbose=2` if you want to understand which columns are considered for relationship. This can result in a large amount of output.
# 5. Be aware of trade-offs of search arguments. `include_many_to_many=True` and `coverage_threshold<1.0` may produce spurious relationships that may be harder to analyze and will need to be filtered.

# MARKDOWN ********************

# ## Detect relationships on the full _Synthea_ dataset

# MARKDOWN ********************

# The simple baseline example was a convenient learning and troubleshooting tool. In practice you may start from a semantic model such as the full _Synthea_ dataset, which has a lot more tables. Explore the full _synthea_ dataset as follows. 
# 
# First, read all files from the _synthea/csv_ directory:

# CELL ********************

all_tables = {
    "allergies": pd.read_csv('synthea/csv/allergies.csv'),
    "careplans": pd.read_csv('synthea/csv/careplans.csv'),
    "conditions": pd.read_csv('synthea/csv/conditions.csv'),
    "devices": pd.read_csv('synthea/csv/devices.csv'),
    "encounters": pd.read_csv('synthea/csv/encounters.csv'),
    "imaging_studies": pd.read_csv('synthea/csv/imaging_studies.csv'),
    "immunizations": pd.read_csv('synthea/csv/immunizations.csv'),
    "medications": pd.read_csv('synthea/csv/medications.csv'),
    "observations": pd.read_csv('synthea/csv/observations.csv'),
    "organizations": pd.read_csv('synthea/csv/organizations.csv'),
    "patients": pd.read_csv('synthea/csv/patients.csv'),
    "payer_transitions": pd.read_csv('synthea/csv/payer_transitions.csv'),
    "payers": pd.read_csv('synthea/csv/payers.csv'),
    "procedures": pd.read_csv('synthea/csv/procedures.csv'),
    "providers": pd.read_csv('synthea/csv/providers.csv'),
    "supplies": pd.read_csv('synthea/csv/supplies.csv'),
}

# MARKDOWN ********************

# Find relationships between the tables, using  SemPy's ``find_relationships`` function:

# CELL ********************

suggested_relationships = find_relationships(all_tables)
suggested_relationships

# MARKDOWN ********************

# Visualize relationships:

# CELL ********************

plot_relationship_metadata(suggested_relationships)

# MARKDOWN ********************

# Count how many new "m:m" relationships will be discovered with `include_many_to_many=True`. These relationships will be in addition to the previously shown "m:1" relationships; therefore, you'll have to filter on `multiplicity`:

# CELL ********************

suggested_relationships = find_relationships(all_tables, coverage_threshold=1.0, include_many_to_many=True) 
suggested_relationships[suggested_relationships['Multiplicity']=='m:m']

# MARKDOWN ********************

# You can sort the relationship data by various columns to gain a deeper understanding of their nature. For example, you could choose to order the output by `Row Count From` and `Row Count To`, which will help identify the largest tables. In a different semantic model, maybe it would be important to focus on number of nulls `Null Count From` or `Coverage To`.
# 
# This analysis can help you to understand if any of the relationships could be invalid, and if you need to remove them from the list of candidates.

# CELL ********************

suggested_relationships.sort_values(['Row Count From', 'Row Count To'], ascending=False)

# MARKDOWN ********************

# ## Related content
# 
# Check out other tutorials for semantic link / SemPy:
# 1. [Clean data with functional dependencies](https://github.com/microsoft/fabric-samples/blob/main/docs-samples/data-science/semantic-link-samples/data_cleaning_functional_dependencies_tutorial.ipynb)
# 1. [Discover relationships in a semantic model using semantic link](https://github.com/microsoft/fabric-samples/blob/main/docs-samples/data-science/semantic-link-samples/powerbi_relationships_tutorial.ipynb)
# 1. [Analyze functional dependencies in a sample semantic model](https://github.com/microsoft/fabric-samples/blob/main/docs-samples/data-science/semantic-link-samples/powerbi_dependencies_tutorial.ipynb)
# 1. [Extract and calculate Power BI measures from a Jupyter notebook](https://github.com/microsoft/fabric-samples/blob/main/docs-samples/data-science/semantic-link-samples/powerbi_measures_tutorial.ipynb)

# MARKDOWN ********************

