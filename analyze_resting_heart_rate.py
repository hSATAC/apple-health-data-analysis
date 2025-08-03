import xml.etree.ElementTree as ET
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np

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
    print("Usage: python analyze_resting_heart_rate.py [path_to_export.xml]")
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

# Create DataFrame
df = pd.DataFrame(resting_hr_data)
df = df.sort_values('date')

# Remove duplicates by keeping the average for same date
df['date_only'] = df['date'].dt.date
df_daily = df.groupby('date_only').agg({
    'value': 'mean',
    'date': 'first'
}).reset_index(drop=True)

# Calculate statistics
print("=== 靜止心率分析報告 ===\n")
print(f"資料期間: {df_daily['date'].min().strftime('%Y-%m-%d')} 至 {df_daily['date'].max().strftime('%Y-%m-%d')}")
print(f"總記錄數: {len(df_daily)} 筆")
print(f"\n基本統計:")
print(f"平均靜止心率: {df_daily['value'].mean():.1f} bpm")
print(f"最高靜止心率: {df_daily['value'].max()} bpm (日期: {df_daily.loc[df_daily['value'].idxmax(), 'date'].strftime('%Y-%m-%d')})")
print(f"最低靜止心率: {df_daily['value'].min()} bpm (日期: {df_daily.loc[df_daily['value'].idxmin(), 'date'].strftime('%Y-%m-%d')})")
print(f"標準差: {df_daily['value'].std():.1f} bpm")

# Yearly analysis
df_daily['year'] = df_daily['date'].dt.year
yearly_stats = df_daily.groupby('year')['value'].agg(['mean', 'min', 'max', 'count'])
print(f"\n年度統計:")
for year, row in yearly_stats.iterrows():
    print(f"{year}年 - 平均: {row['mean']:.1f} bpm, 最低: {row['min']} bpm, 最高: {row['max']} bpm (記錄數: {row['count']})")

# Create visualization
plt.figure(figsize=(14, 8))
plt.style.use('seaborn-v0_8-darkgrid')

# Main plot
ax = plt.subplot(2, 1, 1)
plt.scatter(df_daily['date'], df_daily['value'], alpha=0.6, s=30, color='darkred', label='每日靜止心率')

# Add rolling average
if len(df_daily) > 30:
    df_daily['rolling_avg'] = df_daily['value'].rolling(window=30, center=True).mean()
    plt.plot(df_daily['date'], df_daily['rolling_avg'], color='blue', linewidth=2, label='30天移動平均')

# Add yearly average lines
for year in df_daily['year'].unique():
    year_data = df_daily[df_daily['year'] == year]
    if len(year_data) > 0:
        plt.axhline(y=year_data['value'].mean(), 
                   xmin=(year_data['date'].min() - df_daily['date'].min()).days / (df_daily['date'].max() - df_daily['date'].min()).days,
                   xmax=(year_data['date'].max() - df_daily['date'].min()).days / (df_daily['date'].max() - df_daily['date'].min()).days,
                   color='green', linestyle='--', alpha=0.5, linewidth=1)
        
        # Add year label
        mid_date = year_data['date'].min() + (year_data['date'].max() - year_data['date'].min()) / 2
        plt.text(mid_date, year_data['value'].mean() + 1, f'{year}年平均', 
                horizontalalignment='center', fontsize=9, color='green')

plt.title('靜止心率趨勢圖', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('日期', fontsize=12)
plt.ylabel('靜止心率 (bpm)', fontsize=12)
plt.legend(loc='upper right', fontsize=10)
plt.grid(True, alpha=0.3)

# Format x-axis
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
plt.xticks(rotation=45)

# Add reference lines
plt.axhline(y=60, color='gray', linestyle=':', alpha=0.5, label='正常範圍下限')
plt.axhline(y=100, color='gray', linestyle=':', alpha=0.5, label='正常範圍上限')

# Histogram subplot
plt.subplot(2, 1, 2)
plt.hist(df_daily['value'], bins=20, color='darkred', alpha=0.7, edgecolor='black')
plt.title('靜止心率分布圖', fontsize=14, fontweight='bold')
plt.xlabel('靜止心率 (bpm)', fontsize=12)
plt.ylabel('頻率', fontsize=12)
plt.grid(True, alpha=0.3, axis='y')

# Add vertical lines for mean and median
plt.axvline(df_daily['value'].mean(), color='blue', linestyle='--', linewidth=2, label=f'平均值: {df_daily["value"].mean():.1f}')
plt.axvline(df_daily['value'].median(), color='green', linestyle='--', linewidth=2, label=f'中位數: {df_daily["value"].median():.1f}')
plt.legend()

plt.tight_layout()
# Save to current directory instead of hardcoded path
output_file = 'resting_heart_rate_analysis.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"\nChart saved to: {os.path.abspath(output_file)}")
plt.show()

# Insights
print("\n=== 健康洞察 ===")

# Trend analysis
recent_data = df_daily[df_daily['date'] >= pd.Timestamp('2023-01-01', tz=df_daily['date'].iloc[0].tzinfo)]
older_data = df_daily[df_daily['date'] < pd.Timestamp('2023-01-01', tz=df_daily['date'].iloc[0].tzinfo)]

if len(recent_data) > 0 and len(older_data) > 0:
    recent_avg = recent_data['value'].mean()
    older_avg = older_data['value'].mean()
    change = ((recent_avg - older_avg) / older_avg) * 100
    
    if abs(change) > 5:
        trend = "上升" if change > 0 else "下降"
        print(f"\n1. 趨勢分析: 您的靜止心率近期呈現{trend}趨勢 ({change:+.1f}%)")
    else:
        print(f"\n1. 趨勢分析: 您的靜止心率保持穩定")

# Health assessment
avg_hr = df_daily['value'].mean()
if avg_hr < 60:
    print(f"2. 健康評估: 您的平均靜止心率 ({avg_hr:.1f} bpm) 較低，這通常表示良好的心血管健康狀態")
elif avg_hr <= 100:
    print(f"2. 健康評估: 您的平均靜止心率 ({avg_hr:.1f} bpm) 在正常範圍內 (60-100 bpm)")
else:
    print(f"2. 健康評估: 您的平均靜止心率 ({avg_hr:.1f} bpm) 偏高，建議諮詢醫師")

# Variability
std_hr = df_daily['value'].std()
if std_hr > 15:
    print(f"3. 變異性: 您的靜止心率變異較大 (標準差: {std_hr:.1f})，可能受到壓力、睡眠或生活習慣影響")
else:
    print(f"3. 變異性: 您的靜止心率相對穩定 (標準差: {std_hr:.1f})，顯示良好的生理調節")

# Extreme values
high_hr_days = len(df_daily[df_daily['value'] > 100])
low_hr_days = len(df_daily[df_daily['value'] < 60])
if high_hr_days > 0:
    print(f"4. 異常值: 有 {high_hr_days} 天記錄超過 100 bpm，可能與壓力、疾病或藥物有關")
if low_hr_days > 0:
    print(f"5. 低心率: 有 {low_hr_days} 天記錄低於 60 bpm，如果您不是運動員，建議注意是否有其他症狀")

print("\n建議: 定期監測靜止心率有助於了解整體健康狀況。如有持續異常，請諮詢醫療專業人員。")