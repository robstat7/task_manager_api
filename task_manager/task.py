from flask import (
    Blueprint, request, jsonify
)
from werkzeug.exceptions import abort

from flask_jwt_extended import jwt_required, get_jwt_identity

from task_manager.db import get_db

bp = Blueprint('task', __name__)


STATUS = ['pending', 'completed']


@bp.route('/api/tasks', methods=['GET', 'POST'])
@jwt_required()
def manage_tasks():
    current_user_id = int(get_jwt_identity())

    if request.method == 'GET':
        db = get_db()
        tasks = db.execute(
            'SELECT id, title, status'
            ' FROM task WHERE user_id = ?'
            ' ORDER BY id DESC',
            (current_user_id,)
        ).fetchall()

        tasks_list = [
                      {'task_id': task['id'],
                       'task_title': task['title'],
                       'task_status': task['status']
                       }
                      for task in tasks]

        return (jsonify(tasks_list), 200)

    else:
        title = request.json.get('title')

        if not title:
            return (jsonify({"error": "Title is required"}), 400)
        else:
            db = get_db()
            new_task_cursor = db.execute(
                'INSERT INTO task (title, user_id)'
                ' VALUES (?, ?)',
                (title, current_user_id)
            )
            db.commit()

            result = {"message": "Task added successfully",
                      "task_id": new_task_cursor.lastrowid,
                      "task_title": title,
                      "task_status": "pending"
                     }

            return (jsonify(result), 201)


def get_task(id):
    task = get_db().execute(
        'SELECT id, title, status, user_id'
        ' FROM task'
        ' WHERE id = ?',
        (id,)
    ).fetchone()

    if task is None:
        abort(404, f"Task id {id} doesn't exist.")

    return task 


@bp.route('/api/tasks/<int:id>', methods=['PATCH', 'DELETE'])
@jwt_required()
def update_or_delete_tasks(id):
    current_user_id = int(get_jwt_identity())

    task = get_task(id)

    if task["user_id"] != current_user_id:
        return (jsonify({"error": "Not your task"}), 403)

    if request.method == 'PATCH':
        title = request.json.get('title')

        if not title:
            return (jsonify({"error": "Title is required"}), 400)
        else:
            db = get_db()
            db.execute(
                'UPDATE task SET title = ?'
                ' WHERE id = ?',
                (title, id)
            )
            db.commit()

            result = {"message": "Task title updated successfully",
                      "task_id": id,
                      "task_title": title,
                      "task_status": task["status"]
                     }

            return (jsonify(result), 200)

    else:
        db = get_db()
        db.execute('DELETE FROM task WHERE id = ?', (id,))
        db.commit()


        result = {"message": "Task deleted successfully",
                  "task_id": id,
                  "task_title": task["title"],
                  "task_status": task["status"]
                  }

        return (jsonify(result), 200)


@bp.route('/api/tasks/<int:id>/status', methods=['PATCH'])
@jwt_required()
def update_task_status(id):
    current_user_id = int(get_jwt_identity())

    task = get_task(id)

    if task["user_id"] != current_user_id:
        return (jsonify({"error": "Not your task"}), 403)


    status = request.json.get('status')

    if not status:
        return (jsonify({"error": "Status is required"}), 400)
    elif status not in STATUS:
        return (jsonify({"error": "Invalid status value"}), 422)
    else:
        db = get_db()
        db.execute(
            'UPDATE task SET status = ?'
            ' WHERE id = ?',
            (status, id)
            )
        db.commit()

        result = {"message": "Task status updated successfully",
                  "task_id": id,
                  "task_title": task["title"],
                  "task_status": status
                 }

        return (jsonify(result), 200)
