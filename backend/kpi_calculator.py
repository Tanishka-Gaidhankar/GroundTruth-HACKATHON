import pandas as pd
import numpy as np
from typing import Dict, Tuple, List
from datetime import datetime, timedelta

class KPICalculator:
    """
    Step 2: Calculate marketing KPIs from combined data
    Computes: CTR, CPC, CVR, CPA, ROAS, and aggregations
    """
    
    def __init__(self, combined_df: pd.DataFrame):
        """
        Initialize with combined dataframe from Step 1
        combined_df should have columns: date, campaign, channel, impressions, clicks, 
                    spend, conversions, revenue, visits, rainfall, etc.
        """
        self.df = combined_df.copy()
        self.kpis = {}
        self.aggregations = {}
        
    def calculate_basic_kpis(self) -> Dict:
        """
        Calculate fundamental KPIs for the entire dataset
        """
        kpis = {
            'total_impressions': 0,
            'total_clicks': 0,
            'total_conversions': 0,
            'total_spend': 0,
            'total_revenue': 0,
            'total_visits': 0,
            'ctr': 0,  # Click-Through Rate
            'cpc': 0,  # Cost Per Click
            'cvr': 0,  # Conversion Rate
            'cpa': 0,  # Cost Per Acquisition
            'roas': 0,  # Return on Ad Spend
            'avg_daily_impressions': 0,
            'avg_daily_clicks': 0,
            'avg_daily_conversions': 0,
        }
        
        # Calculate totals
        kpis['total_impressions'] = self.df['impressions'].sum()
        kpis['total_clicks'] = self.df['clicks'].sum()
        kpis['total_conversions'] = self.df['conversions'].sum()
        kpis['total_spend'] = self.df['spend'].sum()
        kpis['total_revenue'] = self.df['revenue'].sum()
        kpis['total_visits'] = self.df['visits'].sum() if 'visits' in self.df.columns else 0
        
        # Calculate rates (avoid division by zero)
        if kpis['total_impressions'] > 0:
            kpis['ctr'] = (kpis['total_clicks'] / kpis['total_impressions']) * 100
        
        if kpis['total_clicks'] > 0:
            kpis['cpc'] = kpis['total_spend'] / kpis['total_clicks']
        
        if kpis['total_clicks'] > 0:
            kpis['cvr'] = (kpis['total_conversions'] / kpis['total_clicks']) * 100
        
        if kpis['total_conversions'] > 0:
            kpis['cpa'] = kpis['total_spend'] / kpis['total_conversions']
        
        if kpis['total_spend'] > 0:
            kpis['roas'] = kpis['total_revenue'] / kpis['total_spend']
        
        # Calculate daily averages
        num_days = len(self.df)
        if num_days > 0:
            kpis['avg_daily_impressions'] = kpis['total_impressions'] / num_days
            kpis['avg_daily_clicks'] = kpis['total_clicks'] / num_days
            kpis['avg_daily_conversions'] = kpis['total_conversions'] / num_days
        
        self.kpis['overall'] = kpis
        return kpis
    
    def calculate_by_channel(self) -> Dict[str, Dict]:
        """
        Calculate KPIs grouped by channel (email, social, organic, etc.)
        """
        if 'channel' not in self.df.columns:
            return {}
        
        channel_kpis = {}
        
        for channel in self.df['channel'].unique():
            channel_df = self.df[self.df['channel'] == channel]
            
            total_impressions = channel_df['impressions'].sum()
            total_clicks = channel_df['clicks'].sum()
            total_conversions = channel_df['conversions'].sum()
            total_spend = channel_df['spend'].sum()
            total_revenue = channel_df['revenue'].sum()
            
            kpi = {
                'channel': channel,
                'impressions': total_impressions,
                'clicks': total_clicks,
                'conversions': total_conversions,
                'spend': total_spend,
                'revenue': total_revenue,
                'ctr': (total_clicks / total_impressions * 100) if total_impressions > 0 else 0,
                'cpc': (total_spend / total_clicks) if total_clicks > 0 else 0,
                'cvr': (total_conversions / total_clicks * 100) if total_clicks > 0 else 0,
                'cpa': (total_spend / total_conversions) if total_conversions > 0 else 0,
                'roas': (total_revenue / total_spend) if total_spend > 0 else 0,
            }
            
            channel_kpis[channel] = kpi
        
        self.aggregations['by_channel'] = channel_kpis
        return channel_kpis
    
    def calculate_by_campaign(self) -> Dict[str, Dict]:
        """
        Calculate KPIs grouped by campaign
        """
        if 'campaign' not in self.df.columns:
            return {}
        
        campaign_kpis = {}
        
        for campaign in self.df['campaign'].unique():
            campaign_df = self.df[self.df['campaign'] == campaign]
            
            total_impressions = campaign_df['impressions'].sum()
            total_clicks = campaign_df['clicks'].sum()
            total_conversions = campaign_df['conversions'].sum()
            total_spend = campaign_df['spend'].sum()
            total_revenue = campaign_df['revenue'].sum()
            
            kpi = {
                'campaign': campaign,
                'impressions': total_impressions,
                'clicks': total_clicks,
                'conversions': total_conversions,
                'spend': total_spend,
                'revenue': total_revenue,
                'ctr': (total_clicks / total_impressions * 100) if total_impressions > 0 else 0,
                'cpc': (total_spend / total_clicks) if total_clicks > 0 else 0,
                'cvr': (total_conversions / total_clicks * 100) if total_clicks > 0 else 0,
                'cpa': (total_spend / total_conversions) if total_conversions > 0 else 0,
                'roas': (total_revenue / total_spend) if total_spend > 0 else 0,
            }
            
            campaign_kpis[campaign] = kpi
        
        self.aggregations['by_campaign'] = campaign_kpis
        return campaign_kpis
    
    def calculate_by_date(self) -> pd.DataFrame:
        """
        Calculate daily KPIs (time-series data for charts)
        """
        if 'date' not in self.df.columns:
            return pd.DataFrame()
        
        daily_kpis = self.df.groupby('date').agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'conversions': 'sum',
            'spend': 'sum',
            'revenue': 'sum',
            'visits': 'sum' if 'visits' in self.df.columns else lambda x: 0
        }).reset_index()
        
        # Calculate daily rates
        daily_kpis['ctr'] = (daily_kpis['clicks'] / daily_kpis['impressions'] * 100).fillna(0)
        daily_kpis['cpc'] = (daily_kpis['spend'] / daily_kpis['clicks']).fillna(0)
        daily_kpis['cvr'] = (daily_kpis['conversions'] / daily_kpis['clicks'] * 100).fillna(0)
        daily_kpis['cpa'] = (daily_kpis['spend'] / daily_kpis['conversions']).fillna(0)
        daily_kpis['roas'] = (daily_kpis['revenue'] / daily_kpis['spend']).fillna(0)
        
        self.aggregations['by_date'] = daily_kpis
        return daily_kpis
    
    def calculate_by_city(self) -> Dict[str, Dict]:
        """
        Calculate KPIs grouped by city (if available)
        """
        if 'city' not in self.df.columns:
            return {}
        
        city_kpis = {}
        
        for city in self.df['city'].unique():
            city_df = self.df[self.df['city'] == city]
            
            total_visits = city_df['visits'].sum() if 'visits' in city_df.columns else 0
            total_conversions = city_df['conversions'].sum()
            total_spend = city_df['spend'].sum()
            total_revenue = city_df['revenue'].sum()
            
            kpi = {
                'city': city,
                'visits': total_visits,
                'conversions': total_conversions,
                'spend': total_spend,
                'revenue': total_revenue,
                'conversion_rate': (total_conversions / total_visits * 100) if total_visits > 0 else 0,
                'revenue_per_visit': (total_revenue / total_visits) if total_visits > 0 else 0,
                'roas': (total_revenue / total_spend) if total_spend > 0 else 0,
            }
            
            city_kpis[city] = kpi
        
        self.aggregations['by_city'] = city_kpis
        return city_kpis
    
    def get_top_performers(self, metric: str = 'roas', n: int = 5) -> List[Dict]:
        """
        Get top N campaigns/channels by a specific metric
        metric: 'roas', 'ctr', 'cpa', 'revenue', etc.
        """
        if 'by_campaign' not in self.aggregations:
            self.calculate_by_campaign()
        
        campaigns = list(self.aggregations['by_campaign'].values())
        
        # Sort by metric (descending for positive metrics, ascending for cost metrics)
        if metric.startswith('c'):  # Cost metrics (CPC, CPA, etc.)
            sorted_campaigns = sorted(campaigns, key=lambda x: x.get(metric, float('inf')))
        else:  # Performance metrics (ROAS, CTR, CVR, etc.)
            sorted_campaigns = sorted(campaigns, key=lambda x: x.get(metric, 0), reverse=True)
        
        return sorted_campaigns[:n]
    
    def get_worst_performers(self, metric: str = 'roas', n: int = 5) -> List[Dict]:
        """
        Get bottom N campaigns/channels by a specific metric
        """
        if 'by_campaign' not in self.aggregations:
            self.calculate_by_campaign()
        
        campaigns = list(self.aggregations['by_campaign'].values())
        
        # Sort by metric (ascending for positive metrics, descending for cost metrics)
        if metric.startswith('c'):  # Cost metrics
            sorted_campaigns = sorted(campaigns, key=lambda x: x.get(metric, 0), reverse=True)
        else:  # Performance metrics
            sorted_campaigns = sorted(campaigns, key=lambda x: x.get(metric, float('inf')))
        
        return sorted_campaigns[:n]
    
    def get_day_of_week_analysis(self) -> Dict:
        """
        Analyze performance by day of week
        """
        if 'date' not in self.df.columns:
            return {}
        
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.df['day_of_week'] = self.df['date'].dt.day_name()
        
        dow_analysis = {}
        
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            day_df = self.df[self.df['day_of_week'] == day]
            
            if len(day_df) == 0:
                continue
            
            total_impressions = day_df['impressions'].sum()
            total_clicks = day_df['clicks'].sum()
            total_conversions = day_df['conversions'].sum()
            total_spend = day_df['spend'].sum()
            total_revenue = day_df['revenue'].sum()
            
            kpi = {
                'day': day,
                'impressions': total_impressions,
                'clicks': total_clicks,
                'conversions': total_conversions,
                'spend': total_spend,
                'revenue': total_revenue,
                'ctr': (total_clicks / total_impressions * 100) if total_impressions > 0 else 0,
                'cpa': (total_spend / total_conversions) if total_conversions > 0 else 0,
                'roas': (total_revenue / total_spend) if total_spend > 0 else 0,
                'avg_spend': total_spend / len(day_df) if len(day_df) > 0 else 0,
            }
            
            dow_analysis[day] = kpi
        
        self.aggregations['by_day_of_week'] = dow_analysis
        return dow_analysis
    
    def generate_kpi_summary(self) -> Dict:
        """
        Generate a comprehensive summary of all KPIs for reporting
        """
        summary = {
            'overall': self.kpis.get('overall', {}),
            'by_channel': self.aggregations.get('by_channel', {}),
            'by_campaign': self.aggregations.get('by_campaign', {}),
            'by_city': self.aggregations.get('by_city', {}),
            'by_day_of_week': self.aggregations.get('by_day_of_week', {}),
            'top_campaigns': self.get_top_performers('roas', 5),
            'worst_campaigns': self.get_worst_performers('roas', 5),
            'daily_trend': self.aggregations.get('by_date', {}).to_dict('records') if isinstance(self.aggregations.get('by_date'), pd.DataFrame) else []
        }
        
        return summary
    
    def calculate_all(self) -> Dict:
        """
        Run all calculations and return complete KPI summary
        """
        print("📊 Calculating KPIs...")
        
        self.calculate_basic_kpis()
        print("✓ Overall KPIs calculated")
        
        self.calculate_by_channel()
        print("✓ Channel KPIs calculated")
        
        self.calculate_by_campaign()
        print("✓ Campaign KPIs calculated")
        
        self.calculate_by_date()
        print("✓ Daily KPIs calculated")
        
        self.calculate_by_city()
        print("✓ City KPIs calculated")
        
        self.get_day_of_week_analysis()
        print("✓ Day-of-week analysis complete")
        
        summary = self.generate_kpi_summary()
        print("✓ KPI summary generated")
        
        return summary


# =====================
# USAGE EXAMPLE
# =====================

if __name__ == "__main__":
    # Assume combined_df comes from Step 1 (pipeline.py)
    # Load combined data
    combined_df = pd.read_csv('combined_data.csv')
    
    # Initialize calculator
    calculator = KPICalculator(combined_df)
    
    # Calculate all KPIs
    kpi_summary = calculator.calculate_all()
    
    # Print results
    print("\n" + "="*50)
    print("📊 KPI SUMMARY")
    print("="*50)
    
    overall = kpi_summary['overall']
    print(f"\n🎯 Overall Metrics:")
    print(f"  • Total Impressions: {overall['total_impressions']:,.0f}")
    print(f"  • Total Clicks: {overall['total_clicks']:,.0f}")
    print(f"  • Total Conversions: {overall['total_conversions']:,.0f}")
    print(f"  • Total Spend: ${overall['total_spend']:,.2f}")
    print(f"  • Total Revenue: ${overall['total_revenue']:,.2f}")
    print(f"  • CTR: {overall['ctr']:.2f}%")
    print(f"  • CPC: ${overall['cpc']:.2f}")
    print(f"  • CVR: {overall['cvr']:.2f}%")
    print(f"  • CPA: ${overall['cpa']:.2f}")
    print(f"  • ROAS: {overall['roas']:.2f}x")
    
    print(f"\n📈 By Channel:")
    for channel, kpi in kpi_summary['by_channel'].items():
        print(f"  • {channel}:")
        print(f"    - Spend: ${kpi['spend']:,.2f} | Revenue: ${kpi['revenue']:,.2f}")
        print(f"    - ROAS: {kpi['roas']:.2f}x | CPA: ${kpi['cpa']:.2f}")
    
    print(f"\n🏆 Top Campaigns (by ROAS):")
    for i, campaign in enumerate(kpi_summary['top_campaigns'], 1):
        print(f"  {i}. {campaign['campaign']}: ROAS {campaign['roas']:.2f}x | Spend: ${campaign['spend']:,.2f}")
    
    print(f"\n📍 By City:")
    for city, kpi in kpi_summary['by_city'].items():
        print(f"  • {city}: {kpi['conversions']} conversions | Revenue: ${kpi['revenue']:,.2f}")
    
    print(f"\n📅 By Day of Week:")
    for day, kpi in kpi_summary['by_day_of_week'].items():
        print(f"  • {day}: CTR {kpi['ctr']:.2f}% | ROAS {kpi['roas']:.2f}x")
