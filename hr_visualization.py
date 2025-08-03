import xml.etree.ElementTree as ET
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
    print("Usage: python hr_visualization.py [path_to_export.xml]")
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

# Yearly analysis for visualization
yearly_data = defaultdict(list)
for date, value in zip(dates, values):
    yearly_data[date.year].append(value)

# Create ASCII visualization
print("\n=== 靜止心率趨勢圖 (年度平均) ===\n")
print("  140 |")
print("  130 |")
print("  120 |")
print("  110 |")
print("  100 |" + "-" * 60)
print("   90 |", end="")
print("   80 |", end="")
print("   70 |", end="")
print("   60 |" + "-" * 60)
print("   50 |")
print("      +" + "-" * 60)
print("       2019  2020  2021  2022  2023  2024  2025")

# Plot yearly averages
years = sorted(yearly_data.keys())
for year in years:
    year_avg = sum(yearly_data[year]) / len(yearly_data[year])
    col_position = 7 + (year - 2019) * 8
    
    # Calculate row position (140 bpm = row 1, 50 bpm = row 10)
    row = int((140 - year_avg) / 10) + 1
    
    # Print the bar
    for i in range(1, 11):
        print(f"\033[{i};{col_position}H", end="")
        if i >= row:
            print("███", end="")
    
    # Print value
    print(f"\033[{row-1};{col_position}H{int(year_avg)}", end="")

# Reset cursor position
print("\033[13;0H")

# Monthly trend for recent years
print("\n\n=== 月度趨勢 (2023-2025) ===")
monthly_data = defaultdict(list)
for date, value in zip(dates, values):
    if date.year >= 2023:
        month_key = f"{date.year}-{date.month:02d}"
        monthly_data[month_key].append(value)

print("\nbpm")
print("100 |")
print(" 95 |")  
print(" 90 |")
print(" 85 |")
print(" 80 |")
print(" 75 |")
print(" 70 |")
print(" 65 |")
print("    +" + "-" * 65)
print("     ", end="")

# Print month labels
months = sorted(monthly_data.keys())
for i, month in enumerate(months):
    if i % 3 == 0:  # Show every 3rd month
        print(f"{month[5:7]}/{month[2:4]}", end="  ")
    else:
        print("     ", end="  ")
print()

# Create simple line chart
chart_width = 65
chart_height = 8
min_val = 65
max_val = 100
chart = [[' ' for _ in range(chart_width)] for _ in range(chart_height)]

# Plot points
for i, month in enumerate(months):
    if month in monthly_data:
        month_avg = sum(monthly_data[month]) / len(monthly_data[month])
        x = min(int(i * chart_width / len(months)), chart_width - 1)
        y = int((max_val - month_avg) * chart_height / (max_val - min_val))
        y = max(0, min(chart_height - 1, y))
        chart[y][x] = '●'

# Connect points with lines
prev_x, prev_y = None, None
for i, month in enumerate(months):
    if month in monthly_data:
        month_avg = sum(monthly_data[month]) / len(monthly_data[month])
        x = min(int(i * chart_width / len(months)), chart_width - 1)
        y = int((max_val - month_avg) * chart_height / (max_val - min_val))
        y = max(0, min(chart_height - 1, y))
        
        if prev_x is not None and abs(x - prev_x) == 1:
            # Draw line between points
            if y == prev_y:
                chart[y][x] = '─'
            elif y > prev_y:
                chart[y][x] = '╱'
            else:
                chart[y][x] = '╲'
        
        prev_x, prev_y = x, y

# Print chart
for row in chart:
    print("     " + ''.join(row))

print("\n圖例: ● = 月平均值")

# Save detailed data to CSV in current directory
output_csv = 'resting_heart_rate_data.csv'
with open(output_csv, 'w') as f:
    f.write("Date,Resting Heart Rate (bpm)\n")
    for date, value in zip(dates, values):
        f.write(f"{date.strftime('%Y-%m-%d')},{value:.1f}\n")

print(f"\n詳細數據已保存至: {os.path.abspath(output_csv)}")