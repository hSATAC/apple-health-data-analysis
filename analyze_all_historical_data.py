import xml.etree.ElementTree as ET
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
from collections import defaultdict
import gc

def parse_all_health_data_efficiently(xml_file):
    """Parse ALL historical data using iterative parsing to handle large files"""
    
    print(f"Starting to parse {xml_file}...")
    print("This may take a few minutes due to file size...")
    
    # Use iterparse for memory-efficient parsing
    context = ET.iterparse(xml_file, events=('start', 'end'))
    context = iter(context)
    event, root = next(context)
    
    # Initialize data collections with monthly aggregation
    monthly_data = defaultdict(lambda: {
        'hr_values': [],
        'hrv_values': [],
        'o2_values': [],
        'sleep_minutes': 0,
        'calories': 0,
        'steps': 0,
        'bp_systolic': [],
        'bp_diastolic': [],
        'record_count': 0
    })
    
    record_count = 0
    
    # Process records one by one
    for event, elem in context:
        if event == 'end' and elem.tag == 'Record':
            record_type = elem.get('type')
            date_str = elem.get('startDate')
            value = elem.get('value')
            
            if date_str and value:
                try:
                    # Parse date and get month key
                    date = pd.to_datetime(date_str)
                    month_key = date.strftime('%Y-%m')
                    
                    # Process different record types
                    if record_type == 'HKQuantityTypeIdentifierRestingHeartRate':
                        monthly_data[month_key]['hr_values'].append(float(value))
                    
                    elif record_type == 'HKQuantityTypeIdentifierHeartRateVariabilitySDNN':
                        monthly_data[month_key]['hrv_values'].append(float(value))
                    
                    elif record_type == 'HKQuantityTypeIdentifierOxygenSaturation':
                        monthly_data[month_key]['o2_values'].append(float(value) * 100)
                    
                    elif record_type == 'HKCategoryTypeIdentifierSleepAnalysis':
                        end_date = elem.get('endDate')
                        if end_date:
                            duration_minutes = (pd.to_datetime(end_date) - date).total_seconds() / 60
                            if 0 < duration_minutes < 1440:  # Less than 24 hours
                                monthly_data[month_key]['sleep_minutes'] += duration_minutes
                    
                    elif record_type == 'HKQuantityTypeIdentifierActiveEnergyBurned':
                        monthly_data[month_key]['calories'] += float(value)
                    
                    elif record_type == 'HKQuantityTypeIdentifierStepCount':
                        monthly_data[month_key]['steps'] += float(value)
                    
                    elif record_type == 'HKQuantityTypeIdentifierBloodPressureSystolic':
                        monthly_data[month_key]['bp_systolic'].append(float(value))
                    
                    elif record_type == 'HKQuantityTypeIdentifierBloodPressureDiastolic':
                        monthly_data[month_key]['bp_diastolic'].append(float(value))
                    
                    monthly_data[month_key]['record_count'] += 1
                    
                except Exception as e:
                    pass  # Skip problematic records
            
            # Clear the element to save memory
            elem.clear()
            root.clear()
            
            record_count += 1
            if record_count % 50000 == 0:
                print(f"  Processed {record_count:,} records...")
                gc.collect()
    
    print(f"Total records processed: {record_count:,}")
    
    # Convert to DataFrame
    processed_data = []
    for month, values in monthly_data.items():
        # Calculate days in month for averaging
        year, month_num = map(int, month.split('-'))
        days_in_month = pd.Period(f'{year}-{month_num}').days_in_month
        
        row = {
            'month': pd.to_datetime(f'{month}-01'),
            'hr_avg': np.mean(values['hr_values']) if values['hr_values'] else np.nan,
            'hr_count': len(values['hr_values']),
            'hrv_avg': np.mean(values['hrv_values']) if values['hrv_values'] else np.nan,
            'hrv_count': len(values['hrv_values']),
            'o2_avg': np.mean(values['o2_values']) if values['o2_values'] else np.nan,
            'o2_min': np.min(values['o2_values']) if values['o2_values'] else np.nan,
            'o2_count': len(values['o2_values']),
            'sleep_avg_hours': (values['sleep_minutes'] / 60 / days_in_month) if values['sleep_minutes'] > 0 else np.nan,
            'calories_daily_avg': values['calories'] / days_in_month,
            'steps_daily_avg': values['steps'] / days_in_month,
            'bp_systolic_avg': np.mean(values['bp_systolic']) if values['bp_systolic'] else np.nan,
            'bp_diastolic_avg': np.mean(values['bp_diastolic']) if values['bp_diastolic'] else np.nan,
            'total_records': values['record_count']
        }
        processed_data.append(row)
    
    df = pd.DataFrame(processed_data).sort_values('month')
    
    # Calculate year-over-year trends
    df['year'] = df['month'].dt.year
    
    return df

def create_historical_analysis_charts(df):
    """Create comprehensive charts for all historical data"""
    
    # Set up the figure
    fig = plt.figure(figsize=(20, 24))
    
    # Define color scheme
    colors = {
        'hr': '#E74C3C',
        'hrv': '#3498DB',
        'o2': '#2ECC71',
        'sleep': '#9B59B6',
        'activity': '#F39C12',
        'bp': '#E67E22'
    }
    
    # 1. Resting Heart Rate Trend
    ax1 = plt.subplot(6, 1, 1)
    hr_data = df.dropna(subset=['hr_avg'])
    if not hr_data.empty:
        ax1.plot(hr_data['month'], hr_data['hr_avg'], color=colors['hr'], linewidth=2, marker='o', markersize=4)
        ax1.fill_between(hr_data['month'], hr_data['hr_avg'], alpha=0.3, color=colors['hr'])
        ax1.set_ylabel('Avg Resting HR (BPM)')
        ax1.set_title('Resting Heart Rate - Full History', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # Add trend line
        z = np.polyfit(range(len(hr_data)), hr_data['hr_avg'], 1)
        p = np.poly1d(z)
        ax1.plot(hr_data['month'], p(range(len(hr_data))), "--", color='darkred', alpha=0.8, label=f'Trend: {z[0]:.2f} BPM/month')
        ax1.legend()
    
    # 2. Heart Rate Variability Trend
    ax2 = plt.subplot(6, 1, 2)
    hrv_data = df.dropna(subset=['hrv_avg'])
    if not hrv_data.empty:
        ax2.plot(hrv_data['month'], hrv_data['hrv_avg'], color=colors['hrv'], linewidth=2, marker='o', markersize=4)
        ax2.fill_between(hrv_data['month'], hrv_data['hrv_avg'], alpha=0.3, color=colors['hrv'])
        ax2.set_ylabel('Avg HRV (ms)')
        ax2.set_title('Heart Rate Variability - Full History', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        # Add trend line
        z = np.polyfit(range(len(hrv_data)), hrv_data['hrv_avg'], 1)
        p = np.poly1d(z)
        ax2.plot(hrv_data['month'], p(range(len(hrv_data))), "--", color='darkblue', alpha=0.8, label=f'Trend: {z[0]:.2f} ms/month')
        ax2.legend()
    
    # 3. Oxygen Saturation
    ax3 = plt.subplot(6, 1, 3)
    o2_data = df.dropna(subset=['o2_avg'])
    if not o2_data.empty:
        ax3.plot(o2_data['month'], o2_data['o2_avg'], color=colors['o2'], linewidth=2, marker='o', markersize=4, label='Average')
        ax3.plot(o2_data['month'], o2_data['o2_min'], color='red', linewidth=1, marker='v', markersize=3, alpha=0.6, label='Minimum')
        ax3.axhline(y=95, color='red', linestyle='--', alpha=0.5, label='Low O2 Threshold')
        ax3.set_ylabel('SpO2 (%)')
        ax3.set_ylim(80, 101)
        ax3.set_title('Oxygen Saturation - Full History', fontsize=14, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        ax3.legend()
    
    # 4. Sleep Patterns
    ax4 = plt.subplot(6, 1, 4)
    sleep_data = df.dropna(subset=['sleep_avg_hours'])
    if not sleep_data.empty:
        # Cap unrealistic values
        sleep_data['sleep_avg_hours'] = sleep_data['sleep_avg_hours'].clip(upper=12)
        ax4.bar(sleep_data['month'], sleep_data['sleep_avg_hours'], color=colors['sleep'], alpha=0.7, width=20)
        ax4.axhline(y=8, color='green', linestyle='--', alpha=0.5, label='Recommended 8 hours')
        ax4.set_ylabel('Avg Hours/Night')
        ax4.set_title('Sleep Duration - Full History', fontsize=14, fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='y')
        ax4.legend()
    
    # 5. Activity Metrics
    ax5 = plt.subplot(6, 1, 5)
    activity_data = df.dropna(subset=['calories_daily_avg'])
    if not activity_data.empty:
        ax5_twin = ax5.twinx()
        
        # Calories on primary axis
        l1 = ax5.plot(activity_data['month'], activity_data['calories_daily_avg'], 
                      color=colors['activity'], linewidth=2, marker='o', markersize=4, label='Calories')
        ax5.set_ylabel('Daily Calories', color=colors['activity'])
        ax5.tick_params(axis='y', labelcolor=colors['activity'])
        
        # Steps on secondary axis
        l2 = ax5_twin.plot(activity_data['month'], activity_data['steps_daily_avg'], 
                           color='purple', linewidth=2, marker='s', markersize=4, label='Steps')
        ax5_twin.set_ylabel('Daily Steps', color='purple')
        ax5_twin.tick_params(axis='y', labelcolor='purple')
        
        ax5.set_title('Activity Metrics - Full History', fontsize=14, fontweight='bold')
        ax5.grid(True, alpha=0.3)
        
        # Combine legends
        lns = l1 + l2
        labs = [l.get_label() for l in lns]
        ax5.legend(lns, labs, loc='upper left')
    
    # 6. Yearly Summary Statistics
    ax6 = plt.subplot(6, 1, 6)
    ax6.axis('off')
    
    # Calculate yearly averages
    yearly_stats = df.groupby('year').agg({
        'hr_avg': 'mean',
        'hrv_avg': 'mean',
        'o2_avg': 'mean',
        'sleep_avg_hours': 'mean',
        'calories_daily_avg': 'mean',
        'steps_daily_avg': 'mean'
    }).round(1)
    
    # Create summary text
    summary_text = "YEARLY AVERAGES\n\n"
    summary_text += yearly_stats.to_string()
    
    ax6.text(0.1, 0.9, summary_text, transform=ax6.transAxes,
             fontsize=12, verticalalignment='top',
             fontfamily='monospace',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgray', alpha=0.5))
    
    # Format x-axis for all plots
    for ax in [ax1, ax2, ax3, ax4, ax5]:
        if ax.has_data():
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    # Main title
    first_date = df['month'].min().strftime('%Y-%m')
    last_date = df['month'].max().strftime('%Y-%m')
    fig.suptitle(f'Complete Health History Analysis ({first_date} to {last_date})', 
                 fontsize=20, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('complete_historical_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("\nHistorical analysis chart saved as 'complete_historical_analysis.png'")
    
    return yearly_stats

def generate_comprehensive_insights(df, yearly_stats):
    """Generate insights from all historical data"""
    
    print("\n" + "="*60)
    print("COMPREHENSIVE HEALTH INSIGHTS - FULL HISTORY")
    print("="*60)
    
    # Date range
    first_date = df['month'].min()
    last_date = df['month'].max()
    total_months = len(df)
    
    print(f"\nData Range: {first_date.strftime('%B %Y')} to {last_date.strftime('%B %Y')}")
    print(f"Total Period: {total_months} months ({total_months/12:.1f} years)")
    
    # 1. Long-term trends
    print("\n1. LONG-TERM TRENDS:")
    
    # Heart Rate Trend
    hr_data = df.dropna(subset=['hr_avg'])
    if len(hr_data) > 12:
        hr_first_year = hr_data.head(12)['hr_avg'].mean()
        hr_last_year = hr_data.tail(12)['hr_avg'].mean()
        hr_change = hr_last_year - hr_first_year
        print(f"   • Resting HR: {hr_change:+.1f} BPM change (First year: {hr_first_year:.1f}, Last year: {hr_last_year:.1f})")
        if hr_change < 0:
            print("     ✓ Improvement in cardiovascular fitness")
        elif hr_change > 5:
            print("     ⚠ Consider cardiovascular health check")
    
    # HRV Trend
    hrv_data = df.dropna(subset=['hrv_avg'])
    if len(hrv_data) > 12:
        hrv_first_year = hrv_data.head(12)['hrv_avg'].mean()
        hrv_last_year = hrv_data.tail(12)['hrv_avg'].mean()
        hrv_change = hrv_last_year - hrv_first_year
        print(f"   • HRV: {hrv_change:+.1f} ms change (First year: {hrv_first_year:.1f}, Last year: {hrv_last_year:.1f})")
        if hrv_change > 0:
            print("     ✓ Improved stress resilience and recovery")
        elif hrv_change < -5:
            print("     ⚠ May indicate increased stress or reduced recovery")
    
    # 2. Health milestones
    print("\n2. HEALTH MILESTONES:")
    
    # Best/Worst months
    if 'hr_avg' in df.columns:
        best_hr_month = df.loc[df['hr_avg'].idxmin(), 'month']
        print(f"   • Lowest Resting HR: {df['hr_avg'].min():.1f} BPM in {best_hr_month.strftime('%B %Y')}")
    
    if 'hrv_avg' in df.columns:
        best_hrv_month = df.loc[df['hrv_avg'].idxmax(), 'month']
        print(f"   • Highest HRV: {df['hrv_avg'].max():.1f} ms in {best_hrv_month.strftime('%B %Y')}")
    
    if 'steps_daily_avg' in df.columns:
        best_steps_month = df.loc[df['steps_daily_avg'].idxmax(), 'month']
        print(f"   • Most Active Month: {df['steps_daily_avg'].max():.0f} steps/day in {best_steps_month.strftime('%B %Y')}")
    
    # 3. Concerning patterns
    print("\n3. AREAS OF CONCERN:")
    
    # Oxygen saturation
    o2_data = df.dropna(subset=['o2_min'])
    if not o2_data.empty:
        low_o2_months = (o2_data['o2_min'] < 90).sum()
        if low_o2_months > 0:
            print(f"   ⚠ {low_o2_months} months with oxygen readings below 90%")
            print("     → Recommend sleep study or pulmonary evaluation")
    
    # Sleep duration
    sleep_data = df.dropna(subset=['sleep_avg_hours'])
    if not sleep_data.empty:
        poor_sleep_months = (sleep_data['sleep_avg_hours'] < 6).sum()
        if poor_sleep_months > 0:
            print(f"   ⚠ {poor_sleep_months} months with average sleep < 6 hours")
    
    # 4. Year-over-year comparison
    print("\n4. YEAR-OVER-YEAR SUMMARY:")
    if not yearly_stats.empty:
        print("\n" + yearly_stats.to_string())
    
    # 5. Recommendations
    print("\n5. PERSONALIZED RECOMMENDATIONS:")
    
    recommendations = []
    
    # Based on trends
    if 'hr_change' in locals() and hr_change > 5:
        recommendations.append("• Focus on cardiovascular exercise to reduce resting heart rate")
    
    if 'hrv_change' in locals() and hrv_change < -5:
        recommendations.append("• Implement stress management techniques (meditation, yoga)")
    
    # Based on recent data
    recent_data = df.tail(6)  # Last 6 months
    
    if not recent_data['o2_avg'].isna().all() and recent_data['o2_avg'].mean() < 95:
        recommendations.append("• Address oxygen saturation issues - consider sleep position, weight management")
    
    if not recent_data['sleep_avg_hours'].isna().all() and recent_data['sleep_avg_hours'].mean() < 7:
        recommendations.append("• Prioritize sleep hygiene - aim for 7-9 hours consistently")
    
    if not recent_data['steps_daily_avg'].isna().all() and recent_data['steps_daily_avg'].mean() < 5000:
        recommendations.append("• Increase daily movement - target 8,000+ steps per day")
    
    if recommendations:
        for rec in recommendations:
            print(rec)
    else:
        print("   ✓ Overall health metrics are within healthy ranges!")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    # Parse ALL historical data
    print("Analyzing complete health history...")
    print("This will take a few minutes due to the large file size...\n")
    
    df = parse_all_health_data_efficiently('輸出.xml')
    
    print(f"\nSuccessfully processed data from {df['month'].min().strftime('%Y-%m')} to {df['month'].max().strftime('%Y-%m')}")
    print(f"Total months of data: {len(df)}")
    
    # Create visualizations
    print("\nGenerating comprehensive charts...")
    yearly_stats = create_historical_analysis_charts(df)
    
    # Generate insights
    generate_comprehensive_insights(df, yearly_stats)
    
    # Save processed data for future use
    df.to_csv('monthly_health_summary.csv', index=False)
    print("\nMonthly summary data saved to 'monthly_health_summary.csv'")