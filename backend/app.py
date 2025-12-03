from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS 
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

# ✅ INITIALIZE FLASK FIRST
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['REPORTS_FOLDER'] = 'reports'

# Create folders
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['REPORTS_FOLDER'], exist_ok=True)

# ✅ IMPORT MODULES AFTER APP EXISTS
try:
    from pipeline import DataPipeline
    from kpi_calculator import KPICalculator
    from weather_analyzer import WeatherAnalyzer
    from anomaly_detector import AnomalyDetector
    from benchmarking import BenchmarkAnalyzer
    from report_builder import ReportBuilder
    print("✓ All backend modules imported successfully")
except ImportError as e:
    print(f"⚠️ Import error: {e}")

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ============================================
# ROUTES - Define after app initialized
# ============================================

@app.route('/')
def serve_index():
    """Serve main HTML page"""
    try:
        return send_from_directory('../frontend', 'index.html')
    except:
        return jsonify({'error': 'Frontend not found. Check file path.'}), 404


@app.route('/status', methods=['GET'])
def status():
    """Health check"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/upload', methods=['POST'])
def upload_and_generate():
    """Main endpoint: Upload CSVs and generate complete report"""
    
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files uploaded'}), 400
        
        files = request.files.getlist('files')
        client_name = request.form.get('client_name', 'Client')
        
        if not files or all(f.filename == '' for f in files):
            return jsonify({'error': 'No files selected'}), 400
        
        print(f"\n📥 Received {len(files)} files from client: {client_name}")
        
        # Save uploaded files
        upload_paths = {}
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                upload_paths[filename] = filepath
                print(f"  ✓ Saved: {filename}")
        
        if not upload_paths:
            return jsonify({'error': 'No valid CSV files uploaded'}), 400
        
        # =========================================
        # STEP 1: Data Pipeline
        # =========================================
        print("\n[STEP 1] Running Data Pipeline...")
        pipeline = DataPipeline(upload_paths)
        combined_df = pipeline.merge_all_data()
        print(f"  ✓ Combined {len(combined_df)} rows")
        
        # =========================================
        # STEP 2: KPI Calculation
        # =========================================
        print("\n[STEP 2] Calculating KPIs...")
        kpi_calc = KPICalculator(combined_df)
        kpi_summary = kpi_calc.calculate_all()
        print(f"  ✓ KPIs calculated")
        
        # =========================================
        # STEP 3: Weather Analysis
        # =========================================
        print("\n[STEP 3] Weather Analysis...")
        weather_analyzer = WeatherAnalyzer(combined_df)
        weather_summary = {}
        if weather_analyzer.check_weather_data_available():
            weather_summary = weather_analyzer.analyze_all()
            print(f"  ✓ Weather analysis complete")
        else:
            print(f"  ⚠️ No weather data available")
        
        # =========================================
        # STEP 4: Anomaly Detection
        # =========================================
        print("\n[STEP 4] Anomaly Detection...")
        anomaly_detector = AnomalyDetector(combined_df)
        anomaly_summary = anomaly_detector.analyze_all()
        print(f"  ✓ Found {anomaly_summary.get('total_anomalies', 0)} anomalies")
        
        # =========================================
        # STEP 5: Benchmarking
        # =========================================
        print("\n[STEP 5] Benchmarking...")
        bench_analyzer = BenchmarkAnalyzer(kpi_summary)
        bench_summary = bench_analyzer.analyze_all()
        print(f"  ✓ Benchmarking complete")
        
        # =========================================
        # STEP 6: Report Generation
        # =========================================
        print("\n[STEP 6] Generating PDF Report...")
        report_builder = ReportBuilder(client_name=client_name)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"InsightGen_Report_{timestamp}.pdf"
        report_path = os.path.join(app.config['REPORTS_FOLDER'], report_filename)
        
        report_builder.generate_pdf(
            report_path,
            kpi_summary=kpi_summary,
            weather_summary=weather_summary,
            anomaly_summary=anomaly_summary,
            bench_summary=bench_summary
        )
        print(f"  ✓ Report saved: {report_filename}")
        
        # =========================================
        # Return Success
        # =========================================
        return jsonify({
            'status': 'success',
            'message': 'Report generated successfully',
            'client_name': client_name,
            'report_file': report_filename,
            'summary': {
                'kpis': {
                    'total_conversions': kpi_summary['overall'].get('total_conversions'),
                    'total_revenue': kpi_summary['overall'].get('total_revenue'),
                    'avg_ctr': kpi_summary['overall'].get('ctr'),
                    'avg_roas': kpi_summary['overall'].get('roas')
                },
                'anomalies': {
                    'total': anomaly_summary.get('total_anomalies', 0),
                    'critical': anomaly_summary.get('critical', 0)
                },
                'benchmarking': {
                    'strengths': len(bench_summary.get('strengths', []))
                }
            }
        })
    
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'error': 'File too large. Maximum: 50MB'}), 413


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════════════╗
    ║         🚀 InsightGen API Server           ║
    ║     Automated Performance Report Gen        ║
    ╚════════════════════════════════════════════╝
    
    🌐 Frontend: http://localhost:5000
    📡 API: http://localhost:5000/upload
    
    """)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
