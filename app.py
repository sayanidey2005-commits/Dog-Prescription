from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import os
from werkzeug.utils import secure_filename
import prescription_model as pm
from datetime import datetime, timedelta
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/detection')
def detection():
    return render_template('detection.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/analyze_prescription', methods=['POST'])
def analyze_prescription():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            logger.info(f"Processing file: {filename}")
            
            # Analyze prescription
            analysis_result = pm.analyze_prescription(filepath)
            logger.info(f"Analysis completed: {len(analysis_result.get('medications', []))} medications found")
            
            # Generate diet recommendations
            diet_plan = pm.generate_diet_recommendations(analysis_result)
            logger.info("Diet recommendations generated")
            
            # Combine results
            final_result = {
                'prescription_analysis': analysis_result,
                'diet_recommendations': diet_plan,
                'uploaded_file': filename,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            # Clean up uploaded file after processing
            try:
                os.remove(filepath)
                logger.info(f"Cleaned up file: {filename}")
            except Exception as e:
                logger.warning(f"Could not remove file {filename}: {str(e)}")
            
            return jsonify(final_result)
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            return jsonify({'error': f'Analysis failed: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/contact_submit', methods=['POST'])
def contact_submit():
    try:
        data = request.get_json()
        name = data.get('name', '')
        email = data.get('email', '')
        subject = data.get('subject', '')
        message = data.get('message', '')
        
        # Here you would typically:
        # 1. Save to database
        # 2. Send email notification
        # 3. Process the contact form
        
        logger.info(f"Contact form submitted: {subject} from {name} ({email})")
        
        return jsonify({
            'success': True,
            'message': 'Thank you for your message! We will get back to you within 24 hours.'
        })
        
    except Exception as e:
        logger.error(f"Contact form error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Sorry, there was an error sending your message. Please try again.'
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)