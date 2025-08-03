import xml.etree.ElementTree as ET
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np

def parse_hrv_data(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    hrv_data = []
    
    for record in root.findall('.//Record'):
        if record.get('type') == 'HKQuantityTypeIdentifierHeartRateVariabilitySDNN':
            date = record.get('startDate')
            value = record.get('value')
            
            if date and value:
                hrv_data.append({
                    'date': pd.to_datetime(date),
                    'value': float(value)  # 毫秒
                })
    
    return pd.DataFrame(hrv_data)

def analyze_hrv(df):
    # 按日期分組計算每日平均值
    df['date_only'] = df['date'].dt.date
    daily_avg = df.groupby('date_only')['value'].agg(['mean', 'min', 'max', 'std']).reset_index()
    daily_avg['date_only'] = pd.to_datetime(daily_avg['date_only'])
    
    # 計算滾動平均
    daily_avg['rolling_avg_7'] = daily_avg['mean'].rolling(window=7, min_periods=1).mean()
    daily_avg['rolling_avg_30'] = daily_avg['mean'].rolling(window=30, min_periods=1).mean()
    
    return daily_avg

def plot_hrv(daily_avg):
    plt.figure(figsize=(15, 8))
    
    # 繪製每日平均值與範圍
    plt.fill_between(daily_avg['date_only'], daily_avg['min'], daily_avg['max'], 
                     alpha=0.2, color='lightgreen', label='Daily Range')
    plt.scatter(daily_avg['date_only'], daily_avg['mean'], 
                alpha=0.5, s=20, color='darkgreen', label='Daily Average')
    
    # 繪製移動平均線
    plt.plot(daily_avg['date_only'], daily_avg['rolling_avg_7'], 
             color='orange', linewidth=2, label='7-Day Moving Average')
    plt.plot(daily_avg['date_only'], daily_avg['rolling_avg_30'], 
             color='red', linewidth=2, label='30-Day Moving Average')
    
    # 添加參考線
    mean_hrv = daily_avg['mean'].mean()
    plt.axhline(y=mean_hrv, color='blue', linestyle='--', alpha=0.5, label=f'Overall Average ({mean_hrv:.1f}ms)')
    
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Heart Rate Variability SDNN (ms)', fontsize=12)
    plt.title('Heart Rate Variability (HRV) Trend Analysis', fontsize=16, fontweight='bold')
    plt.legend(loc='best')
    plt.grid(True, alpha=0.3)
    
    # 格式化x軸日期
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig('hrv_analysis.png', dpi=300)
    plt.close()
    
    # 生成統計摘要
    print("\nHeart Rate Variability Statistics Summary:")
    print(f"Average HRV: {daily_avg['mean'].mean():.2f} ms")
    print(f"Minimum HRV: {daily_avg['min'].min():.2f} ms")
    print(f"Maximum HRV: {daily_avg['max'].max():.2f} ms")
    print(f"Standard deviation: {daily_avg['mean'].std():.2f} ms")
    
    # HRV趨勢分析
    recent_avg = daily_avg['mean'].tail(30).mean()
    overall_avg = daily_avg['mean'].mean()
    trend = "increased" if recent_avg > overall_avg else "decreased"
    print(f"\nTrend Analysis: Last 30 days average HRV {trend} by {abs(recent_avg - overall_avg):.1f} ms compared to overall average")

if __name__ == "__main__":
    df = parse_hrv_data('輸出.xml')
    daily_avg = analyze_hrv(df)
    plot_hrv(daily_avg)