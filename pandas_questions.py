"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.DataFrame({})
    regions = pd.DataFrame({})
    departments = pd.DataFrame({})
    regions = pd.read_csv('data/regions.csv')
    departments = pd.read_csv('data/departments.csv')
    
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions = regions.rename(columns={"code": "code_reg", "name": "name_reg"})
    departments = departments.rename(columns={"region_code": "code_reg", "name": "name_dep", "code": "code_dep"})
    merged = pd.merge(departments, regions, on="code_reg", how="left")
    merged = merged[["code_reg", "name_reg", "code_dep", "name_dep"]]

    return merged



def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    valid_codes = regions_and_departments["code_dep"].unique()
    filtered_referendum = referendum[referendum["Department code"].isin(valid_codes)]

    merged = pd.merge(
        filtered_referendum,
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
        how="inner"
    )
    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

    referendum = referendum[~referendum["Department code"].str.startswith("Z")]
    referendum.loc[:, "Department code"] = referendum[
        "Department code"
    ].str.lstrip("0")
    regions_and_departments.loc[:, "code_dep"] = regions_and_departments[
        "code_dep"
    ].str.lstrip("0")
    merged = referendum.merge(
        regions_and_departments,
        how="inner",
        left_on="Department code",
        right_on="code_dep"
    )
    return merged


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_regions = gpd.read_file('data/regions.geojson')  #Load geographic data

    merged_df = geo_regions.merge(  #Merge referendum results with geographic data
        referendum_result_by_regions,
        left_on='code',
        right_index=True,
        how='left'
    )

    merged_df['ratio'] = (  #Calculate the ratio of Choice A votes
        merged_df['Choice A'] /
        (merged_df['Choice A'] + merged_df['Choice B'])
    )

    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    merged_df.plot(
        column='ratio',  #column to visualize
        cmap='Greens',  #color map
        legend=True,  #add a legend
        ax=ax,  #matplotlib axis
        edgecolor='black'  #outline color
    )
    plt.title("Rate of 'Choice A' over all expressed ballots")
    plt.axis('off')
    plt.show()

    return merged_df  #Return the updated GeoDataFrame




if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
