"""
Example usage of the Apple Health Data Analysis scripts

This script demonstrates how to use the analysis tools with your own data.
"""

import sys
import argparse
from config import DEFAULT_EXPORT_FILE

def main():
    parser = argparse.ArgumentParser(description='Analyze Apple Health data')
    parser.add_argument('--input', '-i', default=DEFAULT_EXPORT_FILE,
                        help=f'Input XML file (default: {DEFAULT_EXPORT_FILE})')
    parser.add_argument('--analysis', '-a', required=True,
                        choices=['sleep', 'oxygen', 'hrv', 'blood_pressure', 'activity', 'all'],
                        help='Type of analysis to perform')
    
    args = parser.parse_args()
    
    print(f"Analyzing {args.input} for {args.analysis} data...")
    
    # Import and run the appropriate analysis
    if args.analysis == 'sleep':
        from analyze_sleep_patterns import parse_sleep_data, analyze_sleep_patterns, plot_sleep_patterns
        df = parse_sleep_data(args.input)
        daily_sleep = analyze_sleep_patterns(df)
        plot_sleep_patterns(daily_sleep)
        
    elif args.analysis == 'oxygen':
        from analyze_oxygen_saturation import parse_oxygen_data, analyze_oxygen_saturation, plot_oxygen_saturation
        df = parse_oxygen_data(args.input)
        daily_avg = analyze_oxygen_saturation(df)
        plot_oxygen_saturation(daily_avg)
        
    elif args.analysis == 'hrv':
        from analyze_hrv import parse_hrv_data, analyze_hrv, plot_hrv
        df = parse_hrv_data(args.input)
        daily_avg = analyze_hrv(df)
        plot_hrv(daily_avg)
        
    elif args.analysis == 'blood_pressure':
        from analyze_blood_pressure import parse_blood_pressure_data, analyze_blood_pressure, plot_blood_pressure
        df = parse_blood_pressure_data(args.input)
        df = analyze_blood_pressure(df)
        plot_blood_pressure(df)
        
    elif args.analysis == 'activity':
        from analyze_activity_energy import parse_activity_data, analyze_activity, plot_activity
        df = parse_activity_data(args.input)
        daily_activity = analyze_activity(df)
        plot_activity(daily_activity)
        
    elif args.analysis == 'all':
        print("Running all analyses...")
        # Run all analyses
        analyses = ['sleep', 'oxygen', 'hrv', 'blood_pressure', 'activity']
        for analysis_type in analyses:
            print(f"\nRunning {analysis_type} analysis...")
            try:
                # Recursive call with specific analysis
                sys.argv = [sys.argv[0], '--input', args.input, '--analysis', analysis_type]
                main()
            except Exception as e:
                print(f"Error in {analysis_type} analysis: {e}")
                continue
    
    print(f"\nAnalysis complete! Check the generated PNG files for visualizations.")

if __name__ == "__main__":
    main()