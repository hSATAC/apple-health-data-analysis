import xml.etree.ElementTree as ET
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np
from matplotlib.gridspec import GridSpec
import matplotlib.font_manager as fm

# Set up for better font rendering
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def parse_health_data_summary(xml_file, days_back=90):
    """Parse only summary statistics for faster processing"""
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Calculate cutoff date
    cutoff_date = pd.Timestamp.now() - timedelta(days=days_back)
    
    # Initialize data collections with daily aggregation
    daily_data = {}
    
    print("Parsing health data...")
    record_count = 0
    
    for record in root.findall('.//Record'):
        record_type = record.get('type')
        date = record.get('startDate')
        value = record.get('value')
        
        if date and value:
            timestamp = pd.to_datetime(date)
            
            # Skip old data
            if timestamp.tz_localize(None) < cutoff_date.tz_localize(None):
                continue
            
            date_key = timestamp.date()
            
            # Initialize daily data if needed
            if date_key not in daily_data:
                daily_data[date_key] = {
                    'hr_values': [],
                    'hrv_values': [],
                    'o2_values': [],
                    'sleep_hours': 0,
                    'calories': 0,
                    'steps': 0
                }
            
            # Aggregate data by type
            if record_type == 'HKQuantityTypeIdentifierRestingHeartRate':
                daily_data[date_key]['hr_values'].append(float(value))
            elif record_type == 'HKQuantityTypeIdentifierHeartRateVariabilitySDNN':
                daily_data[date_key]['hrv_values'].append(float(value))
            elif record_type == 'HKQuantityTypeIdentifierOxygenSaturation':
                daily_data[date_key]['o2_values'].append(float(value) * 100)
            elif record_type == 'HKCategoryTypeIdentifierSleepAnalysis':
                end_date = record.get('endDate')
                if end_date:
                    duration = (pd.to_datetime(end_date) - timestamp).total_seconds() / 3600
                    if 0 < duration < 24:  # Reasonable sleep duration
                        daily_data[date_key]['sleep_hours'] += duration
            elif record_type == 'HKQuantityTypeIdentifierActiveEnergyBurned':
                daily_data[date_key]['calories'] += float(value)
            elif record_type == 'HKQuantityTypeIdentifierStepCount':
                daily_data[date_key]['steps'] += float(value)
            
            record_count += 1
            if record_count % 10000 == 0:
                print(f"  Processed {record_count} records...")
    
    print(f"Total records processed: {record_count}")
    
    # Convert to DataFrame
    processed_data = []
    for date, values in daily_data.items():
        row = {
            'date': pd.to_datetime(date),
            'hr': np.mean(values['hr_values']) if values['hr_values'] else np.nan,
            'hrv': np.mean(values['hrv_values']) if values['hrv_values'] else np.nan,
            'o2': np.mean(values['o2_values']) if values['o2_values'] else np.nan,
            'sleep': min(values['sleep_hours'], 24),  # Cap at 24 hours
            'calories': values['calories'],
            'steps': values['steps']
        }
        processed_data.append(row)
    
    df = pd.DataFrame(processed_data).sort_values('date')
    
    # Calculate rolling averages
    for col in ['hr', 'hrv', 'o2', 'sleep', 'calories', 'steps']:
        if col in df.columns:
            df[f'{col}_7d'] = df[col].rolling(window=7, min_periods=1).mean()
    
    return df

def create_health_summary_dashboard(df):
    """Create a simplified dashboard with key metrics"""
    
    # Create figure
    fig = plt.figure(figsize=(16, 10))
    gs = GridSpec(3, 2, figure=fig, hspace=0.35, wspace=0.25)
    
    # Color scheme
    colors = {
        'hr': '#E74C3C',
        'hrv': '#3498DB',
        'o2': '#2ECC71',
        'sleep': '#9B59B6',
        'activity': '#F39C12'
    }
    
    # 1. Heart Health (HR + HRV)
    ax1 = fig.add_subplot(gs[0, 0])
    
    # Plot HR on primary axis
    hr_data = df.dropna(subset=['hr'])
    if not hr_data.empty:
        ax1.scatter(hr_data['date'], hr_data['hr'], alpha=0.3, s=20, color=colors['hr'])
        ax1.plot(hr_data['date'], hr_data['hr_7d'], color=colors['hr'], linewidth=2, label='HR (7d avg)')
        ax1.set_ylabel('Heart Rate (BPM)', color=colors['hr'])
        ax1.tick_params(axis='y', labelcolor=colors['hr'])
        ax1.set_ylim(40, 90)
    
    # Plot HRV on secondary axis
    ax1_twin = ax1.twinx()
    hrv_data = df.dropna(subset=['hrv'])
    if not hrv_data.empty:
        ax1_twin.scatter(hrv_data['date'], hrv_data['hrv'], alpha=0.3, s=20, color=colors['hrv'])
        ax1_twin.plot(hrv_data['date'], hrv_data['hrv_7d'], color=colors['hrv'], linewidth=2, label='HRV (7d avg)')
        ax1_twin.set_ylabel('HRV (ms)', color=colors['hrv'])
        ax1_twin.tick_params(axis='y', labelcolor=colors['hrv'])
    
    ax1.set_title('Heart Rate & Variability', fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # 2. Oxygen Saturation
    ax2 = fig.add_subplot(gs[0, 1])
    o2_data = df.dropna(subset=['o2'])
    if not o2_data.empty:
        ax2.scatter(o2_data['date'], o2_data['o2'], alpha=0.3, s=20, color=colors['o2'])
        ax2.plot(o2_data['date'], o2_data['o2_7d'], color=colors['o2'], linewidth=2)
        ax2.axhline(y=95, color='red', linestyle='--', alpha=0.5, label='Low O2')
        ax2.set_ylabel('SpO2 (%)')
        ax2.set_ylim(88, 101)
        ax2.set_title('Oxygen Saturation', fontweight='bold')
        ax2.grid(True, alpha=0.3)
    
    # 3. Sleep Pattern
    ax3 = fig.add_subplot(gs[1, 0])
    sleep_data = df.dropna(subset=['sleep'])
    if not sleep_data.empty:
        ax3.bar(sleep_data['date'], sleep_data['sleep'], alpha=0.5, color=colors['sleep'])
        ax3.plot(sleep_data['date'], sleep_data['sleep_7d'], color=colors['sleep'], linewidth=2)
        ax3.axhline(y=8, color='green', linestyle='--', alpha=0.5, label='Target')
        ax3.set_ylabel('Hours')
        ax3.set_ylim(0, 12)
        ax3.set_title('Sleep Duration', fontweight='bold')
        ax3.grid(True, alpha=0.3)
    
    # 4. Activity (Calories + Steps)
    ax4 = fig.add_subplot(gs[1, 1])
    activity_data = df.dropna(subset=['calories'])
    if not activity_data.empty:
        ax4.bar(activity_data['date'], activity_data['calories'], alpha=0.5, color=colors['activity'])
        ax4.plot(activity_data['date'], activity_data['calories_7d'], color=colors['activity'], linewidth=2)
        ax4.axhline(y=500, color='green', linestyle='--', alpha=0.5)
        ax4.set_ylabel('Calories')
        ax4.set_title('Daily Active Calories', fontweight='bold')
        ax4.grid(True, alpha=0.3)
    
    # 5. Summary Statistics
    ax5 = fig.add_subplot(gs[2, :])
    ax5.axis('off')
    
    # Calculate summary stats
    summary_text = "HEALTH SUMMARY (Last 30 Days)\\n\\n"
    
    last_30 = df.tail(30)
    
    if 'hr' in last_30.columns:
        avg_hr = last_30['hr'].mean()
        summary_text += f"Heart Rate: {avg_hr:.1f} BPM\\n"
    
    if 'hrv' in last_30.columns:
        avg_hrv = last_30['hrv'].mean()
        summary_text += f"HRV: {avg_hrv:.1f} ms\\n"
    
    if 'o2' in last_30.columns:
        avg_o2 = last_30['o2'].mean()
        low_o2_days = (last_30['o2'] < 95).sum()
        summary_text += f"Oxygen: {avg_o2:.1f}% (Low: {low_o2_days} days)\\n"
    
    if 'sleep' in last_30.columns:
        avg_sleep = last_30['sleep'].mean()
        summary_text += f"Sleep: {avg_sleep:.1f} hours/night\\n"
    
    if 'calories' in last_30.columns:
        avg_cal = last_30['calories'].mean()
        summary_text += f"Activity: {avg_cal:.0f} cal/day\\n"
    
    if 'steps' in last_30.columns:
        avg_steps = last_30['steps'].mean()
        summary_text += f"Steps: {avg_steps:.0f} steps/day"
    
    ax5.text(0.5, 0.5, summary_text, transform=ax5.transAxes,
             fontsize=14, ha='center', va='center',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgray', alpha=0.5))
    
    # Format x-axis dates
    for ax in [ax1, ax2, ax3, ax4]:
        if ax.has_data():
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=15))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    # Main title
    fig.suptitle(f'Health Dashboard - Last {len(df)} Days', fontsize=16, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('health_summary_dashboard.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("\\nDashboard saved as 'health_summary_dashboard.png'")
    
    return summary_text

def print_insights(df):
    """Print health insights based on the data"""
    print("\\n=== HEALTH INSIGHTS ===\\n")
    
    # Recent data
    recent = df.tail(30)
    
    # 1. Cardiovascular Health
    if 'hr' in recent.columns and 'hrv' in recent.columns:
        hr_trend = recent['hr'].iloc[-1] - recent['hr'].iloc[0] if len(recent) > 1 else 0
        hrv_trend = recent['hrv'].iloc[-1] - recent['hrv'].iloc[0] if len(recent) > 1 else 0
        
        if hr_trend < 0 and hrv_trend > 0:
            print("✓ Cardiovascular health improving (HR ↓, HRV ↑)")
        elif hr_trend > 0 and hrv_trend < 0:
            print("⚠ Signs of stress or overtraining (HR ↑, HRV ↓)")
    
    # 2. Sleep Quality
    if 'sleep' in recent.columns:
        avg_sleep = recent['sleep'].mean()
        if avg_sleep >= 7:
            print(f"✓ Good sleep average: {avg_sleep:.1f} hours")
        else:
            print(f"⚠ Low sleep average: {avg_sleep:.1f} hours (target: 7-9)")
    
    # 3. Activity Level
    if 'calories' in recent.columns:
        avg_cal = recent['calories'].mean()
        active_days = (recent['calories'] >= 500).sum()
        print(f"📊 Activity: {active_days}/30 days met 500+ calorie goal")
    
    # 4. Oxygen Levels
    if 'o2' in recent.columns:
        low_o2 = (recent['o2'] < 95).sum()
        if low_o2 > 5:
            print(f"⚠ Low oxygen on {low_o2} days - consider medical consultation")
        else:
            print("✓ Oxygen levels generally normal")
    
    print("\\n" + "="*40)

if __name__ == "__main__":
    print("Loading health data (last 90 days)...")
    
    # Parse and process data
    df = parse_health_data_summary('輸出.xml', days_back=90)
    
    print(f"\\nData summary: {len(df)} days of data loaded")
    print(f"Metrics available: {[col for col in df.columns if not col.endswith('_7d')]}")
    
    # Create dashboard
    summary = create_health_summary_dashboard(df)
    
    # Print insights
    print_insights(df)