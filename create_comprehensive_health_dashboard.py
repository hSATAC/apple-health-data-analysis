import xml.etree.ElementTree as ET
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np
from matplotlib.gridspec import GridSpec

def parse_all_health_data(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Initialize data collections
    resting_hr_data = []
    hrv_data = []
    oxygen_data = []
    sleep_data = []
    activity_data = []
    
    for record in root.findall('.//Record'):
        record_type = record.get('type')
        date = record.get('startDate')
        value = record.get('value')
        
        if date and value:
            timestamp = pd.to_datetime(date)
            
            if record_type == 'HKQuantityTypeIdentifierRestingHeartRate':
                resting_hr_data.append({'date': timestamp, 'value': float(value)})
            elif record_type == 'HKQuantityTypeIdentifierHeartRateVariabilitySDNN':
                hrv_data.append({'date': timestamp, 'value': float(value)})
            elif record_type == 'HKQuantityTypeIdentifierOxygenSaturation':
                oxygen_data.append({'date': timestamp, 'value': float(value) * 100})
            elif record_type == 'HKCategoryTypeIdentifierSleepAnalysis':
                end_date = record.get('endDate')
                if end_date:
                    sleep_data.append({
                        'date': timestamp.date(),
                        'duration': (pd.to_datetime(end_date) - timestamp).total_seconds() / 3600
                    })
            elif record_type == 'HKQuantityTypeIdentifierActiveEnergyBurned':
                activity_data.append({
                    'date': timestamp.date(),
                    'calories': float(value)
                })
    
    # Convert to DataFrames
    resting_hr_df = pd.DataFrame(resting_hr_data) if resting_hr_data else pd.DataFrame()
    hrv_df = pd.DataFrame(hrv_data) if hrv_data else pd.DataFrame()
    oxygen_df = pd.DataFrame(oxygen_data) if oxygen_data else pd.DataFrame()
    sleep_df = pd.DataFrame(sleep_data) if sleep_data else pd.DataFrame()
    activity_df = pd.DataFrame(activity_data) if activity_data else pd.DataFrame()
    
    return resting_hr_df, hrv_df, oxygen_df, sleep_df, activity_df

def process_daily_data(df, value_col='value', agg_func='mean'):
    if df.empty:
        return pd.DataFrame()
    
    df['date_only'] = df['date'].dt.date if 'date' in df.columns and not df['date'].dtype == 'object' else df['date']
    daily = df.groupby('date_only')[value_col].agg(agg_func).reset_index()
    daily['date_only'] = pd.to_datetime(daily['date_only'])
    daily = daily.sort_values('date_only')
    
    # Calculate rolling averages
    daily['rolling_7'] = daily[value_col].rolling(window=7, min_periods=1).mean()
    daily['rolling_30'] = daily[value_col].rolling(window=30, min_periods=1).mean()
    
    return daily

def create_comprehensive_dashboard(resting_hr_df, hrv_df, oxygen_df, sleep_df, activity_df):
    # Process daily data
    daily_hr = process_daily_data(resting_hr_df) if not resting_hr_df.empty else pd.DataFrame()
    daily_hrv = process_daily_data(hrv_df) if not hrv_df.empty else pd.DataFrame()
    daily_oxygen = process_daily_data(oxygen_df) if not oxygen_df.empty else pd.DataFrame()
    daily_sleep = process_daily_data(sleep_df, 'duration', 'sum') if not sleep_df.empty else pd.DataFrame()
    daily_activity = process_daily_data(activity_df, 'calories', 'sum') if not activity_df.empty else pd.DataFrame()
    
    # Create figure with custom layout
    fig = plt.figure(figsize=(20, 16))
    gs = GridSpec(4, 2, figure=fig, hspace=0.3, wspace=0.2)
    
    # Define color scheme
    colors = {
        'hr': '#FF6B6B',
        'hrv': '#4ECDC4',
        'oxygen': '#45B7D1',
        'sleep': '#96CEB4',
        'activity': '#FFA500'
    }
    
    # 1. Resting Heart Rate
    ax1 = fig.add_subplot(gs[0, 0])
    if not daily_hr.empty:
        ax1.scatter(daily_hr['date_only'], daily_hr['value'], alpha=0.3, s=10, color=colors['hr'])
        ax1.plot(daily_hr['date_only'], daily_hr['rolling_30'], color=colors['hr'], linewidth=2)
        ax1.axhline(y=daily_hr['value'].mean(), color='gray', linestyle='--', alpha=0.5)
        ax1.set_title('Resting Heart Rate Trend', fontsize=14, fontweight='bold')
        ax1.set_ylabel('BPM')
        ax1.grid(True, alpha=0.3)
    
    # 2. Heart Rate Variability
    ax2 = fig.add_subplot(gs[0, 1])
    if not daily_hrv.empty:
        ax2.scatter(daily_hrv['date_only'], daily_hrv['value'], alpha=0.3, s=10, color=colors['hrv'])
        ax2.plot(daily_hrv['date_only'], daily_hrv['rolling_30'], color=colors['hrv'], linewidth=2)
        ax2.axhline(y=daily_hrv['value'].mean(), color='gray', linestyle='--', alpha=0.5)
        ax2.set_title('Heart Rate Variability (HRV)', fontsize=14, fontweight='bold')
        ax2.set_ylabel('SDNN (ms)')
        ax2.grid(True, alpha=0.3)
    
    # 3. Oxygen Saturation
    ax3 = fig.add_subplot(gs[1, 0])
    if not daily_oxygen.empty:
        ax3.scatter(daily_oxygen['date_only'], daily_oxygen['value'], alpha=0.3, s=10, color=colors['oxygen'])
        ax3.plot(daily_oxygen['date_only'], daily_oxygen['rolling_30'], color=colors['oxygen'], linewidth=2)
        ax3.axhline(y=95, color='red', linestyle='--', alpha=0.5, label='Low O2 Threshold')
        ax3.set_title('Oxygen Saturation', fontsize=14, fontweight='bold')
        ax3.set_ylabel('SpO2 (%)')
        ax3.set_ylim(85, 102)
        ax3.grid(True, alpha=0.3)
    
    # 4. Sleep Duration
    ax4 = fig.add_subplot(gs[1, 1])
    if not daily_sleep.empty:
        ax4.bar(daily_sleep['date_only'], daily_sleep['duration'], alpha=0.3, color=colors['sleep'])
        ax4.plot(daily_sleep['date_only'], daily_sleep['rolling_30'], color=colors['sleep'], linewidth=2)
        ax4.axhline(y=8, color='green', linestyle='--', alpha=0.5, label='Recommended')
        ax4.set_title('Sleep Duration', fontsize=14, fontweight='bold')
        ax4.set_ylabel('Hours')
        ax4.grid(True, alpha=0.3)
    
    # 5. Activity Calories
    ax5 = fig.add_subplot(gs[2, :])
    if not daily_activity.empty:
        ax5.bar(daily_activity['date_only'], daily_activity['calories'], alpha=0.3, color=colors['activity'])
        ax5.plot(daily_activity['date_only'], daily_activity['rolling_30'], color=colors['activity'], linewidth=2)
        ax5.axhline(y=500, color='green', linestyle='--', alpha=0.5, label='Target')
        ax5.set_title('Daily Active Calories Burned', fontsize=14, fontweight='bold')
        ax5.set_ylabel('Calories')
        ax5.grid(True, alpha=0.3)
    
    # 6. Correlation Analysis
    ax6 = fig.add_subplot(gs[3, :])
    
    # Merge all data for correlation analysis
    all_data = pd.DataFrame()
    
    if not daily_hr.empty:
        all_data['HR'] = daily_hr.set_index('date_only')['value']
    if not daily_hrv.empty:
        all_data['HRV'] = daily_hrv.set_index('date_only')['value']
    if not daily_oxygen.empty:
        all_data['O2'] = daily_oxygen.set_index('date_only')['value']
    if not daily_sleep.empty:
        all_data['Sleep'] = daily_sleep.set_index('date_only')['duration']
    if not daily_activity.empty:
        all_data['Activity'] = daily_activity.set_index('date_only')['calories']
    
    if not all_data.empty and len(all_data.columns) > 1:
        # Calculate correlations
        correlations = all_data.corr()
        
        # Create correlation heatmap
        im = ax6.imshow(correlations, cmap='RdBu_r', aspect='auto', vmin=-1, vmax=1)
        
        # Set ticks and labels
        ax6.set_xticks(np.arange(len(correlations.columns)))
        ax6.set_yticks(np.arange(len(correlations.columns)))
        ax6.set_xticklabels(correlations.columns)
        ax6.set_yticklabels(correlations.columns)
        
        # Add correlation values
        for i in range(len(correlations.columns)):
            for j in range(len(correlations.columns)):
                text = ax6.text(j, i, f'{correlations.iloc[i, j]:.2f}',
                               ha="center", va="center", color="black", fontsize=10)
        
        ax6.set_title('Health Metrics Correlation Matrix', fontsize=14, fontweight='bold')
        plt.colorbar(im, ax=ax6, label='Correlation')
    
    # Format dates on x-axis for time series plots
    for ax in [ax1, ax2, ax3, ax4, ax5]:
        if ax.has_data():
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    # Add overall title
    fig.suptitle('Comprehensive Health Dashboard', fontsize=20, fontweight='bold', y=0.98)
    
    plt.tight_layout()
    plt.savefig('comprehensive_health_dashboard.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Generate insights
    generate_insights(daily_hr, daily_hrv, daily_oxygen, daily_sleep, daily_activity)

def generate_insights(daily_hr, daily_hrv, daily_oxygen, daily_sleep, daily_activity):
    print("\n=== COMPREHENSIVE HEALTH INSIGHTS ===\n")
    
    # Recent trends (last 30 days vs overall)
    print("1. RECENT TRENDS (Last 30 days vs Overall Average):")
    
    if not daily_hr.empty:
        recent_hr = daily_hr.tail(30)['value'].mean()
        overall_hr = daily_hr['value'].mean()
        hr_change = ((recent_hr - overall_hr) / overall_hr) * 100
        print(f"   - Resting Heart Rate: {recent_hr:.1f} BPM ({hr_change:+.1f}% change)")
    
    if not daily_hrv.empty:
        recent_hrv = daily_hrv.tail(30)['value'].mean()
        overall_hrv = daily_hrv['value'].mean()
        hrv_change = ((recent_hrv - overall_hrv) / overall_hrv) * 100
        print(f"   - HRV: {recent_hrv:.1f} ms ({hrv_change:+.1f}% change)")
    
    if not daily_oxygen.empty:
        recent_o2 = daily_oxygen.tail(30)['value'].mean()
        overall_o2 = daily_oxygen['value'].mean()
        o2_change = ((recent_o2 - overall_o2) / overall_o2) * 100
        print(f"   - Oxygen Saturation: {recent_o2:.1f}% ({o2_change:+.1f}% change)")
    
    if not daily_sleep.empty:
        recent_sleep = daily_sleep.tail(30)['duration'].mean()
        overall_sleep = daily_sleep['duration'].mean()
        sleep_change = ((recent_sleep - overall_sleep) / overall_sleep) * 100
        print(f"   - Sleep Duration: {recent_sleep:.1f} hours ({sleep_change:+.1f}% change)")
    
    if not daily_activity.empty:
        recent_activity = daily_activity.tail(30)['calories'].mean()
        overall_activity = daily_activity['calories'].mean()
        activity_change = ((recent_activity - overall_activity) / overall_activity) * 100
        print(f"   - Activity Calories: {recent_activity:.0f} kcal ({activity_change:+.1f}% change)")
    
    print("\n2. HEALTH STATUS INDICATORS:")
    
    # Fitness indicators
    if not daily_hr.empty and not daily_hrv.empty:
        if recent_hr < overall_hr and recent_hrv > overall_hrv:
            print("   ✓ Cardiovascular fitness improving (lower HR, higher HRV)")
        elif recent_hr > overall_hr and recent_hrv < overall_hrv:
            print("   ⚠ Possible stress or overtraining (higher HR, lower HRV)")
    
    # Sleep quality
    if not daily_sleep.empty:
        if recent_sleep >= 7:
            print("   ✓ Sleep duration adequate")
        else:
            print("   ⚠ Sleep duration below recommended 7-9 hours")
    
    # Activity level
    if not daily_activity.empty:
        if recent_activity >= 500:
            print("   ✓ Activity level meeting targets")
        else:
            print("   ⚠ Activity level below recommended")
    
    # Oxygen levels
    if not daily_oxygen.empty:
        low_o2_days = (daily_oxygen.tail(30)['value'] < 95).sum()
        if low_o2_days > 0:
            print(f"   ⚠ {low_o2_days} days with low oxygen saturation in last 30 days")
        else:
            print("   ✓ Oxygen saturation consistently normal")
    
    print("\n3. ACTIONABLE RECOMMENDATIONS:")
    
    recommendations = []
    
    if not daily_sleep.empty and recent_sleep < 7:
        recommendations.append("- Prioritize sleep hygiene: aim for 7-9 hours nightly")
    
    if not daily_activity.empty and recent_activity < 500:
        recommendations.append("- Increase daily activity to reach 500+ active calories")
    
    if not daily_hrv.empty and recent_hrv < overall_hrv:
        recommendations.append("- Consider stress management techniques to improve HRV")
    
    if not daily_oxygen.empty and low_o2_days > 5:
        recommendations.append("- Consult healthcare provider about oxygen saturation patterns")
    
    if recommendations:
        for rec in recommendations:
            print(rec)
    else:
        print("   ✓ All metrics within healthy ranges - maintain current habits!")
    
    print("\n" + "="*40)

if __name__ == "__main__":
    # Parse all health data
    resting_hr_df, hrv_df, oxygen_df, sleep_df, activity_df = parse_all_health_data('輸出.xml')
    
    # Create comprehensive dashboard
    create_comprehensive_dashboard(resting_hr_df, hrv_df, oxygen_df, sleep_df, activity_df)