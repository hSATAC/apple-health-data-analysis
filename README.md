# Apple Health Data Analysis

A comprehensive Python toolkit for analyzing Apple Health export data, providing insights into various health metrics including heart rate, sleep patterns, activity levels, and more.

## Features

- **Resting Heart Rate Analysis** - Track trends and patterns in your resting heart rate
- **Heart Rate Variability (HRV)** - Monitor stress and recovery through HRV metrics
- **Sleep Pattern Analysis** - Understand your sleep duration and quality over time
- **Oxygen Saturation Tracking** - Monitor SpO2 levels and identify potential issues
- **Activity Metrics** - Analyze daily steps, calories burned, and exercise patterns
- **Blood Pressure Monitoring** - Track systolic/diastolic trends and identify hypertension risks
- **Comprehensive Health Dashboard** - Generate combined visualizations of all health metrics

## Prerequisites

- Python 3.7+
- Apple Health data export (XML format)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/apple-health-data-analysis.git
cd apple-health-data-analysis
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Getting Your Apple Health Data

1. Open the Health app on your iPhone
2. Tap your profile picture in the top right
3. Scroll down and tap "Export All Health Data"
4. Choose "Export" and save the ZIP file
5. Extract the ZIP file - you'll need the `export.xml` file
6. Rename it to `apple_health_export.xml` (or update the filename in scripts)

## Usage

### Quick Start

Analyze all health metrics at once:
```bash
python example_usage.py --input apple_health_export.xml --analysis all
```

### Individual Analyses

Run specific analyses:
```bash
# Sleep analysis
python analyze_sleep_patterns.py

# Heart rate variability
python analyze_hrv.py

# Oxygen saturation
python analyze_oxygen_saturation.py

# Activity and energy
python analyze_activity_energy.py

# Blood pressure
python analyze_blood_pressure.py
```

### Extract Key Statistics

For a quick overview of all your health data:
```bash
python extract_key_statistics.py
```

### Generate Comprehensive Dashboard

Create a combined visualization of all metrics:
```bash
python create_combined_dashboard.py
```

## Configuration

Edit `config.py` to customize:
- Default file paths
- Health metric thresholds
- Chart appearance settings
- Date ranges for analysis

## Output Files

All scripts generate:
- **PNG charts** - High-resolution visualizations saved in the current directory
- **Console output** - Statistical summaries and insights
- **CSV exports** - Some scripts export processed data for further analysis

## Example Visualizations

The toolkit generates various charts including:
- Time series plots with moving averages
- Distribution histograms
- Correlation matrices
- Yearly/monthly aggregations
- Trend analysis with regression lines

## Privacy and Security

- **No data leaves your computer** - All analysis is performed locally
- **Add `.gitignore`** - The included `.gitignore` file prevents accidental upload of personal health data
- **Review before sharing** - Always check generated images before sharing to ensure no sensitive information is visible

## Project Structure

```
apple-health-data-analysis/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── config.py                         # Configuration settings
├── example_usage.py                  # Example script with CLI interface
├── .gitignore                        # Prevents uploading personal data
│
├── analyze_health_data_types.py      # Discover available data types
├── extract_key_statistics.py         # Quick statistical overview
│
├── analyze_sleep_patterns.py         # Sleep analysis
├── analyze_oxygen_saturation.py      # Blood oxygen analysis
├── analyze_hrv.py                    # Heart rate variability
├── analyze_blood_pressure.py         # Blood pressure tracking
├── analyze_activity_energy.py        # Activity and calorie analysis
├── analyze_resting_heart_rate.py     # Resting heart rate trends
│
└── create_combined_dashboard.py      # Generate comprehensive dashboard
```

## Interpreting Results

### Heart Rate
- **Normal resting HR**: 60-100 BPM (lower is generally better)
- **Athletes**: May have resting HR as low as 40-60 BPM

### Heart Rate Variability (HRV)
- **Higher HRV**: Generally indicates better stress resilience
- **Normal range**: 20-100ms (varies by age and fitness)

### Oxygen Saturation
- **Normal**: 95-100%
- **Concerning**: Below 95% (consult healthcare provider)

### Sleep
- **Recommended**: 7-9 hours per night for adults
- **Quality matters**: Consistency is as important as duration

### Activity
- **Steps target**: 8,000-10,000 steps per day
- **Active calories**: Aim for 500+ kcal from activity daily

## Troubleshooting

### Large XML Files
If processing times out due to large files:
1. Use `extract_key_statistics.py` for a sampled analysis
2. Modify scripts to process specific date ranges
3. Increase the sampling rate in configuration

### Missing Data Types
Not all analyses will work if you haven't been tracking certain metrics. The scripts will indicate if data is missing.

### Memory Issues
For very large exports (>1GB), consider:
- Running analyses one at a time
- Using a computer with more RAM
- Modifying scripts to process data in chunks

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for informational purposes only and should not be used as a substitute for professional medical advice. Always consult with healthcare providers for medical decisions.

## Acknowledgments

- Built with Python, pandas, and matplotlib
- Inspired by the quantified self movement
- Thanks to Apple for making health data exportable