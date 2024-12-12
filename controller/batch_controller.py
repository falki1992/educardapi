from app import app
from flask import request, jsonify,session
from model.batch_model import batch_model
from datetime import timedelta
import base64
from werkzeug.utils import secure_filename
import os
import re

UPLOAD_FOLDER = 'uploads/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
batch_model = batch_model()




@app.route('/batches', methods=['POST'])
def create_batch():
    data = request.json
    required_fields = ['name', 'start_date', 'end_date', 'start_time', 'end_time', 'description', 'batch_image', 'no_of_student']

    # Check for missing fields
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({'error': 'Missing required fields', 'missing_fields': missing_fields}), 400

    # Handle Base64 image
    try:
        batch_image_base64 = data['batch_image']

        # Strip the prefix if present
        match = re.match(r'data:image/(.*?);base64,', batch_image_base64)
        if match:
            batch_image_base64 = batch_image_base64.split(',')[1]

        # Decode the Base64 string
        batch_image_data = base64.b64decode(batch_image_base64)

        # Save the decoded image to a file
        filename = secure_filename(f"{data['name']}_batch_image.jpeg")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        with open(filepath, "wb") as image_file:
            image_file.write(batch_image_data)

        # Construct the full URL for the saved image
        batch_image_url = f"{request.host_url}{app.config['UPLOAD_FOLDER']}{filename}"

    except Exception as e:
        return jsonify({'error': f"Failed to process image: {str(e)}"}), 500

    # Create the batch in the database
    batch_id = batch_model.create_batch(
        data['name'], data['start_date'], data['end_date'], data['start_time'], data['end_time'],
        data['description'], batch_image_url, data['no_of_student']
    )

    if isinstance(batch_id, str):  # Error occurred
        return jsonify({'error': batch_id}), 500

    return jsonify({
        'status': 'OK',
        'message': 'Batch created successfully',
        'batch_id': batch_id,
        'batch_image_url': batch_image_url
    }), 201

@app.route('/batches', methods=['GET'])
def get_all_batches():
    batches = batch_model.get_all_batches()
    if isinstance(batches, str):  # Error occurred
        return jsonify({'error': batches}), 500
    # Return successful response
    return jsonify({
        'status': 'OK',
        'message': 'Classes retrieved successfully',  # Updated message
        'response': batches , # Adjusted to match the table name conceptually

    }), 200


@app.route('/batches/<int:batch_id>', methods=['GET'])
def get_batch(batch_id):
    batch = batch_model.get_batch_by_id(batch_id)
    if isinstance(batch, str):  # Error occurred
        return jsonify({'error': batch}), 500
    if not batch:
        return jsonify({'error': 'Batch not found'}), 404
    return jsonify({'status': 'OK', 'message': 'Batch retrieved successfully', 'batch': batch}), 200



@app.route('/batches/<int:batch_id>', methods=['PUT'])
def update_batch(batch_id):
    data = request.json
    required_fields = ['name', 'start_date', 'end_date', 'start_time', 'end_time', 'description', 'batch_image', 'no_of_student']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    rows_affected = batch_model.update_batch(
        batch_id, data['name'], data['start_date'], data['end_date'], data['start_time'],
        data['end_time'], data['description'], data['batch_image'], data['no_of_student']
    )
    if isinstance(rows_affected, str):  # Error occurred
        return jsonify({'error': rows_affected}), 500
    if rows_affected == 0:
        return jsonify({'error': 'Batch not found'}), 404
    return jsonify({'message': 'Batch updated successfully'}), 200


@app.route('/batches/<int:batch_id>', methods=['DELETE'])
def delete_batch(batch_id):
    rows_affected = batch_model.delete_batch(batch_id)
    if isinstance(rows_affected, str):  # Error occurred
        return jsonify({'error': rows_affected}), 500
    if rows_affected == 0:
        return jsonify({'error': 'Batch not found'}), 404
    return jsonify({'message': 'Batch deleted successfully'}), 200


if __name__ == '__main__':
    app.run(debug=True)
