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
        tasks = None
        db = get_db()

        # get query params
        status = request.args.get('status')
        category = request.args.get('category')

        if status is None and category is None:
            tasks = db.execute(
                'SELECT id, title, description, category, status'
                ' FROM task WHERE user_id = ?'
                ' ORDER BY id DESC',
                (current_user_id,)
            ).fetchall()

        elif status is not None and status not in STATUS:
            result = {'error': 'Invalid status value.'}
            return (jsonify(result), 400)

        elif status is not None and category is not None:
            tasks = db.execute(
                'SELECT id, title, description, category, status'
                ' FROM task WHERE user_id = ? AND status = ? AND category = ?'
                ' ORDER BY id DESC',
                (current_user_id, status, category)
                ).fetchall()

        elif status is not None:
            tasks = db.execute(
                    'SELECT id, title, description, category, status'
                    ' FROM task WHERE user_id = ? AND status = ?'
                    ' ORDER BY id DESC',
                    (current_user_id, status)
                    ).fetchall()

        elif category is not None:
            tasks = db.execute(
                    'SELECT id, title, description, category, status'
                    ' FROM task WHERE user_id = ? AND category = ?'
                    ' ORDER BY id DESC',
                    (current_user_id, category)
                    ).fetchall()

        tasks_list = [
                      {'task_id': task['id'],
                       'task_title': task['title'],
                       'task_description': task['description'],
                       'task_category': task['category'],
                       'task_status': task['status']
                       }
                      for task in tasks]

        return (jsonify(tasks_list), 200)

    else:
        title = request.json.get('title')
        description = request.json.get('description')
        category = request.json.get('category')

        if not title:
            return (jsonify({"error": "Title is required"}), 400)
        else:
            db = get_db()
            new_task_cursor = db.execute(
                'INSERT INTO task (title, description, category, user_id)'
                ' VALUES (?, ?, ?, ?)',
                (title, description, category, current_user_id)
            )
            db.commit()

            result = {"message": "Task added successfully",
                      "task_id": new_task_cursor.lastrowid,
                      "task_title": title,
                      "task_description": description,
                      "task_category": category,
                      "task_status": "pending"
                     }

            return (jsonify(result), 201)


def get_task(id):
    task = get_db().execute(
        'SELECT id, title, description, category, status, user_id'
        ' FROM task'
        ' WHERE id = ?',
        (id,)
    ).fetchone()

    if task is None:
        abort(404, f"Task id {id} doesn't exist.")

    return task 


@bp.route('/api/tasks/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
@jwt_required()
def get_update_or_delete_tasks(id):
    current_user_id = int(get_jwt_identity())

    task = get_task(id)

    if task["user_id"] != current_user_id:
        return (jsonify({"error": "Not your task"}), 403)

    if request.method == 'GET':
        result = {"task_id": id,
                  "task_title": task["title"],
                  "task_description": task["description"],
                  "task_category": task["category"],
                  "task_status": task["status"]
                 }
        return (jsonify(result), 200)

    elif request.method == 'PATCH':

        if 'title' in request.json:
            if request.json['title'] is None or request.json['title'] == '':
                result = {"error":
                          "Title is required"}
                return (jsonify(result), 400)

        db = get_db()

        if 'title' in request.json and 'description' in request.json:
            db.execute(
                'UPDATE task SET title = ?, description = ?'
                ' WHERE id = ?',
                (request.json['title'], request.json['description'], id)
            )
            db.commit()

        elif 'description' in request.json:
            db.execute(
                'UPDATE task SET description = ?'
                ' WHERE id = ?',
                (request.json['description'], id)
            )
            db.commit()

        elif 'title' in request.json:
            db.execute(
                'UPDATE task SET title = ?'
                ' WHERE id = ?',
                (request.json['title'], id)
            )
            db.commit()

        updated_task = db.execute(
                'SELECT title, description, category, status'
                ' FROM task'
                ' WHERE id = ?',
                (id,)
            ).fetchone()

        result = {"message": "Task updated successfully",
                  "task_id": id,
                  "task_title": updated_task["title"],
                  "task_description": updated_task["description"],
                  "task_category": updated_task["category"],
                  "task_status": updated_task["status"]
                 }

        return (jsonify(result), 200)

    else:
        db = get_db()
        db.execute('DELETE FROM task WHERE id = ?', (id,))
        db.commit()


        result = {"message": "Task deleted successfully",
                  "task_id": id,
                  "task_title": task["title"],
                  "task_description": task["description"],
                  "task_category": task["category"],
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
                  "task_description": task["description"],
                  "task_category": task["category"],
                  "task_status": status
                 }

        return (jsonify(result), 200)


@bp.route('/api/tasks/<int:id>/category', methods=['PATCH'])
@jwt_required()
def update_task_category(id):
    current_user_id = int(get_jwt_identity())

    task = get_task(id)

    if task["user_id"] != current_user_id:
        return (jsonify({"error": "Not your task"}), 403)


    category = request.json.get('category')

    if category is not None and not category:
        return (jsonify({"error": "Category is required"}), 400)
    else:
        db = get_db()
        db.execute(
            'UPDATE task SET category = ?'
            ' WHERE id = ?',
            (category, id)
            )
        db.commit()

        result = {"message": "Task category updated successfully",
                  "task_id": id,
                  "task_title": task["title"],
                  "task_description": task["description"],
                  "task_category": category,
                  "task_status": task['status']
                 }

        return (jsonify(result), 200)
