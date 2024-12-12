from app import app
from flask import request, jsonify,session
from datetime import datetime
from model.membership_model import membership_model  # Assuming you have a model file for membership-related database operations


# Initialize the membership model
membership_model = membership_model()

@app.route('/membership/create', methods=['POST'])
def create_membership_plan():
    """
    API route to create a new membership plan.
    """
    try:
        # Get data from the request
        data = request.json

        # Validate required fields
        required_fields = ['name', 'description', 'price', 'duration_months']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'All fields are required'}), 400

        name = data['name']
        description = data['description']
        price = float(data['price'])
        duration_months = int(data['duration_months'])

        # Call the model function to insert the membership plan into the database
        result = membership_model.create_plan(name, description, price, duration_months)

        if result['status']:
            return jsonify(result), 200
        else:
            return jsonify({'error': result['message']}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/membership/all', methods=['GET'])
def get_all_memberships():
    """
    API route to fetch all membership plans.
    """
    try:
        # Call the model function to retrieve all membership plans
        memberships = membership_model.get_all_plans()

        if memberships['status'] == 'OK':  # Check the correct key
            return jsonify({
                'status': 'OK',
                'message': memberships['message'],  # Use the message from the model
                'response': memberships['response']  # Correct key for plans data
            }), 200
        else:
            return jsonify({'status': 'FAILED', 'error': memberships['message']}), 500
    except Exception as e:
        return jsonify({'status': 'FAILED', 'error': str(e)}), 500

@app.route('/membership/purchase', methods=['POST'])
def purchase_membership():
    """
    API route to purchase a membership plan for a school.
    """
    try:
        # Extract JSON data from the request
        data = request.json

        # Validate input fields
        required_fields = ['school_id', 'membership_id', 'start_date']
        if not all(field in data for field in required_fields):
            return jsonify({'status': 'FAILED', 'error': 'All fields are required'}), 400

        school_id = data['school_id']
        membership_id = data['membership_id']
        start_date = data['start_date']

        # Call the business logic to handle membership purchase
        result = membership_model.purchase_membership(school_id, membership_id, start_date)

        if result['status'] == 'OK':
            return jsonify({
                'status': 'OK',
                'message': 'Membership purchased successfully',
                'response': result['response']
            }), 201
        else:
            return jsonify({'status': 'FAILED', 'error': result['message']}), 500
    except Exception as e:
        return jsonify({'status': 'FAILED', 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
