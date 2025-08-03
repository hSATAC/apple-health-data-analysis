import xml.etree.ElementTree as ET
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np

def parse_sleep_data(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    sleep_data = []
    
    for record in root.findall('.//Record'):
        if record.get('type') == 'HKCategoryTypeIdentifierSleepAnalysis':
            start_date = record.get('startDate')
            end_date = record.get('endDate')
            value = record.get('value')
            
            if start_date and end_date and value:
                sleep_data.append({
                    'start': pd.to_datetime(start_date),
                    'end': pd.to_datetime(end_date),
                    'value': value
                })
    
    return pd.DataFrame(sleep_data)

def analyze_sleep_patterns(df):
    # 計算每次睡眠的持續時間
    df['duration_hours'] = (df['end'] - df['start']).dt.total_seconds() / 3600
    
    # 按日期分組計算每日總睡眠時間
    df['date'] = df['start'].dt.date
    daily_sleep = df.groupby('date')['duration_hours'].sum().reset_index()
    daily_sleep['date'] = pd.to_datetime(daily_sleep['date'])
    
    # 計算滾動平均
    daily_sleep['rolling_avg_7'] = daily_sleep['duration_hours'].rolling(window=7, min_periods=1).mean()
    daily_sleep['rolling_avg_30'] = daily_sleep['duration_hours'].rolling(window=30, min_periods=1).mean()
    
    return daily_sleep

def plot_sleep_patterns(daily_sleep):
    plt.figure(figsize=(15, 8))
    
    # 繪製每日睡眠時間
    plt.scatter(daily_sleep['date'], daily_sleep['duration_hours'], 
                alpha=0.3, s=20, label='Daily Sleep Hours')
    
    # 繪製移動平均線
    plt.plot(daily_sleep['date'], daily_sleep['rolling_avg_7'], 
             color='orange', linewidth=2, label='7-Day Moving Average')
    plt.plot(daily_sleep['date'], daily_sleep['rolling_avg_30'], 
             color='red', linewidth=2, label='30-Day Moving Average')
    
    # 添加建議睡眠時間參考線
    plt.axhline(y=8, color='green', linestyle='--', alpha=0.5, label='Recommended Sleep (8 hours)')
    plt.axhline(y=7, color='yellow', linestyle='--', alpha=0.5, label='Minimum Recommended (7 hours)')
    
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Sleep Hours', fontsize=12)
    plt.title('Sleep Pattern Analysis', fontsize=16, fontweight='bold')
    plt.legend(loc='best')
    plt.grid(True, alpha=0.3)
    
    # 格式化x軸日期
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig('sleep_patterns_analysis.png', dpi=300)
    plt.close()
    
    # 生成統計摘要
    print("\nSleep Statistics Summary:")
    print(f"Average daily sleep hours: {daily_sleep['duration_hours'].mean():.2f} hours")
    print(f"Minimum sleep hours: {daily_sleep['duration_hours'].min():.2f} hours")
    print(f"Maximum sleep hours: {daily_sleep['duration_hours'].max():.2f} hours")
    print(f"Standard deviation: {daily_sleep['duration_hours'].std():.2f} hours")

if __name__ == "__main__":
    df = parse_sleep_data('輸出.xml')
    daily_sleep = analyze_sleep_patterns(df)
    plot_sleep_patterns(daily_sleep)