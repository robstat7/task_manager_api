from flask import (
    Blueprint, request, jsonify
)
from werkzeug.exceptions import abort

from task_manager.db import get_db

bp = Blueprint('task', __name__)


@bp.route('/api/tasks', methods=['GET', 'POST'])
def manage_tasks():
    if request.method == 'GET':
        db = get_db()
        tasks = db.execute(
            'SELECT id, title'
            ' FROM task'
            ' ORDER BY id DESC'
        ).fetchall()

        tasks_list = [{'task_id': task['id'], 'task_title': task['title']}
                      for task in tasks]

        return (jsonify(tasks_list), 200)

    else:
        title = request.json.get('title')

        if not title:
            return (jsonify({"error": "Title is required"}), 400)
        else:
            db = get_db()
            new_task_cursor = db.execute(
                'INSERT INTO task (title)'
                ' VALUES (?)',
                (title,)
            )
            db.commit()

            result = {"message": "Task added successfully",
                      "task_id": new_task_cursor.lastrowid,
                      "task_title": title
                     }

            return (jsonify(result), 201)


def get_task(id):
    task = get_db().execute(
        'SELECT id, title'
        ' FROM task'
        ' WHERE id = ?',
        (id,)
    ).fetchone()

    if task is None:
        abort(404, f"Task id {id} doesn't exist.")

    return task 


@bp.route('/api/tasks/<int:id>', methods=['PUT', 'DELETE'])
def update(id):
    task = get_task(id)

    if request.method == 'PUT':
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

            result = {"message": "Task updated successfully",
                      "task_id": id,
                      "task_title": title
                     }

            return (jsonify(result), 200)

    else:
        db = get_db()
        db.execute('DELETE FROM task WHERE id = ?', (id,))
        db.commit()


        result = {"message": "Task deleted successfully",
                  "task_id": id,
                  "task_title": task["title"]
                  }

        return (jsonify(result), 200)
