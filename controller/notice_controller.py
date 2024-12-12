from app import app
from flask import jsonify,request
from model.notice_model import notice_model
from model.user_model import user_model

obj = notice_model()
userObj=user_model()

@app.route('/notice/create', methods=['POST'])
def create_notice():
    """
    API to create a new notice.
    """
    try:
        # Extract JSON data from the request
        data = request.json

        # Validate required fields (without added_by, as it comes from the token)
        required_fields = ['title', 'description', 'status', 'date', 'variable']
        if not all(field in data for field in required_fields):
            return jsonify({'status': 'FAILED', 'error': 'All fields except added_by are required'}), 400

        title = data['title']
        description = data['description']
        status = data['status']
        date = data['date']
        variable = data['variable']

        # Extract token from headers
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'status': 'FAILED', 'error': 'Authorization token is required'}), 401

        # Verify the token and extract user information
        user = userObj.verify_token(token)  # Assuming `userObj.verify_token` is implemented
        if not user:
            return jsonify({'status': 'FAILED', 'error': 'Invalid or expired token'}), 401

        added_by = user['email']  # Extract `added_by` from the token payload (e.g., email)

        # Validate status
        if status not in [0, 1]:
            return jsonify({'status': 'FAILED', 'error': 'Invalid status. Must be 0 or 1.'}), 400

        # Validate variable
        valid_variables = ['teachers', 'students', 'all', 'admins']
        if variable not in valid_variables:
            return jsonify({'status': 'FAILED', 'error': f'Invalid variable. Must be one of {valid_variables}'}), 400

        # Call the model to insert the notice
        result = obj.create_notice(title, description, status, date, variable, added_by)

        if result['status'] == 'OK':
            return jsonify({'status': 'OK', 'message': 'Notice created successfully'}), 201
        else:
            return jsonify({'status': 'FAILED', 'error': result['message']}), 500
    except Exception as e:
        return jsonify({'status': 'FAILED', 'error': str(e)}), 500
@app.route('/notices/<string:variable>', methods=['GET'])
def get_notices_by_variable(variable):
    """
    API to fetch notices based on the variable (e.g., teachers, students, admins, all).
    """
    try:
        # Validate the variable
        valid_variables = ['teachers', 'students', 'all', 'admins']
        if variable not in valid_variables:
            return jsonify({'status': 'FAILED', 'error': f'Invalid variable. Must be one of {valid_variables}'}), 400

        # Fetch notices from the model
        notices = obj.get_notices_by_variable(variable)

        if notices['status'] == 'OK':
            return jsonify({'status': 'OK', 'message': 'Notices fetched successfully', 'response': notices['data']}), 200
        else:
            return jsonify({'status': 'FAILED', 'error': notices['message']}), 500
    except Exception as e:
        return jsonify({'status': 'FAILED', 'error': str(e)}), 500

