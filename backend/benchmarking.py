import pandas as pd
import json
import os
from typing import Dict, List, Tuple

class BenchmarkAnalyzer:
    """
    Step 5: Compare client KPIs against industry benchmarks
    Benchmarks loaded from industry_benchmarks.json
    Generates comparative insights and performance ratings
    """
    
    def __init__(self, kpi_summary: Dict, benchmarks_file: str = 'benchmarks/industry_benchmarks.json'):
        """
        Initialize with KPI summary from Step 2
        kpi_summary: output from KPICalculator.generate_kpi_summary()
        benchmarks_file: path to JSON with industry benchmarks
        """
        self.kpi_summary = kpi_summary
        self.benchmarks = self._load_benchmarks(benchmarks_file)
        self.comparisons = {}
        self.insights = []
        self.recommendations = []
    
    def _load_benchmarks(self, benchmarks_file: str) -> Dict:
        """
        Load benchmark data from JSON file
        Expected structure:
        {
            "email": {
                "avg_ctr": 3.5,
                "avg_cpc": 1.2,
                ...
            },
            "search": {...},
            "social": {...},
            "overall": {...}
        }
        """
        if not os.path.exists(benchmarks_file):
            print(f"⚠️ Benchmark file not found: {benchmarks_file}")
            return {}
        
        try:
            with open(benchmarks_file, 'r') as f:
                benchmarks = json.load(f)
            print(f"✓ Loaded benchmarks from {benchmarks_file}")
            return benchmarks
        except Exception as e:
            print(f"✗ Error loading benchmarks: {e}")
            return {}
    
    def compare_overall_metrics(self) -> Dict:
        """
        Compare overall KPIs against overall benchmarks
        Returns comparison with percentile ranking
        """
        if not self.benchmarks or 'overall' not in self.benchmarks:
            print("⚠️ No overall benchmarks available")
            return {}
        
        overall_kpis = self.kpi_summary.get('overall', {})
        overall_bench = self.benchmarks['overall']
        
        comparison = {}
        
        # Map KPI names to benchmark names
        kpi_bench_map = {
            'ctr': 'avg_ctr',
            'cpc': 'avg_cpc',
            'cvr': 'avg_conversion_rate',
            'cpa': 'avg_cpa',
            'roas': 'avg_roas',
        }
        
        for kpi_name, bench_name in kpi_bench_map.items():
            client_value = overall_kpis.get(kpi_name)
            benchmark_value = overall_bench.get(bench_name)
            
            if client_value is not None and benchmark_value is not None:
                # Calculate difference and percentile
                difference = client_value - benchmark_value
                pct_difference = (difference / benchmark_value * 100) if benchmark_value != 0 else 0
                
                # Determine status (for cost metrics, lower is better)
                if kpi_name in ['cpc', 'cpa']:
                    status = 'above' if difference > 0 else 'below'  # below = better for costs
                    performance = 'worse' if difference > 0 else 'better'
                else:
                    status = 'above' if difference > 0 else 'below'  # above = better for rates
                    performance = 'better' if difference > 0 else 'worse'
                
                # Determine percentile tier
                if abs(pct_difference) < 5:
                    tier = 'in_line'
                elif pct_difference > 20:
                    tier = 'top_20'
                elif pct_difference > 10:
                    tier = 'top_40'
                elif pct_difference < -20:
                    tier = 'bottom_20'
                elif pct_difference < -10:
                    tier = 'bottom_40'
                else:
                    tier = 'average'
                
                comparison[kpi_name] = {
                    'client_value': client_value,
                    'benchmark_value': benchmark_value,
                    'difference': difference,
                    'pct_difference': pct_difference,
                    'status': status,
                    'performance': performance,
                    'tier': tier,
                    'badge': self._get_badge(tier),
                    'text': f"{kpi_name.upper()}: {client_value:.2f} vs benchmark {benchmark_value:.2f} ({pct_difference:+.1f}%) {self._get_badge(tier)}"
                }
        
        self.comparisons['overall'] = comparison
        return comparison
    
    def compare_by_channel(self) -> Dict[str, Dict]:
        """
        Compare channel KPIs against channel-specific benchmarks
        """
        if 'by_channel' not in self.kpi_summary or not self.benchmarks:
            return {}
        
        channel_comparisons = {}
        client_channels = self.kpi_summary.get('by_channel', {})
        
        for channel, client_kpi in client_channels.items():
            # Check if channel benchmarks exist
            channel_bench = self.benchmarks.get(channel, {})
            
            if not channel_bench:
                # Fall back to overall benchmarks
                channel_bench = self.benchmarks.get('overall', {})
            
            channel_comparison = {}
            
            kpi_bench_map = {
                'ctr': 'avg_ctr',
                'cpc': 'avg_cpc',
                'cvr': 'avg_conversion_rate',
                'cpa': 'avg_cpa',
                'roas': 'avg_roas',
            }
            
            for kpi_name, bench_name in kpi_bench_map.items():
                client_value = client_kpi.get(kpi_name)
                benchmark_value = channel_bench.get(bench_name)
                
                if client_value is not None and benchmark_value is not None:
                    difference = client_value - benchmark_value
                    pct_difference = (difference / benchmark_value * 100) if benchmark_value != 0 else 0
                    
                    if kpi_name in ['cpc', 'cpa']:
                        status = 'above' if difference > 0 else 'below'
                    else:
                        status = 'above' if difference > 0 else 'below'
                    
                    # Determine tier
                    if abs(pct_difference) < 5:
                        tier = 'in_line'
                    elif pct_difference > 15:
                        tier = 'top_20'
                    elif pct_difference > 5:
                        tier = 'top_40'
                    elif pct_difference < -15:
                        tier = 'bottom_20'
                    elif pct_difference < -5:
                        tier = 'bottom_40'
                    else:
                        tier = 'average'
                    
                    channel_comparison[kpi_name] = {
                        'client_value': client_value,
                        'benchmark_value': benchmark_value,
                        'pct_difference': pct_difference,
                        'tier': tier,
                        'badge': self._get_badge(tier),
                    }
            
            channel_comparisons[channel] = channel_comparison
        
        self.comparisons['by_channel'] = channel_comparisons
        return channel_comparisons
    
    def _get_badge(self, tier: str) -> str:
        """
        Return emoji badge based on performance tier
        """
        badges = {
            'top_20': '🏆 Top 20%',
            'top_40': '✅ Top 40%',
            'in_line': '➖ Inline',
            'average': '📊 Average',
            'bottom_40': '⚠️ Below Average',
            'bottom_20': '🔴 Bottom 20%',
        }
        return badges.get(tier, '❓')
    
    def get_strengths(self, min_pct_above: float = 10) -> List[Dict]:
        """
        Identify metrics where client outperforms benchmark
        min_pct_above: minimum percentage above benchmark to be considered a strength
        """
        strengths = []
        
        overall_comp = self.comparisons.get('overall', {})
        
        for metric, data in overall_comp.items():
            if data['pct_difference'] > min_pct_above:
                strength = {
                    'metric': metric,
                    'client_value': data['client_value'],
                    'benchmark_value': data['benchmark_value'],
                    'pct_above': data['pct_difference'],
                    'tier': data['tier'],
                    'text': f"✅ {metric.upper()} strength: {data['pct_difference']:.1f}% above benchmark"
                }
                strengths.append(strength)
        
        # Sort by pct_difference descending
        strengths.sort(key=lambda x: x['pct_above'], reverse=True)
        return strengths
    
    def get_weaknesses(self, max_pct_below: float = -10) -> List[Dict]:
        """
        Identify metrics where client underperforms benchmark
        max_pct_below: maximum percentage below benchmark to be considered a weakness
        """
        weaknesses = []
        
        overall_comp = self.comparisons.get('overall', {})
        
        for metric, data in overall_comp.items():
            if data['pct_difference'] < max_pct_below:
                weakness = {
                    'metric': metric,
                    'client_value': data['client_value'],
                    'benchmark_value': data['benchmark_value'],
                    'pct_below': abs(data['pct_difference']),
                    'tier': data['tier'],
                    'text': f"🔴 {metric.upper()} weakness: {abs(data['pct_difference']):.1f}% below benchmark"
                }
                weaknesses.append(weakness)
        
        # Sort by pct_below descending
        weaknesses.sort(key=lambda x: x['pct_below'], reverse=True)
        return weaknesses
    
    def generate_benchmark_insights(self) -> List[Dict]:
        """
        Generate human-readable insights from benchmark comparisons
        """
        insights = []
        
        overall_comp = self.comparisons.get('overall', {})
        
        # Count performance tiers
        top_20 = len([m for m in overall_comp.values() if m['tier'] == 'top_20'])
        top_40 = len([m for m in overall_comp.values() if m['tier'] == 'top_40'])
        bottom_20 = len([m for m in overall_comp.values() if m['tier'] == 'bottom_20'])
        
        # Overall performance summary
        if top_20 > 0:
            insight = {
                'type': 'strong_performance',
                'text': f"🏆 Strong performance: {top_20} metric(s) in top 20% vs industry benchmarks"
            }
            insights.append(insight)
        
        if bottom_20 > 0:
            insight = {
                'type': 'weak_performance',
                'text': f"🔴 Areas of concern: {bottom_20} metric(s) in bottom 20% vs industry benchmarks"
            }
            insights.append(insight)
        
        # Strength/weakness summary
        strengths = self.get_strengths()
        if strengths:
            strong_metrics = ', '.join([s['metric'].upper() for s in strengths[:2]])
            insight = {
                'type': 'key_strengths',
                'text': f"💪 Key strengths: {strong_metrics} significantly outperform benchmarks"
            }
            insights.append(insight)
        
        weaknesses = self.get_weaknesses()
        if weaknesses:
            weak_metrics = ', '.join([w['metric'].upper() for w in weaknesses[:2]])
            insight = {
                'type': 'key_weaknesses',
                'text': f"⚡ Improvement areas: {weak_metrics} underperform benchmarks—prioritize optimization"
            }
            insights.append(insight)
        
        self.insights = insights
        return insights
    
    def generate_benchmark_recommendations(self) -> List[Dict]:
        """
        Generate actionable recommendations based on benchmark gaps
        """
        recommendations = []
        
        weaknesses = self.get_weaknesses()
        strengths = self.get_strengths()
        
        # Recommendations for weak areas
        for weakness in weaknesses[:3]:
            metric = weakness['metric']
            gap = weakness['pct_below']
            
            if metric == 'ctr':
                rec = {
                    'type': 'improve_ctr',
                    'priority': 'high',
                    'metric': metric,
                    'text': f"CTR is {gap:.1f}% below benchmark. Test new ad copy, landing pages, and targeting to improve click-through."
                }
            elif metric == 'cpc':
                rec = {
                    'type': 'reduce_cpc',
                    'priority': 'high',
                    'metric': metric,
                    'text': f"CPC is {gap:.1f}% above benchmark. Refine audience targeting and bid strategy to reduce cost per click."
                }
            elif metric == 'cvr':
                rec = {
                    'type': 'improve_cvr',
                    'priority': 'high',
                    'metric': metric,
                    'text': f"Conversion rate is {gap:.1f}% below benchmark. Optimize landing pages, reduce friction, and A/B test conversion flows."
                }
            elif metric == 'roas':
                rec = {
                    'type': 'improve_roas',
                    'priority': 'high',
                    'metric': metric,
                    'text': f"ROAS is {gap:.1f}% below benchmark. Focus on high-AOV products, improve targeting, and allocate budget to best performers."
                }
            else:
                continue
            
            recommendations.append(rec)
        
        # Recommendations for strong areas
        if strengths:
            strong_metric = strengths[0]['metric']
            strong_pct = strengths[0]['pct_above']
            rec = {
                'type': 'scale_success',
                'priority': 'medium',
                'text': f"Scale winner: {strong_metric.upper()} is {strong_pct:.1f}% above benchmark. Increase budget allocation to this channel/campaign."
            }
            recommendations.append(rec)
        
        self.recommendations = recommendations
        return recommendations
    
    def get_percentile_rank(self, metric: str) -> str:
        """
        Get a simple percentile rank description
        """
        overall_comp = self.comparisons.get('overall', {})
        
        if metric not in overall_comp:
            return "Unknown"
        
        pct_diff = overall_comp[metric]['pct_difference']
        
        if pct_diff > 30:
            return "Top 5%"
        elif pct_diff > 20:
            return "Top 10%"
        elif pct_diff > 10:
            return "Top 25%"
        elif pct_diff > 0:
            return "Top 50%"
        elif pct_diff > -10:
            return "Bottom 50%"
        elif pct_diff > -20:
            return "Bottom 25%"
        elif pct_diff > -30:
            return "Bottom 10%"
        else:
            return "Bottom 5%"
    
    def get_summary(self) -> Dict:
        """Generate comprehensive benchmarking summary"""
        summary = {
            'overall_comparison': self.comparisons.get('overall', {}),
            'by_channel_comparison': self.comparisons.get('by_channel', {}),
            'strengths': self.get_strengths(),
            'weaknesses': self.get_weaknesses(),
            'insights': self.insights,
            'recommendations': self.recommendations,
            'benchmarks_loaded': bool(self.benchmarks)
        }
        return summary
    
    def analyze_all(self) -> Dict:
        """
        Run all benchmark analysis
        """
        print("📊 Analyzing benchmarks...")
        
        if not self.benchmarks:
            print("✗ No benchmarks loaded")
            return {}
        
        self.compare_overall_metrics()
        print("✓ Overall metrics compared")
        
        self.compare_by_channel()
        print("✓ Channel metrics compared")
        
        self.generate_benchmark_insights()
        print("✓ Insights generated")
        
        self.generate_benchmark_recommendations()
        print("✓ Recommendations generated")
        
        summary = self.get_summary()
        print("✓ Benchmarking analysis complete")
        
        return summary


# =====================
# USAGE EXAMPLE
# =====================

# =====================
# USAGE EXAMPLE
# =====================

if __name__ == "__main__":
    # Load combined data
    combined_df = pd.read_csv('combined_data.csv')
    
    # Sample KPI summary from Step 2 (if kpi_calculator.py exists)
    try:
        from kpi_calculator import KPICalculator
        kpi_calc = KPICalculator(combined_df)
        kpi_summary = kpi_calc.calculate_all()
    except:
        # Fallback: create a minimal KPI summary
        print("⚠️ KPICalculator not found. Using minimal test data.")
        kpi_summary = {
            'overall': {
                'ctr': 4.2,
                'cpc': 1.10,
                'cvr': 2.8,
                'cpa': 45.00,
                'roas': 2.3,
            },
            'by_channel': {
                'email': {'ctr': 5.0, 'cpc': 0.50, 'cvr': 4.2, 'cpa': 25.00, 'roas': 4.5},
                'search': {'ctr': 4.2, 'cpc': 1.50, 'cvr': 3.5, 'cpa': 40.00, 'roas': 3.0},
                'social': {'ctr': 2.0, 'cpc': 2.00, 'cvr': 1.5, 'cpa': 60.00, 'roas': 1.5},
            }
        }
    
    # Initialize benchmarking analyzer
    analyzer = BenchmarkAnalyzer(kpi_summary, 'industry_benchmarks.json')
    
    # Run analysis
    bench_summary = analyzer.analyze_all()
    
    # Print results
    print("\n" + "="*60)
    print("📊 BENCHMARKING ANALYSIS")
    print("="*60)
    
    # Check if analysis ran successfully
    if not bench_summary.get('benchmarks_loaded'):
        print("\n✗ Error: Benchmarks not loaded. Check file path and JSON format.")
        print("  Expected: benchmarks/industry_benchmarks.json")
        print("  Required keys: 'overall', 'avg_ctr', 'avg_cpc', etc.")
    else:
        print(f"\n✅ Benchmarks loaded successfully\n")
        
        print(f"🎯 Overall Performance vs Benchmarks:")
        overall_comp = bench_summary.get('overall_comparison', {})
        if overall_comp:
            for metric, comp in overall_comp.items():
                print(f"  {comp['text']}")
        else:
            print("  ⚠️ No overall comparisons available")
        
        print(f"\n💪 Strengths:")
        strengths = bench_summary.get('strengths', [])
        if strengths:
            for strength in strengths:
                print(f"  • {strength['text']}")
        else:
            print("  • No significant strengths identified")
        
        print(f"\n⚡ Weaknesses:")
        weaknesses = bench_summary.get('weaknesses', [])
        if weaknesses:
            for weakness in weaknesses:
                print(f"  • {weakness['text']}")
        else:
            print("  • No significant weaknesses identified")
        
        print(f"\n💡 Insights:")
        insights = bench_summary.get('insights', [])
        if insights:
            for insight in insights:
                print(f"  • {insight['text']}")
        else:
            print("  • No insights generated")
        
        print(f"\n🎯 Recommendations:")
        recommendations = bench_summary.get('recommendations', [])
        if recommendations:
            for rec in recommendations[:5]:
                print(f"  • [{rec['priority'].upper()}] {rec['text']}")
        else:
            print("  • No recommendations available")
        
        print("\n✓ Benchmarking analysis complete")

