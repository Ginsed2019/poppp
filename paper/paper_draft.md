1. Introduction (Literature review)

Short intro about why grided pop maps are good (Allows to have high rez data, for vide range of time, when census data is collected only once/twice a decade and in some areas not at all)
Talk about most popular models, their strengths and weakness (Are accurate and global, but has complicated pipeline and depends on derived data sets (this disallows to just "plug in" satiate data and get results))
Shortly talk about U-Nets and CNNs 

1.1. Benefits of gridded population maps
1.2. Existing gridded population maps
1.3. Use of U-Nets and CNNs in gridded population maps

## 2. Methodology

This chapter outlines the methodology used in creation of girded population map model. A quick summary of the methodology is shown in Image 1. More detailed explanation of methodology is described in the following chapters.

![](./images/pipeline_export.svg)

*Image 1: Illustration of methodology. This image shows the sources and flow of data used in this paper. First census data is taken from state data agency, then it's aggregated into a single data set, then it's uploaded to GEE, after this features and labels are retrieved from GEE passed to ML model and finally predictions are made.*

### 2.1. Data collection and sources

The data used in this paper for creating and comparing gridded population maps (GPMs) is summarized in Table 1.

| Definition | Purpose | Resolution | Source | Original source | Date of access |
|------------|---------|------------|--------|-----------------|----------------|
| 2021 Population Census of Lithuania. A 1km grid for the entire country and 500m, 250m, 100m grids for larger towns | Label used for creating ML models | from 100m to 1km | State Data Agency of Lithuania | State Data Agency of Lithuania | 2024-10-06 |
| Sentinel-1 radar data. VV and VH bands for year 2021 (from 2021-01-01 to 2022-01-01) | Feature used for creating ML models | 10m | Google earth engine | Copernicus mission | 2024-10-06 |
| Sentinel-2 multispectral data. 12 different bands ranging from 443.9nm to 2185.7nm for the summer of year 2021 (from 2021-05-01 to 2021-09-01) | Feature used for creating ML models | from 10m to 60m | Google earth engine | Copernicus mission | 2024-10-06 |
| Night light data from VIIRS satellite. Average radiance band for January of year 2021 | Feature used for creating ML models | 464m | Google earth engine | NASA/NOAA | 2024-10-06 |
| WorldPop GPM for year 2021 | GPM compared with our models | 93m | Google earth engine | WorldPop research group | 2025-03-06 |
| Global Human Settlement Layer GPM for year 2021 | GPM compared with our models | 100m | Google earth engine | Global Human Settlement Layer project | 2025-03-06 |

*Table 1: Summary of data used. This table describes what data is used (Definition), what it is used for (Purpose), the resolution data is available in (Resolution), source from where data was taken (Source), who is the owner of the data (Original source) and date when the data was accessed (Date of access).*

The population census data of Lithuania with various resolutions was aggregated and integrated with Google earth engine for more consistent and stable workflow.

### 2.2. Population census aggregation

As mentioned in the previous section the population census data of Lithuania was aggregated together to have a single census GPM of mixed resolutions.
Population census data was available as set of polygons and population living in each polygon, so the aggregation process was designed accordingly.

The aggregation process was as follows:
1. 100m polygons where subtracted (both area and population) from 250m polygons, creating differential polygons of data missing from 100m polygons.
2. Differential polygons and 100m polygons where combined to create more complete dataset.
3. This process was repeated with 500m and 1km resolution data to create a full dataset of best available resolution.

The final result is a single GPM with mixed resolutions ranging from 100m to 1000m, preserving the highest resolution data where available.

After aggregation dataset was integrated with Google earth engine. Via Google earth engine dataset was transformed to raster data.

### 2.3. Data transformations and preprocessing

.................
Each data set mentioned in Table 1 where preprocessed similarly:
1. At first data was filtered by date ranges we are interested. (Shown in Table 1 definition column)
2. Then for Sentinel-2 and Night light data we removed cloudy pixels.
3. After that we calculated mean of all available images over filtered date ranges for each data set.
4. To ensure consistency between all data sets we reprojected each of them to EPSG:3346 (Projected coordinate system for Lithuania).
5. Finally we saved the resulting data sets (their bands) as bitmaps of areas 500m x 500m at 10m for ~100 towns where highest census resolution where available.

After getting the bitmaps, we additionally removed outlier pixels from the data sets by setting extreme values to the minimum or maximum thresholds.
Then we standardized each data set. Its also worth mentioning that we also tried log transform before standardizing on population and night light data, because the following data sets had log distributions.

### 2.4. Train test split

After preparing our data we splitted it to train and test sets, for model training and evaluation. The data was split spatially to ensure independent training and testing areas. Region between latitudes 23.4664
and 24.2794 were designated as the test set, while all other area was training set.
* Training Set: Included 86 cities, such as Vilnius, the largest city in Lithuania.
* Testing Set: Included 22 cities, such as Kaunas, the second-largest city.

### 2.5. Loss functions and Use of U-Nets and CNNs

For training we tried MSE loss function and some custom loss functions derived from it. For calculating MSE loss we simply took the difference of census population and predicted population bitmaps.
For custom loss function we grouped census population pixels based on population ranges and calculated MSE values for each range, then took a mean of these MSE
Add use of U-Nets and CNNs


### 2.6. Comparison methodology

For evaluating created models and comparing them with existing models MAE and MAPE metric will be used at different population ranges. Different population ranges are used because population data has logarithmic distribution, for example in population range from 1 to 5, MAE of 50 would be quite large (prediction was 55 when actual value was 5), but in range from 100 to 500, MAE of 50 is negligible (prediction was 550 when actual value was 500), similar logic can be applied to MAPE. In range from 100 to 500 MAPE of 200% would be quite large (prediction was 1000 when actual value was 500), but in range 1 to 5 MAE of 200% would be negligible (prediction was 10 when actual value was 5).
As a result of this logic MAE is useful for evaluating low population and MAPE for evaluating high population.

## 3. Experiments

describe different CNN, U-Net configurations i tired what was the output of these experiments

3.1. CNN configurations and results
3.2. U-Net configurations and results

4. Results

How my best model compares with other models gpw4, world pop (most popular easily available models)

5. Conclusion

Talk about how my model is better then compared, also talk about possibility of bias because of selected metric for comparing (because of no standard), because i only trained and tested on lt cities
That gpwv4 and world pop are more generic and my model could been better only for post ussr states because of similar architecture style
So further research is needed for better comparison, better models and for seeing how architecture and historical contexts impact models.