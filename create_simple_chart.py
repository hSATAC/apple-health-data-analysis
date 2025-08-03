import xml.etree.ElementTree as ET
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'DejaVu Sans'

# Parse XML file
import sys
import os

# Get input file from command line argument or use default
if len(sys.argv) > 1:
    input_file = sys.argv[1]
else:
    input_file = 'export.xml'  # Default filename in current directory

if not os.path.exists(input_file):
    print(f"Error: Input file '{input_file}' not found.")
    print("Usage: python create_simple_chart.py [path_to_export.xml]")
    sys.exit(1)

tree = ET.parse(input_file)
root = tree.getroot()

# Extract resting heart rate records
resting_hr_data = []
for record in root.findall('Record'):
    if record.get('type') == 'HKQuantityTypeIdentifierRestingHeartRate':
        resting_hr_data.append({
            'date': datetime.strptime(record.get('startDate'), '%Y-%m-%d %H:%M:%S %z'),
            'value': int(record.get('value')),
            'source': record.get('sourceName')
        })

# Create DataFrame and process data
df = pd.DataFrame(resting_hr_data)
df = df.sort_values('date')
df['date_only'] = df['date'].dt.date
df_daily = df.groupby('date_only').agg({
    'value': 'mean',
    'date': 'first'
}).reset_index(drop=True)

# Create figure
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), height_ratios=[2, 1])

# Main trend plot
ax1.scatter(df_daily['date'], df_daily['value'], alpha=0.4, s=30, color='red', label='Daily Resting Heart Rate')

# Add rolling averages
df_daily['rolling_7'] = df_daily['value'].rolling(window=7, center=True).mean()
df_daily['rolling_30'] = df_daily['value'].rolling(window=30, center=True).mean()
ax1.plot(df_daily['date'], df_daily['rolling_7'], color='orange', linewidth=2, label='7-day Moving Average', alpha=0.8)
ax1.plot(df_daily['date'], df_daily['rolling_30'], color='blue', linewidth=3, label='30-day Moving Average')

# Add reference lines
ax1.axhline(y=60, color='gray', linestyle=':', alpha=0.5, label='Normal Range (60-100 bpm)')
ax1.axhline(y=100, color='gray', linestyle=':', alpha=0.5)
ax1.fill_between(df_daily['date'], 60, 100, alpha=0.1, color='green')

# Yearly averages
df_daily['year'] = df_daily['date'].dt.year
for year in df_daily['year'].unique():
    year_data = df_daily[df_daily['year'] == year]
    if len(year_data) > 0:
        year_avg = year_data['value'].mean()
        ax1.hlines(y=year_avg, xmin=year_data['date'].min(), xmax=year_data['date'].max(),
                  colors='green', linestyles='--', alpha=0.6, linewidth=1.5)
        mid_date = year_data['date'].min() + (year_data['date'].max() - year_data['date'].min()) / 2
        ax1.text(mid_date, year_avg + 1, f'{year}: {year_avg:.1f}', 
                horizontalalignment='center', fontsize=9, color='green')

# Formatting
ax1.set_title('Resting Heart Rate Trend Analysis', fontsize=18, fontweight='bold', pad=20)
ax1.set_xlabel('Date', fontsize=12)
ax1.set_ylabel('Resting Heart Rate (bpm)', fontsize=12)
ax1.legend(loc='upper right', fontsize=10, framealpha=0.9)
ax1.grid(True, alpha=0.3)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)

# Yearly boxplot
yearly_data = []
years = sorted(df_daily['year'].unique())
for year in years:
    year_data = df_daily[df_daily['year'] == year]['value'].values
    yearly_data.append(year_data)

bp = ax2.boxplot(yearly_data, tick_labels=years, patch_artist=True, showmeans=True)

# Color the boxes with gradient
colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(bp['boxes'])))
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

ax2.set_title('Yearly Distribution Comparison', fontsize=14, fontweight='bold')
ax2.set_xlabel('Year', fontsize=12)
ax2.set_ylabel('Resting Heart Rate (bpm)', fontsize=12)
ax2.grid(True, alpha=0.3, axis='y')

# Add summary statistics
stats_text = f"""Summary Statistics:
• Average HR: {df_daily['value'].mean():.1f} bpm
• Lowest HR: {df_daily['value'].min()} bpm  
• Highest HR: {df_daily['value'].max()} bpm
• Std Dev: {df_daily['value'].std():.1f} bpm
• Total Days: {len(df_daily)}
"""

# Add text box
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
ax1.text(0.02, 0.95, stats_text, transform=ax1.transAxes, fontsize=10,
         verticalalignment='top', bbox=props)

# Overall title
fig.suptitle('Personal Resting Heart Rate Analysis', fontsize=20, fontweight='bold')

# Save without showing
plt.tight_layout()
# Save to current directory instead of hardcoded path
output_file = 'heart_rate_chart.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
plt.close()

print(f"Chart saved to: {os.path.abspath(output_file)}")