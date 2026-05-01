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


@bp.route('/')
def index():
    db = get_db()
    tasks = db.execute(
        'SELECT id, title'
        ' FROM task'
        ' ORDER BY id DESC'
    ).fetchall()

    tasks_list = [{'task_id': task['id'], 'task_title': task['title']} for task in tasks]
    return jsonify(tasks_list), 200
