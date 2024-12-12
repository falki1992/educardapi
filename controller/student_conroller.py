from app import app
from flask import request, jsonify
from model.student_model import student_model

obj = student_model()

@app.route('/student/register', methods=['POST'])
def student_registration():
    try:
        data = request.json
        if not obj.con:
            return jsonify({'status': 'false', 'msg': 'Database connection failed'}), 500

        response = obj.register_student(data)
        return jsonify(response), 201 if response['status'] == 'true' else 400
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'false', 'msg': 'Internal server error'}), 500
    finally:
        obj.close()
