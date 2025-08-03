"""
Configuration file for Apple Health Data Analysis
"""

# Default input file name
# Users should export their Apple Health data and rename it to this filename
# or modify this variable to match their export filename
DEFAULT_EXPORT_FILE = "apple_health_export.xml"

# Alternative: Accept filename from command line
# Example usage: python analyze_sleep_patterns.py --input my_health_data.xml

# Date range for analysis (set to None to analyze all data)
START_DATE = None  # Format: "YYYY-MM-DD" or None
END_DATE = None    # Format: "YYYY-MM-DD" or None

# Chart settings
CHART_DPI = 300
CHART_STYLE = 'seaborn'

# Analysis thresholds
RESTING_HR_NORMAL_MAX = 70
HRV_NORMAL_MIN = 30
OXYGEN_SATURATION_LOW_THRESHOLD = 95
SLEEP_HOURS_RECOMMENDED = 8
DAILY_STEPS_TARGET = 10000
DAILY_CALORIES_TARGET = 500

# Blood pressure thresholds
BP_SYSTOLIC_NORMAL_MAX = 120
BP_DIASTOLIC_NORMAL_MAX = 80
BP_SYSTOLIC_HIGH = 140
BP_DIASTOLIC_HIGH = 90