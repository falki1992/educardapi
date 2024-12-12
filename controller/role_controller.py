from app import app
from flask import jsonify,request
from model.role_model import role_model

obj = role_model()

@app.route('/roles/getall', methods=['GET'])
def get_all_roles():
    roles = obj.get_all_roles()
    if roles:
        return jsonify({'status':'OK','message': 'Roles found','roles': roles}), 200
    else:
        return jsonify({'status':'FAILED','message': 'No roles found'}), 404

@app.route('/roles/<int:role_id>', methods=['GET'])
def get_role(role_id):
    try:
        role = obj.get_role_by_id(role_id)
        if role:
            return jsonify({'status': 'OK', 'message': 'Role found', 'role': role}), 200
        else:
            return jsonify({'status': 'FAILED', 'message': 'Role not found'}), 404
    except Exception as e:
        return jsonify({'status': 'ERROR', 'message': f'Error fetching role: {str(e)}'}), 500

@app.route('/roles/create', methods=['POST'])
def create_role():
    try:
        data = request.json
        name = data.get('name')

        if not name:
            return jsonify({'status': 'FAILED', 'message': 'Missing required fields'}), 400

        # Debugging statement to ensure data received is correct
        print(f"Creating role with name: {name}")

        role_id = obj.create_role(name)  # Assumes obj is properly initialized

        if role_id:
            return jsonify({'status': 'OK', 'message': 'Role created successfully', 'role_id': role_id}), 201
        else:
            return jsonify({'status': 'FAILED', 'message': 'Failed to create role'}), 500
    except Exception as e:
        print(f"Exception occurred: {e}")  # Log exception details for debugging
        return jsonify({'status': 'ERROR', 'message': f'Error creating role: {str(e)}'}), 500


@app.route('/roles/update/<int:role_id>', methods=['PUT'])
def update_role(role_id):
    try:
        data = request.json
        name = data.get('name')
        if not name :
            return jsonify({'status': 'FAILED', 'message': 'Missing required fields'}), 400

        rows_affected = obj.update_role(role_id, name)
        if rows_affected:
            return jsonify({'status': 'OK', 'message': 'Role updated successfully'}), 200
        else:
            return jsonify({'status': 'FAILED', 'message': 'Failed to update role or no changes made'}), 404
    except Exception as e:
        return jsonify({'status': 'ERROR', 'message': f'Error updating role: {str(e)}'}), 500

@app.route('/roles/delete/<int:role_id>', methods=['DELETE'])
def delete_role(role_id):
    try:
        rows_deleted = obj.delete_role(role_id)
        if rows_deleted:
            return jsonify({'status': 'OK', 'message': 'Role deleted successfully'}), 200
        else:
            return jsonify({'status': 'FAILED', 'message': 'Failed to delete role'}),
    except Exception as e:
        return jsonify({'status': 'ERROR', 'message': f'Error updating role: {str(e)}'}), 500
