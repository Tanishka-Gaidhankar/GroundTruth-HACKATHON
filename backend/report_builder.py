import pandas as pd
import numpy as np
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT

class ReportBuilder:
    """
    Step 7: Build comprehensive PDF report from all analytics
    Combines KPI summary, weather insights, anomalies, benchmarks, and forecast
    """
    
    def __init__(self, client_name: str = "Client"):
        self.client_name = client_name
        self.generated_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        self.story = []
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomHeading1',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1B3A47'),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2D7A8F'),
            spaceAfter=8,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#333333')
        ))
    
    def add_cover_page(self):
        """Add title/cover page"""
        self.story.append(Spacer(1, 2*inch))
        
        title = Paragraph(
            f"<b>InsightGen Performance Report</b>",
            self.styles['CustomHeading1']
        )
        self.story.append(title)
        self.story.append(Spacer(1, 0.3*inch))
        
        client = Paragraph(
            f"<font size=14><b>{self.client_name}</b></font>",
            self.styles['Normal']
        )
        self.story.append(client)
        self.story.append(Spacer(1, 0.5*inch))
        
        date_para = Paragraph(
            f"<font size=11><i>Report Generated: {self.generated_time}</i></font>",
            self.styles['Normal']
        )
        self.story.append(date_para)
        self.story.append(Spacer(1, 2*inch))
        
        subtitle = Paragraph(
            "<font size=12 color=#666666>Automated Weekly Analytics with AI-Powered Insights</font>",
            self.styles['Normal']
        )
        self.story.append(subtitle)
        
        self.story.append(PageBreak())
    
    def add_kpi_table(self, kpi_summary: dict):
        """Add KPI summary table"""
        self.story.append(Paragraph(
            "Performance Metrics by Channel",
            self.styles['CustomHeading2']
        ))
        self.story.append(Spacer(1, 0.1*inch))
        
        # Build table data
        by_channel = kpi_summary.get('by_channel', {})
        table_data = [
            ['Channel', 'CTR', 'CPC', 'CVR', 'CPA', 'ROAS']
        ]
        
        for channel, metrics in by_channel.items():
            table_data.append([
                channel.capitalize(),
                f"{metrics.get('ctr', 0):.2f}%",
                f"${metrics.get('cpc', 0):.2f}",
                f"{metrics.get('cvr', 0):.2f}%",
                f"${metrics.get('cpa', 0):.2f}",
                f"{metrics.get('roas', 0):.2f}x"
            ])
        
        # Create table
        table = Table(table_data, colWidths=[1.2*inch]*6)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2D7A8F')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.3*inch))
    
    def add_weather_insights(self, weather_summary: dict):
        """Add weather analysis section"""
        if not weather_summary or not weather_summary.get('insights'):
            return
        
        self.story.append(Paragraph(
            "🌦️ Weather-Driven Insights",
            self.styles['CustomHeading2']
        ))
        self.story.append(Spacer(1, 0.1*inch))
        
        insights = weather_summary.get('insights', [])
        if insights:
            for insight in insights[:3]:
                text = f"• {insight.get('text', 'No insight available')}"
                self.story.append(Paragraph(text, self.styles['CustomBody']))
                self.story.append(Spacer(1, 0.1*inch))
        else:
            self.story.append(Paragraph(
                "No significant weather correlations detected.",
                self.styles['CustomBody']
            ))
        
        self.story.append(Spacer(1, 0.2*inch))
    
    def add_anomalies(self, anomaly_summary: dict):
        """Add anomaly detection section"""
        if not anomaly_summary or anomaly_summary.get('total_anomalies', 0) == 0:
            self.story.append(Paragraph(
                "🚨 Anomaly Detection",
                self.styles['CustomHeading2']
            ))
            self.story.append(Paragraph(
                "No significant anomalies detected.",
                self.styles['CustomBody']
            ))
            self.story.append(Spacer(1, 0.2*inch))
            return
        
        self.story.append(Paragraph(
            "🚨 Anomalies Detected",
            self.styles['CustomHeading2']
        ))
        self.story.append(Spacer(1, 0.1*inch))
        
        summary_text = f"""
        Total Anomalies: <b>{anomaly_summary.get('total_anomalies', 0)}</b><br/>
        Critical: <b>{anomaly_summary.get('critical', 0)}</b> | 
        Warnings: <b>{anomaly_summary.get('warning', 0)}</b>
        """
        self.story.append(Paragraph(summary_text, self.styles['CustomBody']))
        self.story.append(Spacer(1, 0.15*inch))
        
        # Top anomalies
        top_anomalies = anomaly_summary.get('top_anomalies', [])
        for anom in top_anomalies[:3]:
            severity_emoji = '🚨' if anom.get('severity') == 'critical' else '⚠️'
            text = f"{severity_emoji} {anom.get('text', 'Anomaly detected')}"
            self.story.append(Paragraph(text, self.styles['CustomBody']))
            self.story.append(Spacer(1, 0.08*inch))
        
        self.story.append(Spacer(1, 0.2*inch))
    
    def add_benchmarking(self, bench_summary: dict):
        """Add benchmarking section"""
        if not bench_summary or not bench_summary.get('benchmarks_loaded'):
            return
        
        self.story.append(Paragraph(
            "📊 Competitive Benchmarking",
            self.styles['CustomHeading2']
        ))
        self.story.append(Spacer(1, 0.1*inch))
        
        overall_comp = bench_summary.get('overall_comparison', {})
        comparison_text = "<b>Your Performance vs Industry Average:</b><br/>"
        
        for metric, data in overall_comp.items():
            badge = data.get('badge', '')
            pct = data.get('pct_difference', 0)
            comparison_text += f"{metric.upper()}: {pct:+.1f}% {badge}<br/>"
        
        self.story.append(Paragraph(comparison_text, self.styles['CustomBody']))
        self.story.append(Spacer(1, 0.15*inch))
        
        # Strengths and Weaknesses
        strengths = bench_summary.get('strengths', [])
        if strengths:
            self.story.append(Paragraph("<b>💪 Key Strengths:</b>", self.styles['CustomBody']))
            for strength in strengths[:2]:
                text = f"• {strength.get('text', '')}"
                self.story.append(Paragraph(text, self.styles['CustomBody']))
                self.story.append(Spacer(1, 0.08*inch))
        
        self.story.append(Spacer(1, 0.2*inch))
    
    def add_recommendations(self, kpi_summary: dict, weather_summary: dict, 
                          anomaly_summary: dict, bench_summary: dict):
        """Add recommendations section"""
        self.story.append(PageBreak())
        self.story.append(Paragraph(
            "🎯 Recommendations & Action Items",
            self.styles['CustomHeading2']
        ))
        self.story.append(Spacer(1, 0.15*inch))
        
        recommendations = []
        
        # From benchmarking
        bench_recs = bench_summary.get('recommendations', [])
        recommendations.extend(bench_recs[:2])
        
        # From weather
        weather_recs = weather_summary.get('recommendations', [])
        recommendations.extend(weather_recs[:1])
        
        # From anomalies
        anomaly_recs = anomaly_summary.get('recommendations', [])
        recommendations.extend(anomaly_recs[:1])
        
        # Display recommendations
        for i, rec in enumerate(recommendations[:5], 1):
            priority = rec.get('priority', 'medium').upper()
            text = f"<b>{i}. [{priority}]</b> {rec.get('text', '')}"
            self.story.append(Paragraph(text, self.styles['CustomBody']))
            self.story.append(Spacer(1, 0.12*inch))
        
        self.story.append(Spacer(1, 0.3*inch))
    
    def generate_pdf(self, filepath: str, kpi_summary: dict, weather_summary: dict = None,
                    anomaly_summary: dict = None, bench_summary: dict = None):
        """Generate complete PDF report"""
        self.story = []
        
        self.add_cover_page()
        self.add_kpi_table(kpi_summary)
        
        if weather_summary:
            self.add_weather_insights(weather_summary)
        
        if anomaly_summary:
            self.add_anomalies(anomaly_summary)
        
        if bench_summary:
            self.add_benchmarking(bench_summary)
        
        self.add_recommendations(kpi_summary, weather_summary or {}, 
                                anomaly_summary or {}, bench_summary or {})
        
        # Create PDF
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        doc.build(self.story)
        
        print(f"✓ PDF report generated: {filepath}")
        return filepath
