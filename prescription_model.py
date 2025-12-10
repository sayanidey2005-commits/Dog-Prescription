import pytesseract
from PIL import Image
import re
import json
from datetime import datetime
import pandas as pd
import logging
import os
import io

logger = logging.getLogger(__name__)

class PrescriptionAnalyzer:
    def __init__(self):
        self.medication_keywords = {
            'antibiotics': ['amoxicillin', 'cephalexin', 'doxycycline', 'enrofloxacin', 'metronidazole'],
            'pain_relievers': ['carprofen', 'meloxicam', 'gabapentin', 'tramadol', 'aspirin'],
            'allergy_meds': ['cetirizine', 'diphenhydramine', 'prednisone', 'cytopoint', 'apoquel'],
            'parasite_control': ['ivermectin', 'milbemycin', 'praziquantel', 'selamectin', 'fipronil'],
            'supplements': ['glucosamine', 'omega-3', 'probiotics', 'cosequin', 'dasuquin'],
            'heart_meds': ['enalapril', 'furosemide', 'pimobendan'],
            'eye_meds': ['ophthalmic', 'gentamicin', 'tobramycin']
        }
        
        self.conditions_keywords = {
            'infection': ['infection', 'bacterial', 'viral', 'fever', 'uti', 'ear infection'],
            'arthritis': ['arthritis', 'joint pain', 'lameness', 'osteoarthritis', 'hip dysplasia'],
            'allergy': ['allergy', 'itching', 'skin irritation', 'atopy', 'dermatitis'],
            'dental': ['dental', 'gingivitis', 'tooth', 'periodontal', 'tartar'],
            'digestive': ['diarrhea', 'vomiting', 'digestive', 'stomach', 'gi', 'pancreatitis'],
            'respiratory': ['cough', 'kennel cough', 'pneumonia', 'breathing'],
            'cardiac': ['heart', 'cardiac', 'murmur', 'chf']
        }

    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF using PyMuPDF (fitz) - No Poppler required!"""
        try:
            logger.info("Extracting text from PDF using PyMuPDF")
            
            # Method 1: Try PyMuPDF first (direct text extraction)
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(pdf_path)
                text = ""
                
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    page_text = page.get_text()
                    text += f"\n--- Page {page_num + 1} ---\n{page_text}"
                
                doc.close()
                
                if text.strip():
                    logger.info("✅ Successfully extracted text using PyMuPDF")
                    return text
                else:
                    logger.warning("PyMuPDF extracted empty text, trying OCR method")
                    return self.extract_text_from_pdf_ocr(pdf_path)
                    
            except ImportError:
                logger.error("PyMuPDF not installed")
                return self.extract_text_from_pdf_ocr(pdf_path)
                
        except Exception as e:
            logger.error(f"PDF extraction failed: {str(e)}")
            # Try OCR as last resort
            return self.extract_text_from_pdf_ocr(pdf_path)

    def extract_text_from_pdf_ocr(self, pdf_path):
        """Extract text from PDF using OCR - requires converting PDF to images first"""
        try:
            logger.info("Using OCR method for PDF extraction")
            
            # Try multiple methods to convert PDF to images
            images = self.convert_pdf_to_images(pdf_path)
            
            if not images:
                raise Exception("Could not convert PDF to images")
            
            text = ""
            for i, image in enumerate(images):
                logger.info(f"OCR processing page {i+1}")
                page_text = pytesseract.image_to_string(image)
                text += f"\n--- Page {i+1} ---\n{page_text}"
            
            return text
            
        except Exception as e:
            logger.error(f"OCR PDF processing failed: {str(e)}")
            raise Exception(f"PDF processing failed. Please convert your PDF to images and upload those instead. Error: {str(e)}")

    def convert_pdf_to_images(self, pdf_path):
        """Convert PDF to images using available libraries"""
        images = []
        
        # Method 1: Try pdf2image with Poppler (if available)
        try:
            import pdf2image
            images = pdf2image.convert_from_path(pdf_path, dpi=200)
            logger.info("✅ Used pdf2image for PDF conversion")
            return images
        except:
            logger.info("pdf2image not available or failed")
        
        # Method 2: Try PyMuPDF for image conversion
        try:
            import fitz
            doc = fitz.open(pdf_path)
            images = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Higher resolution
                img_data = pix.tobytes("ppm")
                image = Image.open(io.BytesIO(img_data))
                images.append(image)
            
            doc.close()
            logger.info("✅ Used PyMuPDF for PDF to image conversion")
            return images
        except Exception as e:
            logger.error(f"PyMuPDF image conversion failed: {e}")
        
        # Method 3: Try Wand
        try:
            from wand.image import Image as WandImage
            with WandImage(filename=pdf_path, resolution=200) as img:
                for page in img.sequence:
                    with WandImage(page) as single_page:
                        single_page.format = 'png'
                        image_data = single_page.make_blob('png')
                        image = Image.open(io.BytesIO(image_data))
                        images.append(image)
            logger.info("✅ Used Wand for PDF conversion")
            return images
        except:
            logger.info("Wand not available or failed")
        
        raise Exception("No PDF to image conversion method available")

    def extract_text_from_image(self, image_path):
        """Extract text from image files"""
        try:
            logger.info("Processing image file")
            image = Image.open(image_path)
            
            # Enhance image for better OCR
            image = image.convert('L')  # Convert to grayscale
            
            # Increase image size for better OCR if too small
            if max(image.size) < 1000:
                scale_factor = 2000 / max(image.size)
                new_size = (int(image.size[0] * scale_factor), int(image.size[1] * scale_factor))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Configure Tesseract for better results
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,/-:mgML() '
            text = pytesseract.image_to_string(image, config=custom_config)
            
            return text
        except Exception as e:
            logger.error(f"Image processing failed: {str(e)}")
            raise Exception(f"Image processing failed: {str(e)}")

    def analyze_prescription_text(self, text):
        """Analyze extracted text for medications and instructions"""
        logger.info("Analyzing prescription text")
        analysis = {
            'medications': [],
            'dosage_instructions': [],
            'detected_conditions': [],
            'frequency': [],
            'duration': '',
            'special_instructions': [],
            'confidence_score': 0,
            'raw_text_sample': text[:500] + "..." if len(text) > 500 else text  # For debugging
        }
        
        # Convert text to lowercase for easier matching
        text_lower = text.lower()
        
        # Look for medication patterns
        for category, meds in self.medication_keywords.items():
            for med in meds:
                if med.lower() in text_lower:
                    analysis['medications'].append({
                        'name': med.title(),
                        'category': category,
                        'found_in_text': True
                    })
        
        # Look for conditions
        for condition, keywords in self.conditions_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    if condition not in analysis['detected_conditions']:
                        analysis['detected_conditions'].append(condition)
                    break
        
        # Extract dosage instructions with improved patterns
        dosage_patterns = [
            (r'(\d+(?:\.\d+)?)\s*mg', 'mg'),
            (r'(\d+)\s*ml', 'ml'),
            (r'(\d+)\s*tablet', 'tablet'),
            (r'(\d+)\s*capsule', 'capsule'),
            (r'every\s*(\d+)\s*hours?', 'hours'),
            (r'(\d+)\s*times? daily', 'times daily'),
            (r'once daily', 'once daily'),
            (r'twice daily', 'twice daily')
        ]
        
        for pattern, unit in dosage_patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                analysis['dosage_instructions'].append({
                    'amount': match.group(1) if match.groups() else '1',
                    'unit': unit,
                    'match': match.group(0)
                })
        
        # Extract duration
        duration_patterns = [
            r'for\s*(\d+)\s*days?',
            r'(\d+)\s*day',
            r'(\d+)\s*weeks?',
            r'(\d+)\s*months?'
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, text_lower)
            if match:
                analysis['duration'] = match.group(0)
                break
        
        # Extract special instructions
        special_patterns = [
            r'with\s*food',
            r'after\s*meals',
            r'empty\s*stomach',
            r'do\s*not\s*crush',
            r'with\s*water'
        ]
        
        for pattern in special_patterns:
            if re.search(pattern, text_lower):
                analysis['special_instructions'].append(pattern.replace('\\s*', ' '))
        
        # Calculate confidence score
        medication_score = len(analysis['medications']) * 20
        condition_score = len(analysis['detected_conditions']) * 15
        dosage_score = min(len(analysis['dosage_instructions']) * 10, 30)
        analysis['confidence_score'] = min(95, medication_score + condition_score + dosage_score)
        
        # If no medications found but we have text, provide a fallback analysis
        if not analysis['medications'] and text.strip():
            analysis['general_notes'] = ["No specific medications detected. Please verify the prescription manually."]
            analysis['confidence_score'] = max(analysis['confidence_score'], 10)
        
        logger.info(f"Analysis completed: {len(analysis['medications'])} medications, {len(analysis['detected_conditions'])} conditions, confidence: {analysis['confidence_score']}%")
        return analysis

    def generate_diet_recommendations(self, analysis):
        """Generate comprehensive diet recommendations"""
        logger.info("Generating diet recommendations")
        diet_plan = {
            'general_recommendations': [
                "Always provide fresh, clean water",
                "Monitor your dog's appetite and energy levels daily",
                "Consult your veterinarian before making major diet changes",
                "Keep a consistent feeding schedule"
            ],
            'food_suggestions': [],
            'foods_to_avoid': [
                "Chocolate, grapes, raisins, and onions",
                "Foods high in salt or sugar",
                "Fatty or spicy human foods"
            ],
            'supplements': [],
            'feeding_schedule': {
                'breakfast': "7:00-8:00 AM - Main meal with any morning supplements",
                'lunch': "12:00-1:00 PM - Light snack or puzzle toy",
                'dinner': "6:00-7:00 PM - Main meal with evening supplements",
                'medication_times': "Administer medications with meals unless otherwise directed"
            },
            'hydration_tips': [
                "Ensure fresh water is always available",
                "Add water to dry food to increase hydration",
                "Consider ice cubes as low-calorie treats"
            ]
        }
        
        conditions = analysis.get('detected_conditions', [])
        medications = [med['category'] for med in analysis.get('medications', [])]
        
        # Condition-specific recommendations
        if 'infection' in conditions:
            diet_plan['food_suggestions'].extend([
                "Boiled chicken breast (boneless, skinless)",
                "Plain pumpkin puree (for digestion)",
                "Cooked white rice (easy to digest)",
                "Low-fat cottage cheese"
            ])
            diet_plan['general_recommendations'].append("Provide extra protein to support immune system recovery")
        
        if 'arthritis' in conditions:
            diet_plan['food_suggestions'].extend([
                "Salmon or other fatty fish (rich in omega-3)",
                "Sweet potatoes (anti-inflammatory)",
                "Blueberries (antioxidants)",
                "Green beans (low-calorie filler)"
            ])
            diet_plan['supplements'].extend([
                "Glucosamine and chondroitin for joint health",
                "Fish oil capsules (omega-3 fatty acids)",
                "Turmeric (natural anti-inflammatory)"
            ])
        
        if 'digestive' in conditions:
            diet_plan['food_suggestions'].extend([
                "Boiled chicken and rice (bland diet)",
                "Plain canned pumpkin (fiber source)",
                "Boiled potatoes (no skin)",
                "Plain yogurt (probiotics)"
            ])
            diet_plan['general_recommendations'].append("Feed small, frequent meals to avoid overwhelming the digestive system")
            diet_plan['supplements'].append("Dog-specific probiotics to support gut health")
        
        if 'allergy' in conditions:
            diet_plan['food_suggestions'].extend([
                "Novel protein sources like venison or duck",
                "Limited ingredient foods",
                "Hypoallergenic treats"
            ])
            diet_plan['general_recommendations'].append("Consider an elimination diet to identify allergens")
        
        # Medication-specific adjustments
        if 'antibiotics' in medications:
            diet_plan['supplements'].append("Probiotics (give 2 hours apart from antibiotics)")
            diet_plan['general_recommendations'].append("Antibiotics may cause stomach upset - monitor closely")
        
        if 'pain_relievers' in medications:
            diet_plan['general_recommendations'].append("Always give pain medication with food to protect the stomach")
        
        # Ensure we have some food suggestions even if no specific conditions detected
        if not diet_plan['food_suggestions']:
            diet_plan['food_suggestions'].extend([
                "High-quality commercial dog food",
                "Cooked lean meats",
                "Fresh vegetables like carrots and green beans",
                "Plain, cooked eggs"
            ])
        
        logger.info("Diet recommendations generated successfully")
        return diet_plan

def analyze_prescription(file_path):
    """Main function to analyze prescription"""
    analyzer = PrescriptionAnalyzer()
    
    try:
        if file_path.lower().endswith('.pdf'):
            text = analyzer.extract_text_from_pdf(file_path)
        else:
            text = analyzer.extract_text_from_image(file_path)
        
        analysis = analyzer.analyze_prescription_text(text)
        return analysis
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise Exception(f"Analysis failed: {str(e)}")

def generate_diet_recommendations(analysis):
    """Generate diet recommendations based on analysis"""
    analyzer = PrescriptionAnalyzer()
    return analyzer.generate_diet_recommendations(analysis)