from flask import (
    Blueprint, request, jsonify
)

from task_manager.db import get_db

bp = Blueprint('task', __name__)


@bp.route('/create', methods=['POST'])
def create():
    title = request.json.get('title')

    if not title:
        return jsonify({"error": "Title is required"}), 400 
    else:
        db = get_db()
        db.execute(
            'INSERT INTO task (title)'
            ' VALUES (?)',
            (title,)
        )
        db.commit()
        return jsonify({"message": "Task added successfully"}), 201
