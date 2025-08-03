import xml.etree.ElementTree as ET
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
import seaborn as sns

# Set style and font for Chinese characters
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Heiti TC', 'PingFang HK']
plt.rcParams['axes.unicode_minus'] = False
sns.set_style("whitegrid")

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
    print("Usage: python create_heart_rate_chart.py [path_to_export.xml]")
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

# Create figure with subplots
fig = plt.figure(figsize=(16, 10))
gs = fig.add_gridspec(3, 2, height_ratios=[2, 1, 1], width_ratios=[3, 1], hspace=0.3, wspace=0.2)

# Main trend plot
ax1 = fig.add_subplot(gs[0, :])
ax1.scatter(df_daily['date'], df_daily['value'], alpha=0.4, s=20, color='#FF6B6B', label='每日靜止心率')

# Add rolling averages
df_daily['rolling_7'] = df_daily['value'].rolling(window=7, center=True).mean()
df_daily['rolling_30'] = df_daily['value'].rolling(window=30, center=True).mean()
ax1.plot(df_daily['date'], df_daily['rolling_7'], color='#4ECDC4', linewidth=2, label='7天移動平均', alpha=0.8)
ax1.plot(df_daily['date'], df_daily['rolling_30'], color='#45B7D1', linewidth=3, label='30天移動平均')

# Add reference lines
ax1.axhline(y=60, color='gray', linestyle=':', alpha=0.5, label='正常範圍 (60-100 bpm)')
ax1.axhline(y=100, color='gray', linestyle=':', alpha=0.5)
ax1.fill_between(df_daily['date'], 60, 100, alpha=0.1, color='green')

# Formatting
ax1.set_title('靜止心率長期趨勢分析', fontsize=20, fontweight='bold', pad=20)
ax1.set_xlabel('日期', fontsize=14)
ax1.set_ylabel('靜止心率 (bpm)', fontsize=14)
ax1.legend(loc='upper right', fontsize=11, framealpha=0.9)
ax1.grid(True, alpha=0.3)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)

# Yearly comparison
ax2 = fig.add_subplot(gs[1, 0])
yearly_data = []
df_daily['year'] = df_daily['date'].dt.year
for year in sorted(df_daily['year'].unique()):
    year_data = df_daily[df_daily['year'] == year]['value'].values
    yearly_data.append(year_data)

bp = ax2.boxplot(yearly_data, tick_labels=sorted(df_daily['year'].unique()), 
                 patch_artist=True, showmeans=True, meanline=True)

# Color the boxes
colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(bp['boxes'])))
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

ax2.set_title('年度靜止心率分布比較', fontsize=16, fontweight='bold')
ax2.set_xlabel('年份', fontsize=12)
ax2.set_ylabel('靜止心率 (bpm)', fontsize=12)
ax2.grid(True, alpha=0.3, axis='y')

# Distribution histogram
ax3 = fig.add_subplot(gs[1, 1])
n, bins, patches = ax3.hist(df_daily['value'], bins=25, color='#FF6B6B', alpha=0.7, edgecolor='black')

# Color gradient for histogram
cm = plt.cm.RdYlGn_r
bin_centers = 0.5 * (bins[:-1] + bins[1:])
col = bin_centers - min(bin_centers)
col /= max(col)
for c, p in zip(col, patches):
    plt.setp(p, 'facecolor', cm(c))

ax3.axvline(df_daily['value'].mean(), color='blue', linestyle='--', linewidth=2, 
            label=f'平均值: {df_daily["value"].mean():.1f}')
ax3.axvline(df_daily['value'].median(), color='green', linestyle='--', linewidth=2, 
            label=f'中位數: {df_daily["value"].median():.0f}')
ax3.set_title('心率值分布', fontsize=16, fontweight='bold')
ax3.set_xlabel('靜止心率 (bpm)', fontsize=12)
ax3.set_ylabel('頻率', fontsize=12)
ax3.legend(fontsize=10)
ax3.grid(True, alpha=0.3, axis='y')

# Monthly heatmap for recent years
ax4 = fig.add_subplot(gs[2, :])
recent_df = df_daily[df_daily['date'] >= pd.Timestamp('2023-01-01', tz=df_daily['date'].iloc[0].tzinfo)].copy()
recent_df.loc[:, 'year'] = recent_df['date'].dt.year
recent_df.loc[:, 'month'] = recent_df['date'].dt.month

# Create pivot table for heatmap
heatmap_data = recent_df.pivot_table(values='value', index='month', columns='year', aggfunc='mean')

# Create custom colormap
cmap = sns.diverging_palette(10, 220, as_cmap=True)
sns.heatmap(heatmap_data, annot=True, fmt='.0f', cmap=cmap, center=80, 
            cbar_kws={'label': '平均靜止心率 (bpm)'}, ax=ax4,
            vmin=70, vmax=90)

ax4.set_title('近期月度平均心率熱力圖', fontsize=16, fontweight='bold')
ax4.set_xlabel('年份', fontsize=12)
ax4.set_ylabel('月份', fontsize=12)

# Get actual month labels from the data
month_labels = []
for month in heatmap_data.index:
    month_labels.append(f'{month}月')
ax4.set_yticklabels(month_labels, rotation=0)

# Add summary statistics
stats_text = f"""
統計摘要:
• 平均心率: {df_daily['value'].mean():.1f} bpm
• 最低心率: {df_daily['value'].min()} bpm
• 最高心率: {df_daily['value'].max()} bpm
• 標準差: {df_daily['value'].std():.1f} bpm
• 總記錄數: {len(df_daily)} 天
"""

plt.figtext(0.02, 0.02, stats_text, fontsize=11, 
            bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))

# Overall title
fig.suptitle('個人靜止心率健康追蹤報告', fontsize=24, fontweight='bold', y=0.98)

# Save the figure
plt.tight_layout()
# Save to current directory instead of hardcoded path
output_file = 'heart_rate_analysis_chart.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
plt.show()

print(f"圖表已保存至: {os.path.abspath(output_file)}")