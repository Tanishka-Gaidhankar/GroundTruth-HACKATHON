import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from scipy import stats
from datetime import datetime, timedelta

class AnomalyDetector:
    """
    Step 4: Detect anomalies in KPIs using statistical methods
    Uses Z-Score and IQR methods to flag unusual values
    Calculates severity levels: Critical, Warning, Info
    """
    
    def __init__(self, combined_df: pd.DataFrame, z_score_threshold: float = 2.0, 
                 lookback_days: int = 7):
        """
        Initialize with combined dataframe
        z_score_threshold: Default 2.0 = 95% confidence (values beyond this are anomalous)
        lookback_days: Number of days to use for baseline calculation
        """
        self.df = combined_df.copy()
        self.z_score_threshold = z_score_threshold
        self.lookback_days = lookback_days
        self.anomalies = []
        self.anomaly_details = {}
        
        # Ensure date is datetime
        if 'date' in self.df.columns:
            self.df['date'] = pd.to_datetime(self.df['date'])
    
    def calculate_z_scores(self, metric: str) -> pd.Series:
        """
        Calculate Z-scores for a metric
        Z-score = (value - mean) / std_dev
        """
        if metric not in self.df.columns:
            return pd.Series()
        
        data = self.df[metric].dropna()
        if len(data) < 2:
            return pd.Series()
        
        mean = data.mean()
        std = data.std()
        
        if std == 0:  # All values are the same
            return pd.Series(0, index=self.df.index)
        
        z_scores = np.abs((self.df[metric] - mean) / std)
        return z_scores
    
    def detect_anomalies_by_metric(self, metric: str, by_group: str = None) -> List[Dict]:
        """
        Detect anomalies for a specific metric
        metric: column name (e.g., 'ctr', 'conversions', 'revenue')
        by_group: optional grouping column (e.g., 'channel', 'campaign')
        """
        anomalies = []
        
        if metric not in self.df.columns:
            return anomalies
        
        if by_group and by_group in self.df.columns:
            # Detect anomalies within each group
            for group_value in self.df[by_group].unique():
                group_data = self.df[self.df[by_group] == group_value]
                group_anomalies = self._detect_within_group(
                    group_data, metric, group_value, by_group
                )
                anomalies.extend(group_anomalies)
        else:
            # Detect anomalies across all data
            z_scores = self.calculate_z_scores(metric)
            
            for idx, z_score in z_scores.items():
                if z_score > self.z_score_threshold:
                    value = self.df.loc[idx, metric]
                    date = self.df.loc[idx, 'date'] if 'date' in self.df.columns else None
                    
                    # Calculate severity
                    severity = self._calculate_severity(z_score)
                    
                    # Calculate percentage change from mean
                    mean = self.df[metric].mean()
                    pct_change = ((value - mean) / mean * 100) if mean != 0 else 0
                    
                    anomaly = {
                        'date': date,
                        'metric': metric,
                        'value': value,
                        'z_score': z_score,
                        'severity': severity,
                        'pct_change': pct_change,
                        'baseline_mean': mean,
                        'text': f"{severity.upper()}: {metric} = {value:.2f} (Z-score: {z_score:.2f}, {pct_change:+.1f}% from baseline)"
                    }
                    anomalies.append(anomaly)
        
        return anomalies
    
    def _detect_within_group(self, group_data: pd.DataFrame, metric: str, 
                            group_value: str, group_col: str) -> List[Dict]:
        """Helper to detect anomalies within a group"""
        anomalies = []
        
        if len(group_data) < 3:
            return anomalies
        
        z_scores = np.abs((group_data[metric] - group_data[metric].mean()) / group_data[metric].std())
        
        for idx, z_score in z_scores.items():
            if z_score > self.z_score_threshold:
                value = group_data.loc[idx, metric]
                date = group_data.loc[idx, 'date'] if 'date' in group_data.columns else None
                severity = self._calculate_severity(z_score)
                
                mean = group_data[metric].mean()
                pct_change = ((value - mean) / mean * 100) if mean != 0 else 0
                
                anomaly = {
                    'date': date,
                    'metric': metric,
                    'value': value,
                    'z_score': z_score,
                    'severity': severity,
                    'pct_change': pct_change,
                    'baseline_mean': mean,
                    'group': group_value,
                    'group_col': group_col,
                    'text': f"{severity.upper()}: {metric} for {group_col}={group_value} = {value:.2f} (Z-score: {z_score:.2f}, {pct_change:+.1f}%)"
                }
                anomalies.append(anomaly)
        
        return anomalies
    
    def _calculate_severity(self, z_score: float) -> str:
        """
        Calculate severity level based on Z-score
        Z > 3.0: Critical (99.7% confidence)
        Z > 2.5: Warning (98.8% confidence)
        Z > 2.0: Info (95.4% confidence)
        """
        if z_score > 3.0:
            return 'critical'
        elif z_score > 2.5:
            return 'warning'
        else:
            return 'info'
    
    def detect_recent_anomalies(self, metric: str, days: int = 1) -> List[Dict]:
        """
        Detect anomalies in the most recent N days only
        Useful for "what's wrong today" analysis
        """
        if 'date' not in self.df.columns or metric not in self.df.columns:
            return []
        
        recent_date = self.df['date'].max() - timedelta(days=days)
        recent_data = self.df[self.df['date'] >= recent_date]
        
        anomalies = []
        z_scores = self.calculate_z_scores(metric)
        
        for idx in recent_data.index:
            if idx in z_scores.index:
                z_score = z_scores[idx]
                if z_score > self.z_score_threshold:
                    value = self.df.loc[idx, metric]
                    date = self.df.loc[idx, 'date']
                    severity = self._calculate_severity(z_score)
                    mean = self.df[metric].mean()
                    pct_change = ((value - mean) / mean * 100) if mean != 0 else 0
                    
                    anomaly = {
                        'date': date,
                        'metric': metric,
                        'value': value,
                        'z_score': z_score,
                        'severity': severity,
                        'pct_change': pct_change,
                        'text': f"[{date.strftime('%Y-%m-%d')}] {metric}: {pct_change:+.1f}%"
                    }
                    anomalies.append(anomaly)
        
        return anomalies
    
    def detect_all_anomalies(self, metrics_to_check: List[str] = None) -> Dict[str, List[Dict]]:
        """
        Detect anomalies across multiple metrics
        metrics_to_check: list of column names to analyze
                         if None, will auto-detect numeric columns
        """
        if metrics_to_check is None:
            # Auto-detect numeric columns (excluding date)
            metrics_to_check = [col for col in self.df.select_dtypes(include=[np.number]).columns]
        
        all_anomalies = {}
        
        for metric in metrics_to_check:
            anomalies = self.detect_anomalies_by_metric(metric)
            if anomalies:
                all_anomalies[metric] = anomalies
        
        self.anomalies = [anom for anomaly_list in all_anomalies.values() for anom in anomaly_list]
        return all_anomalies
    
    def get_critical_anomalies(self) -> List[Dict]:
        """Get only CRITICAL level anomalies"""
        return [a for a in self.anomalies if a.get('severity') == 'critical']
    
    def get_top_anomalies(self, n: int = 5, severity: str = None) -> List[Dict]:
        """
        Get top N anomalies by Z-score
        severity: filter by 'critical', 'warning', 'info', or None for all
        """
        filtered = self.anomalies
        
        if severity:
            filtered = [a for a in filtered if a.get('severity') == severity]
        
        # Sort by Z-score descending
        sorted_anomalies = sorted(filtered, key=lambda x: x.get('z_score', 0), reverse=True)
        
        return sorted_anomalies[:n]
    
    def generate_anomaly_insights(self) -> List[Dict]:
        """
        Generate human-readable insights from detected anomalies
        """
        insights = []
        
        # Group by severity
        critical = [a for a in self.anomalies if a.get('severity') == 'critical']
        warnings = [a for a in self.anomalies if a.get('severity') == 'warning']
        
        if critical:
            insight = {
                'type': 'critical_anomalies',
                'count': len(critical),
                'text': f"🚨 CRITICAL: {len(critical)} critical anomaly/ies detected requiring immediate investigation"
            }
            insights.append(insight)
            
            # Top critical
            top_critical = sorted(critical, key=lambda x: x.get('z_score', 0), reverse=True)[0]
            insight = {
                'type': 'top_critical_detail',
                'detail': top_critical,
                'text': f"Most critical: {top_critical['text']}"
            }
            insights.append(insight)
        
        if warnings:
            insight = {
                'type': 'warning_anomalies',
                'count': len(warnings),
                'text': f"⚠️  WARNING: {len(warnings)} warning-level anomaly/ies detected"
            }
            insights.append(insight)
        
        # Metric-specific insights
        metrics_affected = {}
        for anomaly in self.anomalies:
            metric = anomaly.get('metric')
            if metric not in metrics_affected:
                metrics_affected[metric] = []
            metrics_affected[metric].append(anomaly)
        
        for metric, anomaly_list in metrics_affected.items():
            if len(anomaly_list) > 0:
                avg_pct = np.mean([abs(a.get('pct_change', 0)) for a in anomaly_list])
                insight = {
                    'type': f'metric_{metric}',
                    'metric': metric,
                    'count': len(anomaly_list),
                    'avg_deviation': avg_pct,
                    'text': f"{metric}: {len(anomaly_list)} anomaly/ies detected (avg deviation: {avg_pct:.1f}%)"
                }
                insights.append(insight)
        
        return insights
    
    def generate_anomaly_recommendations(self) -> List[Dict]:
        """
        Generate actionable recommendations based on anomalies
        """
        recommendations = []
        
        critical = self.get_critical_anomalies()
        
        if critical:
            rec = {
                'type': 'urgent_investigation',
                'priority': 'critical',
                'text': f"Urgent: Investigate {len(critical)} critical anomaly(ies). These represent extreme deviations from normal performance."
            }
            recommendations.append(rec)
        
        # By metric recommendations
        by_metric = {}
        for anomaly in self.anomalies:
            metric = anomaly.get('metric')
            if metric not in by_metric:
                by_metric[metric] = []
            by_metric[metric].append(anomaly)
        
        for metric, anomalies_list in by_metric.items():
            if len(anomalies_list) > 2:
                rec = {
                    'type': f'recurring_anomaly_{metric}',
                    'priority': 'high',
                    'metric': metric,
                    'text': f"Recurring issue: {metric} has shown {len(anomalies_list)} anomalies. Investigate root cause systematically."
                }
                recommendations.append(rec)
        
        # Spike vs drop recommendations
        for anomaly in critical[:3]:  # Top 3 critical
            if anomaly.get('pct_change', 0) > 0:
                rec = {
                    'type': 'spike_investigation',
                    'priority': 'high',
                    'detail': anomaly,
                    'text': f"Positive spike in {anomaly['metric']}: Identify what drove the increase and replicate."
                }
            else:
                rec = {
                    'type': 'drop_investigation',
                    'priority': 'critical',
                    'detail': anomaly,
                    'text': f"Performance drop in {anomaly['metric']}: Identify and fix the root cause immediately."
                }
            recommendations.append(rec)
        
        return recommendations
    
    def get_summary(self) -> Dict:
        """Generate comprehensive anomaly detection summary"""
        critical_count = len(self.get_critical_anomalies())
        warning_count = len([a for a in self.anomalies if a.get('severity') == 'warning'])
        info_count = len([a for a in self.anomalies if a.get('severity') == 'info'])
        
        summary = {
            'total_anomalies': len(self.anomalies),
            'critical': critical_count,
            'warning': warning_count,
            'info': info_count,
            'anomalies': self.anomalies,
            'top_anomalies': self.get_top_anomalies(5),
            'insights': self.generate_anomaly_insights(),
            'recommendations': self.generate_anomaly_recommendations()
        }
        
        return summary
    
    def analyze_all(self, metrics_to_check: List[str] = None) -> Dict:
        """
        Run complete anomaly detection
        """
        print("🚨 Detecting anomalies...")
        
        anomaly_dict = self.detect_all_anomalies(metrics_to_check)
        print(f"✓ Detected {len(self.anomalies)} total anomalies")
        
        insights = self.generate_anomaly_insights()
        print(f"✓ Generated {len(insights)} insights")
        
        recommendations = self.generate_anomaly_recommendations()
        print(f"✓ Generated {len(recommendations)} recommendations")
        
        summary = self.get_summary()
        print("✓ Anomaly detection complete")
        
        return summary


# =====================
# USAGE EXAMPLE
# =====================

if __name__ == "__main__":
    # Load combined data (from Step 1 + Step 2)
    combined_df = pd.read_csv('combined_data.csv')
    
    # Initialize anomaly detector
    detector = AnomalyDetector(combined_df, z_score_threshold=2.0, lookback_days=7)
    
    # Run all detection
    anomaly_summary = detector.analyze_all(
        metrics_to_check=['ctr', 'conversions', 'revenue', 'cpc', 'roas']
    )
    
    # Print results
    print("\n" + "="*60)
    print("🚨 ANOMALY DETECTION SUMMARY")
    print("="*60)
    
    print(f"\n📊 Anomaly Count:")
    print(f"  • Total Anomalies: {anomaly_summary['total_anomalies']}")
    print(f"  • 🚨 Critical: {anomaly_summary['critical']}")
    print(f"  • ⚠️  Warning: {anomaly_summary['warning']}")
    print(f"  • ℹ️  Info: {anomaly_summary['info']}")
    
    print(f"\n🔝 Top 5 Anomalies:")
    for i, anom in enumerate(anomaly_summary['top_anomalies'], 1):
        print(f"  {i}. {anom['text']}")
    
    print(f"\n💡 Key Insights:")
    for insight in anomaly_summary['insights'][:5]:
        print(f"  • {insight['text']}")
    
    print(f"\n🎯 Recommendations:")
    for rec in anomaly_summary['recommendations'][:5]:
        print(f"  • [{rec['priority'].upper()}] {rec['text']}")
    
    # Export anomalies to CSV for audit trail
    if anomaly_summary['total_anomalies'] > 0:
        anomalies_df = pd.DataFrame(anomaly_summary['anomalies'])
        anomalies_df.to_csv('detected_anomalies.csv', index=False)
        print(f"\n✓ Anomalies exported to detected_anomalies.csv")
