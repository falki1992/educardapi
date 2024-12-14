from flask import request, jsonify
from model.exam_model import exam_model
from model.user_model import user_model

# Initialize the models
obj = exam_model()
userObj = user_model()

# Function to fetch dashboard data (moved outside setup_routes)
def get_dashboard_data(uid):
    exam = obj.fetch_exam(uid)
    all_batches = obj.fetch_batches()
    top_three = obj.fetch_top_three_results(exam['id']) if exam else []
    good, poor, average = obj.fetch_result_counts(exam['id']) if exam else (0, 0, 0)
    doubts_data, doubts_data_approve, doubts_data_pending = obj.fetch_doubts_data()
    total_amount, offline, online = obj.fetch_payment_statistics(uid)
    all_users = obj.fetch_all_users()

    return {
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

# Define routes
def setup_routes(app):
    @app.route('/admin/dashboard', methods=['GET'])
    def dashboard():
        token = request.headers.get('Authorization')
        print(token)
        try:
            if not token:
                return jsonify({"error": "Token is missing"}), 400

            # Verify token and get user ID
            user = userObj.verify_token(token)
            if not user:
                return jsonify({"error": "Invalid or expired token"}), 400

            uid = user['id']
            response = get_dashboard_data(uid)

            return jsonify({'status': 'OK', 'message': 'Dashboard Data Fetch', 'response': response}), 200

        except Exception as err:
            return jsonify({"error": f"Error: {err}"}), 500
