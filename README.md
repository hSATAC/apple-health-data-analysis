# Apple Health Data Analysis

Scripts to analyze Apple Health exported data, focusing on resting heart rate trends and visualizations.

## Usage

All scripts accept an optional command line argument for the input XML file:

```bash
python analyze_hr_basic.py [path_to_export.xml]
python analyze_resting_heart_rate.py [path_to_export.xml]
python create_heart_rate_chart.py [path_to_export.xml]
# etc.
```

If no argument is provided, scripts will look for `export.xml` in the current directory.

## Output

- Charts are saved as PNG files in the current directory
- CSV data exports are saved in the current directory

## Requirements

- Python 3.x
- pandas
- matplotlib
- numpy
- seaborn (for some visualizations)
