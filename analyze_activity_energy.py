import xml.etree.ElementTree as ET
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np

def parse_activity_data(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    activity_data = []
    
    for record in root.findall('.//Record'):
        record_type = record.get('type')
        date = record.get('startDate')
        value = record.get('value')
        
        if date and value and record_type in ['HKQuantityTypeIdentifierActiveEnergyBurned', 
                                               'HKQuantityTypeIdentifierStepCount']:
            activity_data.append({
                'date': pd.to_datetime(date),
                'type': record_type,
                'value': float(value)
            })
    
    return pd.DataFrame(activity_data)

def analyze_activity(df):
    # 分離不同類型的數據
    energy_df = df[df['type'] == 'HKQuantityTypeIdentifierActiveEnergyBurned'].copy()
    steps_df = df[df['type'] == 'HKQuantityTypeIdentifierStepCount'].copy()
    
    # 按日期分組計算每日總和
    energy_df['date_only'] = energy_df['date'].dt.date
    daily_energy = energy_df.groupby('date_only')['value'].sum().reset_index()
    daily_energy['date_only'] = pd.to_datetime(daily_energy['date_only'])
    daily_energy.columns = ['date', 'calories']
    
    steps_df['date_only'] = steps_df['date'].dt.date
    daily_steps = steps_df.groupby('date_only')['value'].sum().reset_index()
    daily_steps['date_only'] = pd.to_datetime(daily_steps['date_only'])
    daily_steps.columns = ['date', 'steps']
    
    # 合併數據
    daily_activity = pd.merge(daily_energy, daily_steps, on='date', how='outer')
    daily_activity = daily_activity.sort_values('date')
    
    # 計算滾動平均
    daily_activity['calories_avg_7'] = daily_activity['calories'].rolling(window=7, min_periods=1).mean()
    daily_activity['steps_avg_7'] = daily_activity['steps'].rolling(window=7, min_periods=1).mean()
    
    return daily_activity

def plot_activity(daily_activity):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))
    
    # 繪製卡路里消耗
    ax1.bar(daily_activity['date'], daily_activity['calories'], 
            alpha=0.3, color='orange', label='Daily Burn')
    ax1.plot(daily_activity['date'], daily_activity['calories_avg_7'], 
             color='red', linewidth=2, label='7-Day Moving Average')
    
    # 添加目標線
    ax1.axhline(y=500, color='green', linestyle='--', alpha=0.5, label='Recommended Minimum (500 kcal)')
    
    ax1.set_ylabel('Active Calories (kcal)', fontsize=12)
    ax1.set_title('Daily Active Energy Burned', fontsize=14, fontweight='bold')
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)
    
    # 繪製步數
    ax2.bar(daily_activity['date'], daily_activity['steps'], 
            alpha=0.3, color='blue', label='Daily Steps')
    ax2.plot(daily_activity['date'], daily_activity['steps_avg_7'], 
             color='darkblue', linewidth=2, label='7-Day Moving Average')
    
    # 添加目標線
    ax2.axhline(y=10000, color='green', linestyle='--', alpha=0.5, label='Recommended Goal (10,000 steps)')
    ax2.axhline(y=7500, color='yellow', linestyle='--', alpha=0.5, label='Minimum Goal (7,500 steps)')
    
    ax2.set_xlabel('Date', fontsize=12)
    ax2.set_ylabel('Steps', fontsize=12)
    ax2.set_title('Daily Step Count', fontsize=14, fontweight='bold')
    ax2.legend(loc='best')
    ax2.grid(True, alpha=0.3)
    
    # 格式化x軸日期
    for ax in [ax1, ax2]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('activity_energy_analysis.png', dpi=300)
    plt.close()
    
    # 生成統計摘要
    print("\nActivity Statistics Summary:")
    print(f"Average daily active calories: {daily_activity['calories'].mean():.0f} kcal")
    print(f"Maximum daily calories: {daily_activity['calories'].max():.0f} kcal")
    print(f"Average daily steps: {daily_activity['steps'].mean():.0f} steps")
    print(f"Maximum daily steps: {daily_activity['steps'].max():.0f} steps")
    print(f"Days reaching 10,000 steps goal: {(daily_activity['steps'] >= 10000).sum()} days")
    print(f"Days reaching 500 kcal goal: {(daily_activity['calories'] >= 500).sum()} days")

if __name__ == "__main__":
    df = parse_activity_data('輸出.xml')
    daily_activity = analyze_activity(df)
    plot_activity(daily_activity)