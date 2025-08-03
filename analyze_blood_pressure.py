import xml.etree.ElementTree as ET
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np

def parse_blood_pressure_data(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    bp_data = []
    
    # 收集收縮壓和舒張壓數據
    systolic_records = {}
    diastolic_records = {}
    
    for record in root.findall('.//Record'):
        record_type = record.get('type')
        date = record.get('startDate')
        value = record.get('value')
        
        if date and value:
            timestamp = pd.to_datetime(date)
            
            if record_type == 'HKQuantityTypeIdentifierBloodPressureSystolic':
                systolic_records[timestamp] = float(value)
            elif record_type == 'HKQuantityTypeIdentifierBloodPressureDiastolic':
                diastolic_records[timestamp] = float(value)
    
    # 配對收縮壓和舒張壓
    for timestamp in systolic_records:
        if timestamp in diastolic_records:
            bp_data.append({
                'date': timestamp,
                'systolic': systolic_records[timestamp],
                'diastolic': diastolic_records[timestamp]
            })
    
    return pd.DataFrame(bp_data)

def analyze_blood_pressure(df):
    # 按日期排序
    df = df.sort_values('date')
    
    # 計算脈壓
    df['pulse_pressure'] = df['systolic'] - df['diastolic']
    
    # 分類血壓狀態
    def classify_bp(row):
        if row['systolic'] < 120 and row['diastolic'] < 80:
            return 'Normal'
        elif row['systolic'] < 130 and row['diastolic'] < 80:
            return 'Elevated'
        elif row['systolic'] < 140 or row['diastolic'] < 90:
            return 'Stage 1 HTN'
        elif row['systolic'] < 160 or row['diastolic'] < 100:
            return 'Stage 2 HTN'
        else:
            return 'HTN Crisis'
    
    df['category'] = df.apply(classify_bp, axis=1)
    
    return df

def plot_blood_pressure(df):
    plt.figure(figsize=(15, 10))
    
    # 繪製血壓趨勢圖
    plt.subplot(2, 1, 1)
    plt.plot(df['date'], df['systolic'], 'ro-', label='Systolic', markersize=6, alpha=0.7)
    plt.plot(df['date'], df['diastolic'], 'bo-', label='Diastolic', markersize=6, alpha=0.7)
    
    # 添加正常範圍參考線
    plt.axhline(y=120, color='green', linestyle='--', alpha=0.5, label='Normal Systolic Upper Limit')
    plt.axhline(y=80, color='lightgreen', linestyle='--', alpha=0.5, label='Normal Diastolic Upper Limit')
    plt.axhline(y=140, color='orange', linestyle='--', alpha=0.5, label='Hypertension Threshold')
    plt.axhline(y=90, color='orange', linestyle='--', alpha=0.3)
    
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Blood Pressure (mmHg)', fontsize=12)
    plt.title('Blood Pressure Trend Analysis', fontsize=16, fontweight='bold')
    plt.legend(loc='best')
    plt.grid(True, alpha=0.3)
    
    # 格式化x軸日期
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.xticks(rotation=45)
    
    # 繪製血壓分類統計
    plt.subplot(2, 1, 2)
    category_counts = df['category'].value_counts()
    colors = {'Normal': 'green', 'Elevated': 'yellow', 'Stage 1 HTN': 'orange', 
              'Stage 2 HTN': 'red', 'HTN Crisis': 'darkred'}
    
    bars = plt.bar(category_counts.index, category_counts.values, 
                    color=[colors.get(cat, 'gray') for cat in category_counts.index])
    
    plt.xlabel('Blood Pressure Category', fontsize=12)
    plt.ylabel('Number of Measurements', fontsize=12)
    plt.title('Blood Pressure Category Distribution', fontsize=14, fontweight='bold')
    
    # 添加數值標籤
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                 f'{int(height)}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('blood_pressure_analysis.png', dpi=300)
    plt.close()
    
    # 生成統計摘要
    print("\nBlood Pressure Statistics Summary:")
    print(f"Average systolic: {df['systolic'].mean():.1f} mmHg")
    print(f"Average diastolic: {df['diastolic'].mean():.1f} mmHg")
    print(f"Average pulse pressure: {df['pulse_pressure'].mean():.1f} mmHg")
    print(f"\nBlood Pressure Category Distribution:")
    for category, count in category_counts.items():
        percentage = (count / len(df)) * 100
        print(f"{category}: {count} measurements ({percentage:.1f}%)")

if __name__ == "__main__":
    df = parse_blood_pressure_data('輸出.xml')
    df = analyze_blood_pressure(df)
    plot_blood_pressure(df)