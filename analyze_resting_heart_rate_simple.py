import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from collections import defaultdict
import statistics

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
    print("Usage: python analyze_resting_heart_rate_simple.py [path_to_export.xml]")
    sys.exit(1)

tree = ET.parse(input_file)
root = tree.getroot()

# Extract resting heart rate records
resting_hr_data = []
for record in root.findall('Record'):
    if record.get('type') == 'HKQuantityTypeIdentifierRestingHeartRate':
        date = datetime.strptime(record.get('startDate'), '%Y-%m-%d %H:%M:%S %z')
        value = int(record.get('value'))
        resting_hr_data.append({
            'date': date,
            'value': value,
            'source': record.get('sourceName')
        })

# Sort by date
resting_hr_data.sort(key=lambda x: x['date'])

# Group by date and calculate daily average
daily_data = defaultdict(list)
for item in resting_hr_data:
    date_key = item['date'].date()
    daily_data[date_key].append(item['value'])

# Calculate daily averages
dates = []
values = []
for date, hr_values in sorted(daily_data.items()):
    dates.append(datetime.combine(date, datetime.min.time()))
    values.append(sum(hr_values) / len(hr_values))

# Calculate statistics
print("=== 靜止心率分析報告 ===\n")
print(f"資料期間: {min(dates).strftime('%Y-%m-%d')} 至 {max(dates).strftime('%Y-%m-%d')}")
print(f"總記錄數: {len(dates)} 筆")
print(f"\n基本統計:")
avg_hr = sum(values) / len(values)
min_hr = min(values)
max_hr = max(values)
min_idx = values.index(min_hr)
max_idx = values.index(max_hr)
std_hr = statistics.stdev(values) if len(values) > 1 else 0

print(f"平均靜止心率: {avg_hr:.1f} bpm")
print(f"最高靜止心率: {max_hr} bpm (日期: {dates[max_idx].strftime('%Y-%m-%d')})")
print(f"最低靜止心率: {min_hr} bpm (日期: {dates[min_idx].strftime('%Y-%m-%d')})")
print(f"標準差: {std_hr:.1f} bpm")

# Yearly analysis
yearly_data = defaultdict(list)
for date, value in zip(dates, values):
    yearly_data[date.year].append(value)

print(f"\n年度統計:")
for year in sorted(yearly_data.keys()):
    year_values = yearly_data[year]
    year_avg = sum(year_values) / len(year_values)
    year_min = min(year_values)
    year_max = max(year_values)
    print(f"{year}年 - 平均: {year_avg:.1f} bpm, 最低: {year_min} bpm, 最高: {year_max} bpm (記錄數: {len(year_values)})")

# Create visualization
plt.figure(figsize=(14, 8))
plt.style.use('seaborn-v0_8-darkgrid')

# Main plot
ax = plt.subplot(2, 1, 1)
plt.scatter(dates, values, alpha=0.6, s=30, color='darkred', label='每日靜止心率')

# Add rolling average (simple moving average)
if len(values) > 30:
    rolling_avg = []
    window = 30
    for i in range(len(values)):
        start = max(0, i - window // 2)
        end = min(len(values), i + window // 2 + 1)
        if end - start > 0:
            rolling_avg.append(sum(values[start:end]) / (end - start))
        else:
            rolling_avg.append(values[i])
    plt.plot(dates, rolling_avg, color='blue', linewidth=2, label='30天移動平均')

# Add yearly average lines
for year, year_values in yearly_data.items():
    year_dates = [d for d in dates if d.year == year]
    if year_dates:
        year_avg = sum(year_values) / len(year_values)
        plt.plot([min(year_dates), max(year_dates)], [year_avg, year_avg], 
                color='green', linestyle='--', alpha=0.5, linewidth=1)
        
        # Add year label
        mid_date = min(year_dates) + (max(year_dates) - min(year_dates)) / 2
        plt.text(mid_date, year_avg + 1, f'{year}年平均', 
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
plt.hist(values, bins=20, color='darkred', alpha=0.7, edgecolor='black')
plt.title('靜止心率分布圖', fontsize=14, fontweight='bold')
plt.xlabel('靜止心率 (bpm)', fontsize=12)
plt.ylabel('頻率', fontsize=12)
plt.grid(True, alpha=0.3, axis='y')

# Add vertical lines for mean and median
median_hr = sorted(values)[len(values)//2]
plt.axvline(avg_hr, color='blue', linestyle='--', linewidth=2, label=f'平均值: {avg_hr:.1f}')
plt.axvline(median_hr, color='green', linestyle='--', linewidth=2, label=f'中位數: {median_hr:.1f}')
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
recent_values = [v for d, v in zip(dates, values) if d.year >= 2023]
older_values = [v for d, v in zip(dates, values) if d.year < 2023]

if recent_values and older_values:
    recent_avg = sum(recent_values) / len(recent_values)
    older_avg = sum(older_values) / len(older_values)
    change = ((recent_avg - older_avg) / older_avg) * 100
    
    if abs(change) > 5:
        trend = "上升" if change > 0 else "下降"
        print(f"\n1. 趨勢分析: 您的靜止心率近期呈現{trend}趨勢 ({change:+.1f}%)")
    else:
        print(f"\n1. 趨勢分析: 您的靜止心率保持穩定")
else:
    print(f"\n1. 趨勢分析: 資料不足以進行趨勢分析")

# Health assessment
if avg_hr < 60:
    print(f"2. 健康評估: 您的平均靜止心率 ({avg_hr:.1f} bpm) 較低，這通常表示良好的心血管健康狀態")
elif avg_hr <= 100:
    print(f"2. 健康評估: 您的平均靜止心率 ({avg_hr:.1f} bpm) 在正常範圍內 (60-100 bpm)")
else:
    print(f"2. 健康評估: 您的平均靜止心率 ({avg_hr:.1f} bpm) 偏高，建議諮詢醫師")

# Variability
if std_hr > 15:
    print(f"3. 變異性: 您的靜止心率變異較大 (標準差: {std_hr:.1f})，可能受到壓力、睡眠或生活習慣影響")
else:
    print(f"3. 變異性: 您的靜止心率相對穩定 (標準差: {std_hr:.1f})，顯示良好的生理調節")

# Extreme values
high_hr_days = sum(1 for v in values if v > 100)
low_hr_days = sum(1 for v in values if v < 60)
if high_hr_days > 0:
    print(f"4. 異常值: 有 {high_hr_days} 天記錄超過 100 bpm，可能與壓力、疾病或藥物有關")
if low_hr_days > 0:
    print(f"5. 低心率: 有 {low_hr_days} 天記錄低於 60 bpm，如果您不是運動員，建議注意是否有其他症狀")

print("\n建議: 定期監測靜止心率有助於了解整體健康狀況。如有持續異常，請諮詢醫療專業人員。")