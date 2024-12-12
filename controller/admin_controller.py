from app import app
from flask import request, jsonify,session
from model.exam_model import exam_model
from model.user_model import user_model


# Initialize the user_model once as `obj`
obj = exam_model()
userObj= user_model()

from flask import request, jsonify

@app.route('/admin/dashboard', methods=['GET'])
def dashboard():
    token=request.headers.get('Authorization')
    print(token)
    """Fetch and return dashboard data in JSON format using token."""
    try:
        # Extract the token from the request header

        if not token:
            return jsonify({"error": "Token is missing"}), 400

        # Verify the token and get the user ID
        user = userObj.verify_token(token)
        if not user:
            return jsonify({"error": "Invalid or expired token"}), 400

        uid = user['id']  # Extract user ID from the token verification

        # Fetch Exam
        exam = obj.fetch_exam(uid)

        # Fetch Batches
        all_batches = obj.fetch_batches()

        top_three = []
        good, poor, average = 0, 0, 0
        if exam:
            # Fetch Top Three Results
            top_three = obj.fetch_top_three_results(exam['id'])

            # Fetch Result Counts (good, poor, average)
            good, poor, average = obj.fetch_result_counts(exam['id'])

        # Fetch Doubts Data
        doubts_data, doubts_data_approve, doubts_data_pending = obj.fetch_doubts_data()

        # Fetch Payment Statistics
        total_amount, offline, online = obj.fetch_payment_statistics(uid)

        # Fetch All Users
        all_users = obj.fetch_all_users()

        # Final Response
        response = {
            "title": "Dashboard",
            "exam": exam,
            "all_batches": all_batches,
            "top_three": top_three,
            "good": good,
            "poor": poor,
            "average": average,
            "doubts_data": doubts_data,
            "doubts_data_approve": doubts_data_approve,
            "doubts_data_pending": doubts_data_pending,
            "total_amount": total_amount,
            "offline": offline,
            "online": online,
            "all_users": all_users
        }

        return jsonify({'status': 'OK', 'message': 'Dashboard Data Fetch', 'response': response}), 200

    except Exception as err:
        return jsonify({"error": f"Error: {err}"}), 500
