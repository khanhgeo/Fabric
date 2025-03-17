# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# MARKDOWN ********************

# # Tutorial: Use Great Expectations (GX) to validate Power BI semantic models

# MARKDOWN ********************

# This tutorial illustrates how to use SemPy together with [Great Expectations](https://greatexpectations.io/) (GX) to perform data validation on Power BI semantic models.
# 
# In this tutorial, you learn how to:
# 
# - Validate constraints on a dataset in your Fabric workspace with Great Expectation's Fabric Data Source (built on semantic link).
#     - Configure a GX Data Context, Data Assets, and Expectations.
#     - View validation results with a GX Checkpoint. 
# - Use semantic link to analyze raw data.

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
# * Add a lakehouse to the notebook.


# MARKDOWN ********************

# ## Set up the notebook
# 
# In this section, you set up a notebook environment with the necessary modules and data.
# 
# 1. Install `SemPy` and the relevant `Great Expectations` libraries from PyPI using the `%pip` in-line installation capability within the notebook.

# CELL ********************

# install libraries
%pip install semantic-link 'great-expectations<1.0' great_expectations_experimental great_expectations_zipcode_expectations
%pip installpip install --upgrade uszipcode sqlalchemy_mate

# load %%dax cell magic
%load_ext sempy

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# 2. Perform necessary imports of modules that you'll need later: 

# CELL ********************

import great_expectations as gx
from great_expectations.expectations.expectation import ExpectationConfiguration
#from great_expectations_zipcode_expectations.expectations import expect_column_values_to_be_valid_zip5

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Set up GX Data Context and Data Source
# 
# In order to get started with Great Expectations, you first have to set up a GX [Data Context](https://docs.greatexpectations.io/docs/reference/learn/terms/data_context/). The context serves as an entry point for GX operations and holds all relevant configurations.

# CELL ********************

context = gx.get_context()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# You can now add your Fabric dataset to this context as a [Data Source](https://docs.greatexpectations.io/docs/reference/learn/terms/datasource) to start interacting with the data. This tutorial uses a standard Power BI sample semantic model [Retail Analysis Sample .pbix file](https://learn.microsoft.com/en-us/power-bi/create-reports/sample-retail-analysis).

# CELL ********************

ds = context.sources.add_fabric_powerbi("Retail Analysis Data Source", dataset="Retail Analysis Sample PBIX")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Specify Data Assets
# 
# Define [Data Assets](https://docs.greatexpectations.io/docs/reference/learn/terms/data_asset) to specify the subset of data you'd like to work with. The asset can be as simple as full tables, or be as complex as a custom Data Analysis Expressions (DAX) query.
# 
# Here, you'll add multiple assets:
# * Power BI table
# * Power BI measure
# * Custom DAX query
# * [Dynamic Management View](https://learn.microsoft.com/en-us/analysis-services/instances/use-dynamic-management-views-dmvs-to-monitor-analysis-services?view=asallproducts-allversions) (DMV) query


# MARKDOWN ********************

# ### Power BI table
# 
# Add a Power BI table as a data asset.

# CELL ********************

ds.add_powerbi_table_asset("Store Asset", table="Store")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### Power BI measure
# 
# If your dataset contains preconfigured measures, you add the measures as assets following a similar API to SemPy's `evaluate_measure`. 

# CELL ********************

ds.add_powerbi_measure_asset(
    "Total Units Asset",
    measure="TotalUnits",
    groupby_columns=["Time[FiscalYear]", "Time[FiscalMonth]"]
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### DAX
# If you'd like to define your own measures or have more control over specific rows, you can add a DAX asset with a custom DAX query. Here, we define a `Total Units Ratio` measure by dividing two existing measures.

# CELL ********************

ds.add_powerbi_dax_asset(
    "Total Units YoY Asset",
    dax_string=
    """
    EVALUATE SUMMARIZECOLUMNS(
        'Time'[FiscalYear],
        'Time'[FiscalMonth],
        "Total Units Ratio", DIVIDE([Total Units This Year], [Total Units Last Year])
    )    
    """
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### DMV query
# 
# In some cases, it might be helpful to use [Dynamic Management View](https://learn.microsoft.com/en-us/analysis-services/instances/use-dynamic-management-views-dmvs-to-monitor-analysis-services?view=asallproducts-allversions) (DMV) calculations as part of the data validation process. For example, you can keep track of the number of referential integrity violations within your dataset. For more information, see "[Clean data = faster reports](https://dax.tips/2019/11/28/clean-data-faster-reports/)" 

# CELL ********************

ds.add_powerbi_dax_asset(
    "Referential Integrity Violation",
    dax_string=
    """
    SELECT
        [Database_name],
        [Dimension_Name],
        [RIVIOLATION_COUNT]
    FROM $SYSTEM.DISCOVER_STORAGE_TABLES
    """
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Expectations
# 
# In order to add specific constraints to the assets, you first have to configure [Expectation Suites](https://docs.greatexpectations.io/docs/reference/learn/terms/expectation_suite). After adding individual [Expectations](https://docs.greatexpectations.io/docs/reference/learn/terms/expectation) to each suite, you can then update the Data Context set up in the beginning with the new suite. For a full list of available expectations, see the [GX Expectation Gallery](https://greatexpectations.io/expectations/).
# 
# Start by adding a "Retail Store Suite" with two expectations:
# * a valid zip code
# * a table with row count between 80 and 200

# CELL ********************

suite_store = context.add_expectation_suite("Retail Store Suite")

#suite_store.add_expectation(ExpectationConfiguration("expect_column_values_to_be_valid_zip5", { "column": "PostalCode" }))
suite_store.add_expectation(ExpectationConfiguration("expect_table_row_count_to_be_between", { "min_value": 80, "max_value": 200 }))

context.add_or_update_expectation_suite(expectation_suite=suite_store)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from great_expectations.expectations.registry import list_registered_expectation_implementations
print(list_registered_expectation_implementations())


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ##### `TotalUnits` Measure

# MARKDOWN ********************

# Add a "Retail Measure Suite" with one expectation:
# 
# * Column values should be greater than 50,000

# CELL ********************

suite_measure = context.add_expectation_suite("Retail Measure Suite")
suite_measure.add_expectation(ExpectationConfiguration(
    "expect_column_values_to_be_between", 
    {
        "column": "TotalUnits",
        "min_value": 50000
    }
))

context.add_or_update_expectation_suite(expectation_suite=suite_measure)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### `Total Units Ratio` DAX
# 
# Add a "Retail DAX Suite" with one expectation:
# 
# * Column values for Total Units Ratio shoud be between 0.8 and 1.5

# CELL ********************

suite_dax = context.add_expectation_suite("Retail DAX Suite")
suite_dax.add_expectation(ExpectationConfiguration(
    "expect_column_values_to_be_between", 
    {
        "column": "[Total Units Ratio]",
        "min_value": 0.8,
        "max_value": 1.5
    }
))

context.add_or_update_expectation_suite(expectation_suite=suite_dax)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### Referential Integrity Violations (DMV)
# 
# Add a "Retail DMV Suite" with one expectation:
# 
# * the RIVIOLATION_COUNT should be 0

# CELL ********************

suite_dmv = context.add_expectation_suite("Retail DMV Suite")
# There should be no RI violations
suite_dmv.add_expectation(ExpectationConfiguration(
    "expect_column_values_to_be_in_set", 
    {
        "column": "RIVIOLATION_COUNT",
        "value_set": [0]
    }
))
context.add_or_update_expectation_suite(expectation_suite=suite_dmv)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Validation
# 
# To actually run the specified expectations against the data, first create a [Checkpoint](https://docs.greatexpectations.io/docs/reference/learn/terms/checkpoint) and add it to the context. For more information on Checkpoint configuration, see [Data Validation workflow](https://docs.greatexpectations.io/docs/reference/learn/guides/validation/validate_data_overview).

# CELL ********************

checkpoint_config = {
    "name": f"Retail Analysis Checkpoint",
    "validations": [
        {
            "expectation_suite_name": "Retail Store Suite",
            "batch_request": {
                "datasource_name": "Retail Analysis Data Source",
                "data_asset_name": "Store Asset",
            },
        },
        {
            "expectation_suite_name": "Retail Measure Suite",
            "batch_request": {
                "datasource_name": "Retail Analysis Data Source",
                "data_asset_name": "Total Units Asset",
            },
        },
        {
            "expectation_suite_name": "Retail DAX Suite",
            "batch_request": {
                "datasource_name": "Retail Analysis Data Source",
                "data_asset_name": "Total Units YoY Asset",
            },
        },
        {
            "expectation_suite_name": "Retail DMV Suite",
            "batch_request": {
                "datasource_name": "Retail Analysis Data Source",
                "data_asset_name": "Referential Integrity Violation",
            },
        },
    ],
}
checkpoint = context.add_checkpoint(
    **checkpoint_config
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# Now run the checkpoint and extract the results as a pandas DataFrame for simple formatting.

# CELL ********************

result = checkpoint.run()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# Process and print your results.

# CELL ********************

import pandas as pd

data = []

for run_result in result.run_results:
    for validation_result in result.run_results[run_result]["validation_result"]["results"]:
        row = {
            "Batch ID": run_result.batch_identifier,
            "type": validation_result.expectation_config.expectation_type,
            "success": validation_result.success
        }

        row.update(dict(validation_result.result))
        
        data.append(row)

result_df = pd.DataFrame.from_records(data)    

result_df[["Batch ID", "type", "success", "element_count", "unexpected_count", "partial_unexpected_list"]]

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# From these results you can see that all your expectations passed the validation, except for the "Total Units YoY Asset" that you defined through a custom DAX query. 

# MARKDOWN ********************

# ## Diagnostics
# 
# Using semantic link, you can fetch the source data to understand which exact years are out of range. Semantic link provides an inline magic for executing DAX queries. Use semantic link to execute the same query you passed into the GX Data Asset and visualize the resulting values.

# CELL ********************

# MAGIC %%dax "Retail Analysis Sample PBIX"
# MAGIC 
# MAGIC EVALUATE SUMMARIZECOLUMNS(
# MAGIC     'Time'[FiscalYear],
# MAGIC     'Time'[FiscalMonth],
# MAGIC     "Total Units Ratio", DIVIDE([Total Units This Year], [Total Units Last Year])
# MAGIC )

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# Save these results in a DataFrame.

# CELL ********************

df = _

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import matplotlib.pyplot as plt

df["Total Units % Change YoY"] = (df["[Total Units Ratio]"] - 1)

df.set_index(["Time[FiscalYear]", "Time[FiscalMonth]"]).plot.bar(y="Total Units % Change YoY")

plt.axhline(0)

plt.axhline(-0.2, color="red", linestyle="dotted")
plt.axhline( 0.5, color="red", linestyle="dotted")

None

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# From the plot, you can see that April and July were slightly out of range and can then take further steps to investigate.

# MARKDOWN ********************

# ## Storing GX Configuration
# 
# As the data in your dataset changes over time, you might want to rerun the GX validations you just performed. Currently, the Data Context (containing the connected Data Assets, Expectation Suites, and Checkpoint) lives ephemerally, but it can be converted to a File Context for future use. Alternatively, you can instantiate a File Context (see [Instantiate a Data Context](https://docs.greatexpectations.io/docs/reference/learn/guides/setup/configuring_data_contexts/instantiating_data_contexts/instantiate_data_context#specify-a-folder-containing-a-previously-initialized-filesystem-data-context)).

# CELL ********************

context = context.convert_to_file_context()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# Now that you saved the context, copy the `gx` directory to your lakehouse.
# 
# 
# > [!IMPORTANT]
# > **This cell assumes you  [added a lakehouse](https://aka.ms/fabric/addlakehouse) to the notebook.** If there is no lakehouse attached, you won't see an error, but you also won't later be able to get the context. If you add a lakehouse now, the kernel will restart, so you'll have to re-run the entire notebook to get back to this point.

# CELL ********************

# copy GX directory to attached lakehouse
!cp -r gx/ /lakehouse/default/Files/gx

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# Now, future contexts can be created with `context = gx.get_context(project_root_dir="<your path here>")` to use all the configurations from this tutorial.
# 
# For example, in a new notebook, attach the same lakehouse and use `context = gx.get_context(project_root_dir="/lakehouse/default/Files/gx")` to retrieve the context.
