import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from scipy import stats

class WeatherAnalyzer:
    """
    Step 3: Analyze weather correlation with performance metrics
    Correlates temperature, rainfall with conversions, visits, revenue
    Generates weather-driven insights and recommendations
    """
    
    def __init__(self, combined_df: pd.DataFrame):
        """
        Initialize with combined dataframe
        combined_df should have columns: date, conversions, revenue, visits, 
                    temperature_c, rainfall_mm, channel, city
        """
        self.df = combined_df.copy()
        self.correlations = {}
        self.insights = []
        self.recommendations = []
        
        # Ensure date is datetime
        if 'date' in self.df.columns:
            self.df['date'] = pd.to_datetime(self.df['date'])
    
    def check_weather_data_available(self) -> bool:
        """Check if weather data exists in dataframe"""
        weather_cols = ['temperature_c', 'rainfall_mm']
        return all(col in self.df.columns for col in weather_cols)
    
    def calculate_correlations(self) -> Dict[str, Dict]:
        """
        Calculate Pearson correlation between weather and performance metrics
        Returns: {'metric': {'temperature': corr, 'rainfall': corr, 'p_value': p}}
        """
        if not self.check_weather_data_available():
            print("⚠️ Weather data not available")
            return {}
        
        weather_cols = ['temperature_c', 'rainfall_mm']
        performance_cols = ['conversions', 'revenue', 'visits', 'clicks', 'impressions']
        
        # Filter only available performance columns
        available_perf_cols = [col for col in performance_cols if col in self.df.columns]
        
        correlations = {}
        
        for perf_col in available_perf_cols:
            correlations[perf_col] = {}
            
            for weather_col in weather_cols:
                # Remove NaN values for correlation
                valid_data = self.df[[perf_col, weather_col]].dropna()
                
                if len(valid_data) > 2:  # Need at least 3 data points
                    corr, p_value = stats.pearsonr(valid_data[weather_col], valid_data[perf_col])
                    correlations[perf_col][weather_col] = {
                        'correlation': corr,
                        'p_value': p_value,
                        'significant': p_value < 0.05  # 95% confidence
                    }
        
        self.correlations = correlations
        return correlations
    
    def get_strong_correlations(self, threshold: float = 0.6) -> Dict[str, Dict]:
        """
        Get correlations above threshold (strong signals)
        threshold: typically 0.6 for strong correlation
        """
        strong = {}
        
        for metric, weather_corr in self.correlations.items():
            for weather_type, data in weather_corr.items():
                corr = abs(data['correlation'])
                if corr >= threshold and data['significant']:
                    if metric not in strong:
                        strong[metric] = {}
                    strong[metric][weather_type] = data
        
        return strong
    
    def analyze_rainy_days(self) -> Dict:
        """
        Specific analysis: Performance on rainy vs. non-rainy days
        """
        if 'rainfall_mm' not in self.df.columns:
            return {}
        
        # Define rainy day: rainfall > 1mm
        rainy_threshold = 1.0
        rainy_days = self.df[self.df['rainfall_mm'] > rainy_threshold]
        non_rainy_days = self.df[self.df['rainfall_mm'] <= rainy_threshold]
        
        metrics_to_analyze = ['conversions', 'revenue', 'visits', 'clicks']
        available_metrics = [m for m in metrics_to_analyze if m in self.df.columns]
        
        analysis = {
            'rainy_days_count': len(rainy_days),
            'non_rainy_days_count': len(non_rainy_days),
            'metrics': {}
        }
        
        for metric in available_metrics:
            if len(rainy_days) > 0 and len(non_rainy_days) > 0:
                rainy_avg = rainy_days[metric].mean()
                non_rainy_avg = non_rainy_days[metric].mean()
                
                # Calculate percentage difference
                if non_rainy_avg > 0:
                    pct_change = ((rainy_avg - non_rainy_avg) / non_rainy_avg) * 100
                else:
                    pct_change = 0
                
                analysis['metrics'][metric] = {
                    'rainy_avg': rainy_avg,
                    'non_rainy_avg': non_rainy_avg,
                    'pct_change': pct_change,
                    'interpretation': 'increase' if pct_change > 0 else 'decrease'
                }
        
        return analysis
    
    def analyze_temperature_ranges(self) -> Dict:
        """
        Segment performance by temperature ranges
        Cold: < 10°C, Cool: 10-15°C, Mild: 15-20°C, Warm: 20-25°C, Hot: > 25°C
        """
        if 'temperature_c' not in self.df.columns:
            return {}
        
        # Define temperature ranges
        temp_ranges = {
            'cold': (0, 10),
            'cool': (10, 15),
            'mild': (15, 20),
            'warm': (20, 25),
            'hot': (25, 50)
        }
        
        metrics_to_analyze = ['conversions', 'revenue', 'visits', 'clicks']
        available_metrics = [m for m in metrics_to_analyze if m in self.df.columns]
        
        analysis = {}
        
        for temp_name, (min_t, max_t) in temp_ranges.items():
            temp_data = self.df[(self.df['temperature_c'] >= min_t) & (self.df['temperature_c'] < max_t)]
            
            if len(temp_data) > 0:
                range_analysis = {
                    'count': len(temp_data),
                    'metrics': {}
                }
                
                for metric in available_metrics:
                    range_analysis['metrics'][metric] = {
                        'avg': temp_data[metric].mean(),
                        'total': temp_data[metric].sum(),
                        'max': temp_data[metric].max(),
                        'min': temp_data[metric].min()
                    }
                
                analysis[temp_name] = range_analysis
        
        return analysis
    
    def generate_weather_insights(self) -> List[Dict]:
        """
        Generate human-readable insights from weather analysis
        """
        insights = []
        
        # Get strong correlations
        strong_corr = self.get_strong_correlations(threshold=0.6)
        
        for metric, weather_data in strong_corr.items():
            for weather_type, corr_data in weather_data.items():
                corr_value = corr_data['correlation']
                direction = 'increases' if corr_value > 0 else 'decreases'
                
                insight = {
                    'type': 'correlation',
                    'metric': metric,
                    'weather_factor': weather_type,
                    'correlation': corr_value,
                    'strength': 'strong' if abs(corr_value) > 0.7 else 'moderate',
                    'text': f"Performance correlates with {weather_type}: {metric} {direction} when {weather_type} increases (r={corr_value:.2f})"
                }
                insights.append(insight)
        
        # Rainy day insights
        rainy_analysis = self.analyze_rainy_days()
        if rainy_analysis:
            for metric, data in rainy_analysis.get('metrics', {}).items():
                pct = data['pct_change']
                if abs(pct) > 10:  # Only significant changes
                    insight = {
                        'type': 'rainy_day',
                        'metric': metric,
                        'pct_change': pct,
                        'text': f"On rainy days, {metric} {data['interpretation']} by {abs(pct):.1f}%"
                    }
                    insights.append(insight)
        
        # Temperature range insights
        temp_analysis = self.analyze_temperature_ranges()
        if temp_analysis:
            # Find best and worst performing temperature ranges
            best_temp = max(temp_analysis.items(), 
                           key=lambda x: x[1]['metrics'].get('conversions', {}).get('avg', 0))
            worst_temp = min(temp_analysis.items(),
                            key=lambda x: x[1]['metrics'].get('conversions', {}).get('avg', 0))
            
            if best_temp[0] != worst_temp[0]:
                insight = {
                    'type': 'temperature_range',
                    'best_temp': best_temp[0],
                    'worst_temp': worst_temp[0],
                    'text': f"Performance peaks during {best_temp[0]} weather and dips during {worst_temp[0]} weather"
                }
                insights.append(insight)
        
        self.insights = insights
        return insights
    
    def generate_recommendations(self) -> List[Dict]:
        """
        Generate actionable recommendations based on weather insights
        """
        recommendations = []
        
        # If strong weather correlation detected
        strong_corr = self.get_strong_correlations(threshold=0.6)
        
        if strong_corr:
            for metric, weather_data in strong_corr.items():
                for weather_type, data in weather_data.items():
                    if data['correlation'] > 0.6:
                        # Positive correlation: increase investment when weather is favorable
                        rec = {
                            'type': 'increase_budget_when_favorable',
                            'priority': 'high',
                            'text': f"Increase marketing budget when {weather_type} is favorable (high), as it correlates with higher {metric}",
                            'estimated_impact': f"{abs(data['correlation']) * 100:.0f}% correlation"
                        }
                        recommendations.append(rec)
                    elif data['correlation'] < -0.6:
                        # Negative correlation: shift budget to digital when unfavorable weather
                        rec = {
                            'type': 'shift_to_digital_when_unfavorable',
                            'priority': 'high',
                            'text': f"When {weather_type} is unfavorable, shift budget toward digital channels as {metric} drops",
                            'estimated_impact': f"{abs(data['correlation']) * 100:.0f}% correlation"
                        }
                        recommendations.append(rec)
        
        # Rainy day specific recommendations
        rainy_analysis = self.analyze_rainy_days()
        if rainy_analysis:
            rainy_conv = rainy_analysis['metrics'].get('conversions', {})
            if rainy_conv.get('pct_change', 0) > 10:
                rec = {
                    'type': 'capitalize_on_rainy_days',
                    'priority': 'high',
                    'text': f"Conversions increase {rainy_conv['pct_change']:.1f}% on rainy days. Increase digital ad spend when rain is forecasted.",
                    'estimated_impact': f"+{rainy_conv['pct_change']:.1f}% conversions"
                }
                recommendations.append(rec)
            elif rainy_conv.get('pct_change', 0) < -10:
                rec = {
                    'type': 'reduce_spend_on_rainy_days',
                    'priority': 'medium',
                    'text': f"Conversions drop {abs(rainy_conv['pct_change']):.1f}% on rainy days. Consider reducing outdoor/foot-traffic focused campaigns.",
                    'estimated_impact': f"Save {abs(rainy_conv['pct_change']):.1f}% wasted spend"
                }
                recommendations.append(rec)
        
        # Temperature range recommendations
        temp_analysis = self.analyze_temperature_ranges()
        if len(temp_analysis) > 1:
            best_temp = max(temp_analysis.items(),
                           key=lambda x: x[1]['metrics'].get('conversions', {}).get('avg', 0))
            rec = {
                'type': 'optimize_for_best_temperature',
                'priority': 'medium',
                'text': f"Performance peaks during {best_temp[0]} weather. Plan major campaigns and promotions for these conditions.",
                'estimated_impact': "Maximize campaign ROI"
            }
            recommendations.append(rec)
        
        self.recommendations = recommendations
        return recommendations
    
    def get_by_channel_weather_impact(self) -> Dict:
        """
        Analyze how weather affects different channels differently
        """
        if 'channel' not in self.df.columns or not self.check_weather_data_available():
            return {}
        
        by_channel = {}
        
        for channel in self.df['channel'].unique():
            channel_df = self.df[self.df['channel'] == channel]
            
            # Calculate correlation for this channel
            valid_data = channel_df[['conversions', 'temperature_c', 'rainfall_mm']].dropna()
            
            if len(valid_data) > 2:
                temp_corr, temp_p = stats.pearsonr(valid_data['temperature_c'], valid_data['conversions'])
                rain_corr, rain_p = stats.pearsonr(valid_data['rainfall_mm'], valid_data['conversions'])
                
                by_channel[channel] = {
                    'temperature_correlation': {
                        'value': temp_corr,
                        'p_value': temp_p,
                        'significant': temp_p < 0.05
                    },
                    'rainfall_correlation': {
                        'value': rain_corr,
                        'p_value': rain_p,
                        'significant': rain_p < 0.05
                    }
                }
        
        return by_channel
    
    def generate_summary(self) -> Dict:
        """
        Generate comprehensive weather analysis summary
        """
        summary = {
            'data_available': self.check_weather_data_available(),
            'correlations': self.correlations,
            'strong_correlations': self.get_strong_correlations(threshold=0.6),
            'rainy_day_analysis': self.analyze_rainy_days(),
            'temperature_range_analysis': self.analyze_temperature_ranges(),
            'by_channel_impact': self.get_by_channel_weather_impact(),
            'insights': self.insights,
            'recommendations': self.recommendations
        }
        
        return summary
    
    def analyze_all(self) -> Dict:
        """
        Run all weather analysis and return complete summary
        """
        print("🌦️ Analyzing weather correlations...")
        
        if not self.check_weather_data_available():
            print("⚠️ Weather data not available in dataset")
            return {}
        
        self.calculate_correlations()
        print("✓ Correlations calculated")
        
        self.generate_weather_insights()
        print("✓ Insights generated")
        
        self.generate_recommendations()
        print("✓ Recommendations generated")
        
        summary = self.generate_summary()
        print("✓ Weather analysis complete")
        
        return summary


# =====================
# USAGE EXAMPLE
# =====================

if __name__ == "__main__":
    # Load combined data (from Step 1 + Step 2)
    combined_df = pd.read_csv('test.csv')
    
    # Initialize weather analyzer
    analyzer = WeatherAnalyzer(combined_df)
    
    # Run all analysis
    weather_summary = analyzer.analyze_all()
    
    # Print results
    print("\n" + "="*60)
    print("🌦️ WEATHER ANALYSIS SUMMARY")
    print("="*60)
    
    print("\n📊 Strong Correlations (r > 0.6):")
    strong = weather_summary.get('strong_correlations', {})
    if strong:
        for metric, weather_data in strong.items():
            for weather_type, data in weather_data.items():
                print(f"  • {metric} ↔️ {weather_type}: r={data['correlation']:.2f}")
    else:
        print("  • No strong correlations found")
    
    print("\n🌧️ Rainy Day Impact:")
    rainy = weather_summary.get('rainy_day_analysis', {})
    if rainy:
        print(f"  • Rainy days: {rainy['rainy_days_count']}")
        print(f"  • Non-rainy days: {rainy['non_rainy_days_count']}")
        for metric, data in rainy.get('metrics', {}).items():
            print(f"  • {metric}: {data['pct_change']:+.1f}% on rainy days")
    
    print("\n🌡️ Temperature Range Performance:")
    temp = weather_summary.get('temperature_range_analysis', {})
    if temp:
        for temp_range, data in temp.items():
            conversions = data['metrics'].get('conversions', {}).get('avg', 0)
            print(f"  • {temp_range.capitalize()}: {conversions:.0f} avg conversions")
    
    print("\n💡 Key Insights:")
    for insight in weather_summary.get('insights', [])[:5]:
        print(f"  • {insight['text']}")
    
    print("\n🎯 Recommendations:")
    for rec in weather_summary.get('recommendations', [])[:5]:
        print(f"  • [{rec['priority'].upper()}] {rec['text']}")
    
    print("\n📈 By Channel Weather Impact:")
    by_channel = weather_summary.get('by_channel_impact', {})
    for channel, data in by_channel.items():
        temp_sig = "✓" if data['temperature_correlation']['significant'] else "✗"
        rain_sig = "✓" if data['rainfall_correlation']['significant'] else "✗"
        print(f"  • {channel}:")
        print(f"    - Temperature impact {temp_sig}: {data['temperature_correlation']['value']:.2f}")
        print(f"    - Rainfall impact {rain_sig}: {data['rainfall_correlation']['value']:.2f}")
