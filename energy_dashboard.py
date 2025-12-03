"""
Campus Energy-Use Dashboard - Capstone Project
Complete solution with all tasks implemented
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import os
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# TASK 3: Object-Oriented Modeling
# ============================================================================

class MeterReading:
    """Represents a single meter reading with timestamp and consumption"""
    
    def __init__(self, timestamp, kwh):
        self.timestamp = pd.to_datetime(timestamp)
        self.kwh = float(kwh)
    
    def __repr__(self):
        return f"MeterReading({self.timestamp}, {self.kwh} kWh)"


class Building:
    """Represents a building with its meter readings"""
    
    def __init__(self, name):
        self.name = name
        self.meter_readings = []
    
    def add_reading(self, timestamp, kwh):
        """Add a meter reading to the building"""
        reading = MeterReading(timestamp, kwh)
        self.meter_readings.append(reading)
    
    def calculate_total_consumption(self):
        """Calculate total energy consumption"""
        return sum(reading.kwh for reading in self.meter_readings)
    
    def calculate_average_consumption(self):
        """Calculate average energy consumption"""
        if not self.meter_readings:
            return 0
        return self.calculate_total_consumption() / len(self.meter_readings)
    
    def get_peak_consumption(self):
        """Get the peak consumption reading"""
        if not self.meter_readings:
            return None
        return max(self.meter_readings, key=lambda r: r.kwh)
    
    def generate_report(self):
        """Generate a summary report for the building"""
        if not self.meter_readings:
            return f"No data available for {self.name}"
        
        total = self.calculate_total_consumption()
        avg = self.calculate_average_consumption()
        peak = self.get_peak_consumption()
        min_reading = min(self.meter_readings, key=lambda r: r.kwh)
        
        report = f"""
Building Report: {self.name}
{'=' * 50}
Total Readings: {len(self.meter_readings)}
Total Consumption: {total:.2f} kWh
Average Consumption: {avg:.2f} kWh
Peak Consumption: {peak.kwh:.2f} kWh at {peak.timestamp}
Minimum Consumption: {min_reading.kwh:.2f} kWh at {min_reading.timestamp}
"""
        return report


class BuildingManager:
    """Manages multiple buildings and their data"""
    
    def __init__(self):
        self.buildings = {}
    
    def add_building(self, building):
        """Add a building to the manager"""
        self.buildings[building.name] = building
    
    def get_building(self, name):
        """Get a building by name"""
        return self.buildings.get(name)
    
    def get_all_buildings(self):
        """Get all buildings"""
        return list(self.buildings.values())
    
    def generate_campus_report(self):
        """Generate a report for all buildings"""
        total_campus = sum(b.calculate_total_consumption() for b in self.buildings.values())
        
        report = f"""
Campus-Wide Energy Report
{'=' * 50}
Total Buildings: {len(self.buildings)}
Total Campus Consumption: {total_campus:.2f} kWh

Building Breakdown:
"""
        for building in self.buildings.values():
            consumption = building.calculate_total_consumption()
            percentage = (consumption / total_campus * 100) if total_campus > 0 else 0
            report += f"  - {building.name}: {consumption:.2f} kWh ({percentage:.1f}%)\n"
        
        return report


# ============================================================================
# TASK 1: Data Ingestion and Validation
# ============================================================================

def create_sample_data(data_dir='data'):
    """Create sample CSV files for testing"""
    Path(data_dir).mkdir(exist_ok=True)
    
    buildings = ['Library', 'Engineering_Block', 'Admin_Building', 'Sports_Complex']
    
    # Generate data for the past 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    dates = pd.date_range(start=start_date, end=end_date, freq='H')
    
    for building in buildings:
        # Generate realistic consumption patterns
        base_load = np.random.randint(50, 150)
        
        data = []
        for date in dates:
            # Add variation based on time of day
            hour = date.hour
            if 6 <= hour <= 22:  # Peak hours
                consumption = base_load + np.random.normal(30, 10)
            else:  # Off-peak
                consumption = base_load + np.random.normal(10, 5)
            
            consumption = max(0, consumption)  # Ensure non-negative
            data.append({'timestamp': date, 'kwh': consumption})
        
        df = pd.DataFrame(data)
        df.to_csv(f'{data_dir}/{building}.csv', index=False)
    
    print(f"Sample data created in '{data_dir}/' directory")


def ingest_data(data_dir='data'):
    """
    Read and validate multiple CSV files from the data directory
    Returns a combined DataFrame with all building data
    """
    data_path = Path(data_dir)
    
    if not data_path.exists():
        print(f"Data directory '{data_dir}' not found. Creating sample data...")
        create_sample_data(data_dir)
    
    combined_data = []
    failed_files = []
    
    # Find all CSV files
    csv_files = list(data_path.glob('*.csv'))
    
    if not csv_files:
        print(f"No CSV files found in '{data_dir}'. Creating sample data...")
        create_sample_data(data_dir)
        csv_files = list(data_path.glob('*.csv'))
    
    print(f"Found {len(csv_files)} CSV files to process...")
    
    for file_path in csv_files:
        try:
            # Extract building name from filename
            building_name = file_path.stem
            
            # Read CSV with error handling
            df = pd.read_csv(file_path, on_bad_lines='skip')
            
            # Validate required columns
            if 'timestamp' not in df.columns or 'kwh' not in df.columns:
                print(f"Warning: {file_path.name} missing required columns. Skipping...")
                failed_files.append(file_path.name)
                continue
            
            # Add building name if not present
            df['building'] = building_name
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            
            # Remove rows with invalid data
            df = df.dropna(subset=['timestamp', 'kwh'])
            
            # Ensure kwh is numeric
            df['kwh'] = pd.to_numeric(df['kwh'], errors='coerce')
            df = df.dropna(subset=['kwh'])
            
            combined_data.append(df)
            print(f"✓ Successfully loaded: {file_path.name} ({len(df)} records)")
            
        except FileNotFoundError:
            print(f"Error: File not found - {file_path.name}")
            failed_files.append(file_path.name)
        except Exception as e:
            print(f"Error processing {file_path.name}: {str(e)}")
            failed_files.append(file_path.name)
    
    if combined_data:
        df_combined = pd.concat(combined_data, ignore_index=True)
        df_combined = df_combined.sort_values('timestamp').reset_index(drop=True)
        print(f"\n✓ Total records loaded: {len(df_combined)}")
        return df_combined, failed_files
    else:
        print("No valid data loaded!")
        return None, failed_files


# ============================================================================
# TASK 2: Core Aggregation Logic
# ============================================================================

def calculate_daily_totals(df):
    """Calculate daily total consumption for each building"""
    df['date'] = df['timestamp'].dt.date
    daily_totals = df.groupby(['date', 'building'])['kwh'].sum().reset_index()
    daily_totals.columns = ['date', 'building', 'total_kwh']
    return daily_totals


def calculate_weekly_aggregates(df):
    """Calculate weekly aggregate statistics"""
    df_copy = df.copy()
    df_copy.set_index('timestamp', inplace=True)
    
    # Fixed for Pandas compatibility
    weekly_agg = df_copy.groupby('building')['kwh'].resample('W').agg(
        total='sum',
        mean='mean',
        max='max',
        min='min'
    ).reset_index()
    
    return weekly_agg


def building_wise_summary(df):
    """Generate summary statistics for each building"""
    summary = df.groupby('building')['kwh'].agg([
        ('total_kwh', 'sum'),
        ('mean_kwh', 'mean'),
        ('max_kwh', 'max'),
        ('min_kwh', 'min'),
        ('readings_count', 'count')
    ]).reset_index()
    
    return summary


def find_peak_hours(df):
    """Find peak consumption hours for each building"""
    df['hour'] = df['timestamp'].dt.hour
    peak_hours = df.groupby(['building', 'hour'])['kwh'].mean().reset_index()
    peak_by_building = peak_hours.loc[peak_hours.groupby('building')['kwh'].idxmax()]
    return peak_by_building


# ============================================================================
# TASK 4: Visual Output with Matplotlib
# ============================================================================

def create_dashboard(df, daily_totals, weekly_agg, output_dir='output'):
    """Create a comprehensive dashboard with multiple visualizations"""
    Path(output_dir).mkdir(exist_ok=True)
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Campus Energy Consumption Dashboard', fontsize=16, fontweight='bold')
    
    # 1. Daily Consumption Trend Line
    ax1 = axes[0, 0]
    for building in daily_totals['building'].unique():
        building_data = daily_totals[daily_totals['building'] == building]
        ax1.plot(building_data['date'], building_data['total_kwh'], 
                marker='o', label=building, linewidth=2)
    
    ax1.set_xlabel('Date', fontweight='bold')
    ax1.set_ylabel('Total Consumption (kWh)', fontweight='bold')
    ax1.set_title('Daily Energy Consumption Trends', fontweight='bold')
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # 2. Bar Chart - Average Weekly Usage
    ax2 = axes[0, 1]
    weekly_avg = weekly_agg.groupby('building')['mean'].mean().reset_index()
    bars = ax2.bar(weekly_avg['building'], weekly_avg['mean'], 
                   color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
    
    ax2.set_xlabel('Building', fontweight='bold')
    ax2.set_ylabel('Average Weekly Consumption (kWh)', fontweight='bold')
    ax2.set_title('Average Weekly Usage Comparison', fontweight='bold')
    ax2.tick_params(axis='x', rotation=45)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}', ha='center', va='bottom')
    
    # 3. Scatter Plot - Peak Hour Consumption
    ax3 = axes[1, 0]
    df['hour'] = df['timestamp'].dt.hour
    
    for building in df['building'].unique():
        building_data = df[df['building'] == building]
        hourly_avg = building_data.groupby('hour')['kwh'].mean()
        ax3.scatter(hourly_avg.index, hourly_avg.values, 
                   label=building, alpha=0.6, s=100)
    
    ax3.set_xlabel('Hour of Day', fontweight='bold')
    ax3.set_ylabel('Average Consumption (kWh)', fontweight='bold')
    ax3.set_title('Hourly Consumption Pattern', fontweight='bold')
    ax3.legend(loc='best')
    ax3.grid(True, alpha=0.3)
    ax3.set_xticks(range(0, 24, 2))
    
    # 4. Pie Chart - Total Consumption Distribution
    ax4 = axes[1, 1]
    building_totals = df.groupby('building')['kwh'].sum()
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    wedges, texts, autotexts = ax4.pie(building_totals.values, 
                                        labels=building_totals.index,
                                        autopct='%1.1f%%',
                                        colors=colors,
                                        startangle=90)
    
    ax4.set_title('Total Energy Consumption Distribution', fontweight='bold')
    
    # Make percentage text more readable
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    plt.tight_layout()
    
    # Save the dashboard
    output_path = Path(output_dir) / 'dashboard.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Dashboard saved to: {output_path}")
    
    plt.close()


# ============================================================================
# TASK 5: Persistence and Executive Summary
# ============================================================================

def export_data(df, building_summary, output_dir='output'):
    """Export cleaned data and summaries to CSV files"""
    Path(output_dir).mkdir(exist_ok=True)
    
    # Export cleaned data
    cleaned_path = Path(output_dir) / 'cleaned_energy_data.csv'
    df.to_csv(cleaned_path, index=False)
    print(f"✓ Cleaned data exported to: {cleaned_path}")
    
    # Export building summary
    summary_path = Path(output_dir) / 'building_summary.csv'
    building_summary.to_csv(summary_path, index=False)
    print(f"✓ Building summary exported to: {summary_path}")


def generate_executive_summary(df, building_summary, peak_hours, manager, output_dir='output'):
    """Generate executive summary report"""
    Path(output_dir).mkdir(exist_ok=True)
    
    # Calculate key metrics
    total_consumption = df['kwh'].sum()
    highest_building = building_summary.loc[building_summary['total_kwh'].idxmax()]
    
    # Find overall peak time
    df['hour'] = df['timestamp'].dt.hour
    overall_peak = df.groupby('hour')['kwh'].mean().idxmax()
    
    # Calculate trends
    df['date'] = df['timestamp'].dt.date
    daily_totals = df.groupby('date')['kwh'].sum()
    first_week_avg = daily_totals.head(7).mean()
    last_week_avg = daily_totals.tail(7).mean()
    trend = ((last_week_avg - first_week_avg) / first_week_avg) * 100
    
    # Generate summary text
    summary = f"""
{'='*70}
CAMPUS ENERGY CONSUMPTION - EXECUTIVE SUMMARY
{'='*70}

Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

KEY FINDINGS:
{'-'*70}

1. TOTAL CAMPUS CONSUMPTION
   Total Energy Used: {total_consumption:,.2f} kWh
   Analysis Period: {df['timestamp'].min().strftime('%Y-%m-%d')} to {df['timestamp'].max().strftime('%Y-%m-%d')}
   Total Buildings Monitored: {df['building'].nunique()}

2. HIGHEST CONSUMING BUILDING
   Building Name: {highest_building['building']}
   Total Consumption: {highest_building['total_kwh']:,.2f} kWh
   Average Hourly: {highest_building['mean_kwh']:.2f} kWh
   Peak Reading: {highest_building['max_kwh']:.2f} kWh

3. PEAK LOAD ANALYSIS
   Campus Peak Hour: {overall_peak}:00 - {overall_peak+1}:00
   
   Building-Specific Peak Hours:
"""
    
    for _, row in peak_hours.iterrows():
        summary += f"   - {row['building']}: {int(row['hour'])}:00 ({row['kwh']:.2f} kWh avg)\n"
    
    summary += f"""
4. CONSUMPTION TRENDS
   First Week Average: {first_week_avg:.2f} kWh/day
   Last Week Average: {last_week_avg:.2f} kWh/day
   Trend: {'+' if trend > 0 else ''}{trend:.1f}%
   
5. BUILDING PERFORMANCE SUMMARY
{'-'*70}
"""
    
    for _, row in building_summary.iterrows():
        summary += f"""
   {row['building']}:
   - Total: {row['total_kwh']:,.2f} kWh
   - Average: {row['mean_kwh']:.2f} kWh/hour
   - Range: {row['min_kwh']:.2f} - {row['max_kwh']:.2f} kWh
"""
    
    summary += f"""
{'='*70}
RECOMMENDATIONS:
{'-'*70}

1. Focus energy-saving initiatives on {highest_building['building']}
2. Implement load-shifting strategies during peak hour ({overall_peak}:00)
3. Investigate {'increasing' if trend > 0 else 'decreasing'} consumption trend
4. Consider demand response programs during peak hours

{'='*70}
"""
    
    # Save to file
    summary_path = Path(output_dir) / 'summary.txt'
    with open(summary_path, 'w') as f:
        f.write(summary)
    
    print(f"✓ Executive summary saved to: {summary_path}")
    
    # Print to console
    print(summary)
    
    return summary


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    print("\n" + "="*70)
    print("CAMPUS ENERGY-USE DASHBOARD - CAPSTONE PROJECT")
    print("="*70 + "\n")
    
    # Task 1: Data Ingestion
    print("TASK 1: Data Ingestion and Validation")
    print("-" * 70)
    df_combined, failed_files = ingest_data('data')
    
    if df_combined is None:
        print("Failed to load data. Exiting...")
        return
    
    if failed_files:
        print(f"\nWarning: {len(failed_files)} files failed to load: {failed_files}")
    
    # Task 2: Core Aggregation Logic
    print("\n" + "="*70)
    print("TASK 2: Core Aggregation Logic")
    print("-" * 70)
    
    daily_totals = calculate_daily_totals(df_combined)
    print(f"✓ Calculated daily totals: {len(daily_totals)} records")
    
    weekly_agg = calculate_weekly_aggregates(df_combined)
    print(f"✓ Calculated weekly aggregates: {len(weekly_agg)} records")
    
    building_summary = building_wise_summary(df_combined)
    print(f"✓ Generated building-wise summary for {len(building_summary)} buildings")
    
    peak_hours = find_peak_hours(df_combined)
    print(f"✓ Identified peak hours for each building")
    
    # Task 3: Object-Oriented Modeling
    print("\n" + "="*70)
    print("TASK 3: Object-Oriented Modeling")
    print("-" * 70)
    
    manager = BuildingManager()
    
    for building_name in df_combined['building'].unique():
        building = Building(building_name)
        building_data = df_combined[df_combined['building'] == building_name]
        
        for _, row in building_data.iterrows():
            building.add_reading(row['timestamp'], row['kwh'])
        
        manager.add_building(building)
        print(f"✓ Created Building object: {building_name}")
    
    # Task 4: Visualization
    print("\n" + "="*70)
    print("TASK 4: Visual Output with Matplotlib")
    print("-" * 70)
    
    create_dashboard(df_combined, daily_totals, weekly_agg)
    
    # Task 5: Persistence and Summary
    print("\n" + "="*70)
    print("TASK 5: Persistence and Executive Summary")
    print("-" * 70)
    
    export_data(df_combined, building_summary)
    generate_executive_summary(df_combined, building_summary, peak_hours, manager)
    
    print("\n" + "="*70)
    print("✓ ALL TASKS COMPLETED SUCCESSFULLY!")
    print("="*70 + "\n")
    
    print("Output files created:")
    print("  - output/dashboard.png (visualization)")
    print("  - output/cleaned_energy_data.csv (processed data)")
    print("  - output/building_summary.csv (statistics)")
    print("  - output/summary.txt (executive report)")


if __name__ == "__main__":
    main()