from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
import json
import os
import uuid
import shutil
import qrcode 
from io import BytesIO  

app = Flask(__name__)
FORMS_DIR = 'forms'
RESPONSES_DIR = 'responses'
QR_CODES_DIR = 'static/qrcodes'  


# CHECKS IF EXISITING ANG FOLDERS
os.makedirs(FORMS_DIR, exist_ok=True)
os.makedirs(RESPONSES_DIR, exist_ok=True)
os.makedirs(QR_CODES_DIR, exist_ok=True)  



def generate_unique_id():
    return str(uuid.uuid4())



def load_form(form_id):
    filepath = os.path.join(FORMS_DIR, f'{form_id}.json')
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None


# Saving and making the form json
def save_form(form_data):
    form_id = generate_unique_id()
    filepath = os.path.join(FORMS_DIR, f'{form_id}.json')
    with open(filepath, 'w') as f:
        json.dump(form_data, f, indent=4)
    return form_id



# saving response... STILL IN PROGRESS NOT WORKING
def save_response(form_id, response_data):
    """Saves the form response to a JSON file."""
    form_responses_dir = os.path.join(RESPONSES_DIR, form_id)
    os.makedirs(form_responses_dir, exist_ok=True) 
    response_id = generate_unique_id()
    filepath = os.path.join(form_responses_dir, f'{response_id}.json')
    try:  
        with open(filepath, 'w') as f:
            json.dump(response_data, f, indent=4)
        return True  
    except Exception as e:
        print(f"Error saving response: {e}")  
        return False  



# This one checks if may response and show sa dashboard
def get_form_responses(form_id):
    responses = []
    form_responses_dir = os.path.join(RESPONSES_DIR, form_id)
    if os.path.exists(form_responses_dir):
        for filename in os.listdir(form_responses_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(form_responses_dir, filename)
                with open(filepath, 'r') as f:
                    responses.append(json.load(f))
    return responses


# delete form data
def delete_form_data(form_id):
    form_filepath = os.path.join(FORMS_DIR, f'{form_id}.json')
    responses_dir = os.path.join(RESPONSES_DIR, form_id)
    try:
        os.remove(form_filepath)
    except FileNotFoundError:
        pass
    try:
        shutil.rmtree(responses_dir)
    except FileNotFoundError:
        pass
    # Delete associated QR code
    qr_code_path = os.path.join(QR_CODES_DIR, f'form_{form_id}.png')
    try:
        os.remove(qr_code_path)
    except FileNotFoundError:
        pass


# creates the qr code. NOTICE, COPY PASTE NI HEHE
def generate_qr_code(form_id):
    """
    Generates a QR code for the form URL and saves it to a file.

    Args:
        form_id (str): The ID of the form.

    Returns:
        str: The filename of the generated QR code image.
    """
    
    
    form_url = url_for('display_form', form_id=form_id, _external=True)  # Get the full URL
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(form_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    qr_code_filename = f'form_{form_id}.png'
    qr_code_path = os.path.join(QR_CODES_DIR, qr_code_filename)
    img.save(qr_code_path)
    return qr_code_filename

# FROM THIS ONWARDS PURO NA INI SERVER..... SI PAG ROUTE NA NI KANG MGA WEB SA SERVER WEB. DO NOT TOUCH AKO NA BAHALA DITO 
@app.route('/admin/dashboard')
def admin_dashboard():
    forms = []
    for filename in os.listdir(FORMS_DIR):
        if filename.endswith('.json'):
            form_id = filename[:-5]
            form_data = load_form(form_id)
            response_count = len(get_form_responses(form_id))
            qr_code_filename = f'form_{form_id}.png'  # default
            qr_code_path = os.path.join(QR_CODES_DIR, qr_code_filename)
            if not os.path.exists(qr_code_path):
                qr_code_filename = generate_qr_code(form_id)
            if form_data and 'name' in form_data:
                forms.append({
                    'id': form_id,
                    'name': form_data['name'],
                    'response_count': response_count,
                    'qr_code_filename': qr_code_filename,  # Pass the filename to the template
                })
    return render_template('admin_dashboard.html', forms=forms)


@app.route('/admin/create')
def create_form():
    return render_template('create_form.html')


@app.route('/admin/save_form', methods=['POST'])
def save_form_route():
    form_data = request.get_json()
    if form_data and 'questions' in form_data and 'name' in form_data:
        form_id = save_form(form_data)
        qr_code_filename = generate_qr_code(form_id)  # Generate QR code on form creation
        return jsonify({'success': True, 'form_id': form_id, 'qr_code_filename': qr_code_filename})  # Return filename
    return jsonify({'success': False, 'error': 'Invalid form data'}), 400


@app.route('/admin/forms/<form_id>/responses')
def view_responses(form_id):
    form_data = load_form(form_id)
    responses = get_form_responses(form_id)
    if form_data:
        return render_template('view_responses.html', form=form_data, responses=responses)
    return "Form not found", 404


@app.route('/admin/forms/<form_id>/responses/<response_id>')
def view_individual_response(form_id, response_id):
    form_responses_dir = os.path.join(RESPONSES_DIR, form_id)
    filepath = os.path.join(form_responses_dir, f'{response_id}.json')
    try:
        with open(filepath, 'r') as f:
            response = json.load(f)
            form_data = load_form(form_id)
            return render_template('view_individual_response.html', form=form_data, response=response)
    except FileNotFoundError:
        return "Response not found", 404


@app.route('/admin/forms/<form_id>/delete', methods=['POST'])
def delete_form(form_id):
    delete_form_data(form_id)
    return redirect(url_for('admin_dashboard'))


@app.route('/forms/<form_id>')
def display_form(form_id):
    form_data = load_form(form_id)
    if form_data:
        return render_template('display_form.html', form=form_data)
    return "Form not found", 404


@app.route('/submit_form/<form_id>', methods=['POST'])
def submit_form(form_id):
    """Handles form submission and saves response data."""
    answers = request.form.to_dict()
    success = save_response(form_id, answers)
    if success:
        return "Thank you for your submission!"
    else:
        return "Failed to save your submission. Please try again.", 500


@app.route('/admin/qrcodes/<filename>')
def serve_qr_code(filename):
    """
    Serves the QR code image file.

    Args:
        filename (str): The name of the QR code image file.

    Returns:
        Response: The QR code image file as a response.
    """
    return send_file(os.path.join(QR_CODES_DIR, filename), mimetype='image/png')




if __name__ == '__main__':
    app.run(debug=True)
