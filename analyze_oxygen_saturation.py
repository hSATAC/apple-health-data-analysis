import xml.etree.ElementTree as ET
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np

def parse_oxygen_data(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    oxygen_data = []
    
    for record in root.findall('.//Record'):
        if record.get('type') == 'HKQuantityTypeIdentifierOxygenSaturation':
            date = record.get('startDate')
            value = record.get('value')
            
            if date and value:
                oxygen_data.append({
                    'date': pd.to_datetime(date),
                    'value': float(value) * 100  # 轉換為百分比
                })
    
    return pd.DataFrame(oxygen_data)

def analyze_oxygen_saturation(df):
    # 按日期分組計算每日平均值
    df['date_only'] = df['date'].dt.date
    daily_avg = df.groupby('date_only')['value'].agg(['mean', 'min', 'max', 'std']).reset_index()
    daily_avg['date_only'] = pd.to_datetime(daily_avg['date_only'])
    
    # 計算滾動平均
    daily_avg['rolling_avg_7'] = daily_avg['mean'].rolling(window=7, min_periods=1).mean()
    daily_avg['rolling_avg_30'] = daily_avg['mean'].rolling(window=30, min_periods=1).mean()
    
    return daily_avg

def plot_oxygen_saturation(daily_avg):
    plt.figure(figsize=(15, 8))
    
    # 繪製每日平均值與範圍
    plt.fill_between(daily_avg['date_only'], daily_avg['min'], daily_avg['max'], 
                     alpha=0.2, color='lightblue', label='Daily Range')
    plt.scatter(daily_avg['date_only'], daily_avg['mean'], 
                alpha=0.5, s=20, color='blue', label='Daily Average')
    
    # 繪製移動平均線
    plt.plot(daily_avg['date_only'], daily_avg['rolling_avg_7'], 
             color='orange', linewidth=2, label='7-Day Moving Average')
    plt.plot(daily_avg['date_only'], daily_avg['rolling_avg_30'], 
             color='red', linewidth=2, label='30-Day Moving Average')
    
    # 添加正常範圍參考線
    plt.axhline(y=95, color='green', linestyle='--', alpha=0.5, label='Normal Range Lower Limit (95%)')
    plt.axhline(y=90, color='red', linestyle='--', alpha=0.5, label='Low Oxygen Warning (90%)')
    
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Oxygen Saturation (%)', fontsize=12)
    plt.title('Oxygen Saturation Trend Analysis', fontsize=16, fontweight='bold')
    plt.legend(loc='best')
    plt.grid(True, alpha=0.3)
    plt.ylim(85, 102)
    
    # 格式化x軸日期
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig('oxygen_saturation_analysis.png', dpi=300)
    plt.close()
    
    # 生成統計摘要
    print("\nOxygen Saturation Statistics Summary:")
    print(f"Average oxygen saturation: {daily_avg['mean'].mean():.2f}%")
    print(f"Minimum oxygen saturation: {daily_avg['min'].min():.2f}%")
    print(f"Maximum oxygen saturation: {daily_avg['max'].max():.2f}%")
    print(f"Days below 95%: {(daily_avg['mean'] < 95).sum()} days")

if __name__ == "__main__":
    df = parse_oxygen_data('輸出.xml')
    daily_avg = analyze_oxygen_saturation(df)
    plot_oxygen_saturation(daily_avg)