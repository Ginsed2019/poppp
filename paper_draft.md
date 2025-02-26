1. Introduction (Literature review)

Short intro about why grided pop maps are good (Allows to have high rez data, for vide range of time, when census data is collected only once/twice a decade and in some areas not at all)
Talk about most popular models, their strengths and weakness (Are accurate and global, but has complicated pipeline and depends on derived data sets (this disallows to just "plug in" satiate data and get results))
Shortly talk about U-Nets and CNNs 

1.1. Benefits of gridded population maps
1.2. Existing gridded population maps
1.3. Use of U-Nets and CNNs in gridded population maps

2. Methodology

Write about data sources, collection and preprocessing, how i aggregate census data, covert it to raster image via gee transform to EPSG:3346 etc. etc.
Then write about what models i will use (CNN and U-Net)
Then how do i check the accuracy of my results - how i will compare my results with other models (Try finding default comparison metric for grided pop maps (as of now every article uses something different :( )))
This should be sufficient for methodology. Add pipeline image
Also loss functions ...

2.1. Data collection and sources
2.2. Population census aggregation
2.3. Data transformations and preprocessing
2.4. Train test split
2.5. Loss functions and Use of U-Nets and CNNs
2.6. Comparison methodology

3. Experiments

describe different CNN, U-Net configurations i tired what was the output of these experiments

3.1. CNN configurations and results
3.2. U-Net configurations and results

4. Results

How my best model compares with other models gpw4, world pop (most popular easily available models)

5. Conclusion

Talk about how my model is better then compared, also talk about possibility of bias because of selected metric for comparing (because of no standard), because i only trained and tested on lt cities
That gpwv4 and world pop are more generic and my model could been better only for post ussr states because of similar architecture style
So further research is needed for better comparison, better models and for seeing how architecture and historical contexts impact models.