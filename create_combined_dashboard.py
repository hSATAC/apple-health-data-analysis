import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib.image as mpimg
import os

def create_combined_dashboard():
    """Combine existing charts into one comprehensive dashboard"""
    
    # List of generated charts
    charts = [
        ('sleep_patterns_analysis.png', 'Sleep Patterns'),
        ('oxygen_saturation_analysis.png', 'Oxygen Saturation'),
        ('hrv_analysis.png', 'Heart Rate Variability'),
        ('activity_energy_analysis.png', 'Activity & Energy'),
        ('heart_rate_chart.png', 'Resting Heart Rate')
    ]
    
    # Check which charts exist
    existing_charts = []
    for chart_file, title in charts:
        if os.path.exists(chart_file):
            existing_charts.append((chart_file, title))
            print(f"Found: {chart_file}")
        else:
            print(f"Missing: {chart_file}")
    
    if not existing_charts:
        print("No charts found to combine!")
        return
    
    # Create figure with subplots
    n_charts = len(existing_charts)
    cols = 2
    rows = (n_charts + 1) // 2
    
    fig = plt.figure(figsize=(20, rows * 6))
    
    # Add main title
    fig.suptitle('Comprehensive Health Dashboard - All Metrics', fontsize=24, fontweight='bold', y=0.98)
    
    # Create subplots for each chart
    for idx, (chart_file, title) in enumerate(existing_charts):
        ax = plt.subplot(rows, cols, idx + 1)
        
        # Read and display the image
        img = mpimg.imread(chart_file)
        ax.imshow(img)
        ax.axis('off')
        ax.set_title(title, fontsize=16, pad=10)
    
    # Adjust layout
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    # Save the combined dashboard
    plt.savefig('comprehensive_health_dashboard_combined.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("\nCombined dashboard saved as 'comprehensive_health_dashboard_combined.png'")

if __name__ == "__main__":
    create_combined_dashboard()