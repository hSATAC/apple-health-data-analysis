import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime
import sys

def extract_key_statistics(xml_file, sample_rate=10):
    """Extract key statistics with sampling for faster processing"""
    
    print(f"Extracting statistics from {xml_file}...")
    print(f"Using sampling rate: 1/{sample_rate} records")
    
    # Statistics collectors
    stats = {
        'total_records': 0,
        'date_range': {'min': None, 'max': None},
        'hr_stats': {'count': 0, 'sum': 0, 'min': float('inf'), 'max': 0},
        'hrv_stats': {'count': 0, 'sum': 0, 'min': float('inf'), 'max': 0},
        'o2_stats': {'count': 0, 'sum': 0, 'min': float('inf'), 'max': 0, 'below_95': 0},
        'sleep_total_hours': 0,
        'calories_total': 0,
        'steps_total': 0,
        'bp_systolic': {'count': 0, 'sum': 0, 'above_140': 0},
        'bp_diastolic': {'count': 0, 'sum': 0, 'above_90': 0}
    }
    
    yearly_counts = defaultdict(lambda: defaultdict(int))
    
    # Parse with iterparse
    context = ET.iterparse(xml_file, events=('start', 'end'))
    context = iter(context)
    event, root = next(context)
    
    record_num = 0
    
    for event, elem in context:
        if event == 'end' and elem.tag == 'Record':
            record_num += 1
            
            # Sample records for faster processing
            if record_num % sample_rate != 0:
                elem.clear()
                root.clear()
                continue
            
            record_type = elem.get('type')
            date_str = elem.get('startDate')
            value_str = elem.get('value')
            
            if date_str and value_str:
                try:
                    date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    value = float(value_str)
                    year = date.year
                    
                    # Update date range
                    if stats['date_range']['min'] is None or date < stats['date_range']['min']:
                        stats['date_range']['min'] = date
                    if stats['date_range']['max'] is None or date > stats['date_range']['max']:
                        stats['date_range']['max'] = date
                    
                    # Process by type
                    if record_type == 'HKQuantityTypeIdentifierRestingHeartRate':
                        stats['hr_stats']['count'] += 1
                        stats['hr_stats']['sum'] += value
                        stats['hr_stats']['min'] = min(stats['hr_stats']['min'], value)
                        stats['hr_stats']['max'] = max(stats['hr_stats']['max'], value)
                        yearly_counts[year]['hr'] += 1
                    
                    elif record_type == 'HKQuantityTypeIdentifierHeartRateVariabilitySDNN':
                        stats['hrv_stats']['count'] += 1
                        stats['hrv_stats']['sum'] += value
                        stats['hrv_stats']['min'] = min(stats['hrv_stats']['min'], value)
                        stats['hrv_stats']['max'] = max(stats['hrv_stats']['max'], value)
                        yearly_counts[year]['hrv'] += 1
                    
                    elif record_type == 'HKQuantityTypeIdentifierOxygenSaturation':
                        o2_value = value * 100
                        stats['o2_stats']['count'] += 1
                        stats['o2_stats']['sum'] += o2_value
                        stats['o2_stats']['min'] = min(stats['o2_stats']['min'], o2_value)
                        stats['o2_stats']['max'] = max(stats['o2_stats']['max'], o2_value)
                        if o2_value < 95:
                            stats['o2_stats']['below_95'] += 1
                        yearly_counts[year]['o2'] += 1
                    
                    elif record_type == 'HKCategoryTypeIdentifierSleepAnalysis':
                        end_str = elem.get('endDate')
                        if end_str:
                            end_date = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
                            hours = (end_date - date).total_seconds() / 3600
                            if 0 < hours < 24:
                                stats['sleep_total_hours'] += hours
                                yearly_counts[year]['sleep'] += 1
                    
                    elif record_type == 'HKQuantityTypeIdentifierActiveEnergyBurned':
                        stats['calories_total'] += value
                        yearly_counts[year]['calories'] += 1
                    
                    elif record_type == 'HKQuantityTypeIdentifierStepCount':
                        stats['steps_total'] += value
                        yearly_counts[year]['steps'] += 1
                    
                    elif record_type == 'HKQuantityTypeIdentifierBloodPressureSystolic':
                        stats['bp_systolic']['count'] += 1
                        stats['bp_systolic']['sum'] += value
                        if value >= 140:
                            stats['bp_systolic']['above_140'] += 1
                    
                    elif record_type == 'HKQuantityTypeIdentifierBloodPressureDiastolic':
                        stats['bp_diastolic']['count'] += 1
                        stats['bp_diastolic']['sum'] += value
                        if value >= 90:
                            stats['bp_diastolic']['above_90'] += 1
                    
                except Exception as e:
                    pass
            
            # Update progress
            if record_num % 100000 == 0:
                print(f"  Processed {record_num:,} records...")
                sys.stdout.flush()
            
            elem.clear()
            root.clear()
            stats['total_records'] = record_num
    
    # Adjust counts for sampling
    for key in stats:
        if isinstance(stats[key], dict) and 'count' in stats[key]:
            stats[key]['count'] *= sample_rate
            stats[key]['sum'] *= sample_rate
    
    stats['total_records'] = record_num
    stats['sleep_total_hours'] *= sample_rate
    stats['calories_total'] *= sample_rate
    stats['steps_total'] *= sample_rate
    
    return stats, yearly_counts

def print_statistics_report(stats, yearly_counts, sample_rate):
    """Print a formatted report of the statistics"""
    
    print("\n" + "="*60)
    print("APPLE HEALTH DATA - COMPLETE HISTORICAL ANALYSIS")
    print("="*60)
    
    # Date range
    if stats['date_range']['min'] and stats['date_range']['max']:
        start_date = stats['date_range']['min'].strftime('%Y-%m-%d')
        end_date = stats['date_range']['max'].strftime('%Y-%m-%d')
        total_days = (stats['date_range']['max'] - stats['date_range']['min']).days
        print(f"\nData Period: {start_date} to {end_date} ({total_days:,} days)")
    
    print(f"Total Records Processed: {stats['total_records']:,} (sampled)")
    print(f"Estimated Total Records: {stats['total_records'] * sample_rate:,}")
    
    # Heart Rate Statistics
    print("\n1. RESTING HEART RATE:")
    if stats['hr_stats']['count'] > 0:
        avg_hr = stats['hr_stats']['sum'] / stats['hr_stats']['count']
        print(f"   • Average: {avg_hr:.1f} BPM")
        print(f"   • Range: {stats['hr_stats']['min']:.0f} - {stats['hr_stats']['max']:.0f} BPM")
        print(f"   • Total measurements: ~{stats['hr_stats']['count']:,}")
    
    # HRV Statistics
    print("\n2. HEART RATE VARIABILITY:")
    if stats['hrv_stats']['count'] > 0:
        avg_hrv = stats['hrv_stats']['sum'] / stats['hrv_stats']['count']
        print(f"   • Average: {avg_hrv:.1f} ms")
        print(f"   • Range: {stats['hrv_stats']['min']:.0f} - {stats['hrv_stats']['max']:.0f} ms")
        print(f"   • Total measurements: ~{stats['hrv_stats']['count']:,}")
    
    # Oxygen Saturation
    print("\n3. OXYGEN SATURATION:")
    if stats['o2_stats']['count'] > 0:
        avg_o2 = stats['o2_stats']['sum'] / stats['o2_stats']['count']
        below_95_pct = (stats['o2_stats']['below_95'] / stats['o2_stats']['count']) * 100
        print(f"   • Average: {avg_o2:.1f}%")
        print(f"   • Range: {stats['o2_stats']['min']:.0f}% - {stats['o2_stats']['max']:.0f}%")
        print(f"   • Below 95%: {below_95_pct:.1f}% of readings")
        if stats['o2_stats']['min'] < 90:
            print(f"   ⚠ WARNING: Minimum O2 of {stats['o2_stats']['min']:.0f}% recorded")
    
    # Sleep Statistics
    print("\n4. SLEEP PATTERNS:")
    if stats['sleep_total_hours'] > 0 and total_days > 0:
        avg_sleep = stats['sleep_total_hours'] / total_days
        print(f"   • Estimated average: {avg_sleep:.1f} hours/night")
        print(f"   • Total tracked sleep: ~{stats['sleep_total_hours']:,.0f} hours")
    
    # Activity Statistics
    print("\n5. ACTIVITY METRICS:")
    if total_days > 0:
        avg_calories = stats['calories_total'] / total_days
        avg_steps = stats['steps_total'] / total_days
        print(f"   • Average calories: {avg_calories:.0f} kcal/day")
        print(f"   • Average steps: {avg_steps:.0f} steps/day")
    
    # Blood Pressure
    print("\n6. BLOOD PRESSURE:")
    if stats['bp_systolic']['count'] > 0:
        avg_systolic = stats['bp_systolic']['sum'] / stats['bp_systolic']['count']
        avg_diastolic = stats['bp_diastolic']['sum'] / stats['bp_diastolic']['count']
        high_bp_pct = (stats['bp_systolic']['above_140'] / stats['bp_systolic']['count']) * 100
        print(f"   • Average: {avg_systolic:.0f}/{avg_diastolic:.0f} mmHg")
        print(f"   • Readings ≥140/90: {high_bp_pct:.1f}%")
    
    # Yearly Distribution
    print("\n7. YEARLY DATA DISTRIBUTION:")
    years = sorted(yearly_counts.keys())
    for year in years:
        counts = yearly_counts[year]
        print(f"   {year}: HR={counts.get('hr', 0)*sample_rate:,}, "
              f"HRV={counts.get('hrv', 0)*sample_rate:,}, "
              f"O2={counts.get('o2', 0)*sample_rate:,}, "
              f"Sleep={counts.get('sleep', 0)*sample_rate:,}")
    
    # Key Insights
    print("\n8. KEY INSIGHTS:")
    
    insights = []
    
    if stats['hr_stats']['count'] > 0 and avg_hr < 60:
        insights.append("✓ Excellent resting heart rate (<60 BPM)")
    elif stats['hr_stats']['count'] > 0 and avg_hr > 75:
        insights.append("⚠ Elevated resting heart rate (>75 BPM)")
    
    if stats['hrv_stats']['count'] > 0 and avg_hrv > 30:
        insights.append("✓ Good heart rate variability (>30 ms)")
    elif stats['hrv_stats']['count'] > 0 and avg_hrv < 20:
        insights.append("⚠ Low heart rate variability (<20 ms)")
    
    if stats['o2_stats']['count'] > 0 and below_95_pct > 10:
        insights.append("⚠ Frequent low oxygen readings (>10% below 95%)")
    
    if 'avg_sleep' in locals() and avg_sleep < 7:
        insights.append("⚠ Below recommended sleep duration (<7 hours)")
    
    if 'avg_steps' in locals() and avg_steps < 5000:
        insights.append("⚠ Low daily step count (<5000)")
    elif 'avg_steps' in locals() and avg_steps > 10000:
        insights.append("✓ Excellent daily step count (>10000)")
    
    for insight in insights:
        print(f"   {insight}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    # Use sampling for faster processing (1 out of every 10 records)
    sample_rate = 10
    
    stats, yearly_counts = extract_key_statistics('輸出.xml', sample_rate=sample_rate)
    print_statistics_report(stats, yearly_counts, sample_rate)