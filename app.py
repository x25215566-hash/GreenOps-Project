"""Eco-friendly Serverless Note and Task Manager Flask application"""

import os
from flask import Flask, jsonify, request
import boto3
from botocore.exceptions import ClientError

APP = Flask(__name__)
app = APP

AWS_REGION = os.getenv("AWS_REGION", "eu-west-1")
TABLE_NAME = os.getenv("DYNAMODB_TABLE", "GreenOpsTasks")

def get_table():
    """Return a dynaomoDB Table resource using environment configuration"""
    dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
    return dynamodb.Table(TABLE_NAME)

@app.route("/", methods=["GET"])
def health_check():
    """Return service health status"""
    return jsonify({"Status": "ok", "service": "green-ops-tasks"}), 200

@app.route("/tasks", methods=["GET"])
def list_tasks():
    """Retrieve all tasks from DynamoDB"""
    try:
        table = get_table()
        response = table.scan()
        return jsonify({"tasks": response.get("Items", [])}), 200
    except ClientError as exc:
        return jsonify({"error": exc.response["Error"]["Message"]}), 500

@app.route("/tasks", methods=["POST"])
def create_task():
    """Create a new task item in DynamoDB"""
    payload= request.get_json(silent=True) or {}
    task_id= payload.get("id")
    title= payload.get("title")
    if not task_id or not title:
        return jsonify({"error": "Both 'id' and 'title' are required"}), 400

    item ={
        "id": str(task_id),
        "title": str(title),
        "completed": bool(payload.get("completed", False)),
    }
    try:
        get_table().put_item(Item=item)
        return jsonify({"task": item}), 201
    except ClientError as exc:
        return jsonify({"error": exc.response["Error"]["Message"]}), 500

@app.route("/tasks/<task_id>", methods=["PUT"])
def update_task(task_id):
    """Update an existing task in DynamoDB"""
    payload = request.get_json(silent=True) or {}
    completed = bool(payload.get("completed", True))
    try:
        response = get_table().update_item(
            Key={"id": str(task_id)},
            UpdateExpression="SET completed = :completed",
            ExpressionAttributeValues={":completed": completed},
            ReturnValues="ALL_NEW",
        )
        return jsonify({"task": response.get("Attributes", {})}), 200
    except ClientError as exc:
        return jsonify({"error": exc.response["Error"]["Message"]}), 500

@app.route("/tasks/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    """Delete a task from DynamoDB"""
    try:
        get_table().delete_item(Key={"id": str(task_id)})
        return jsonify({"deleted": str(task_id)}), 200

    except ClientError as exc:
        return jsonify({"error": exc.response["Error"]["Message"]}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
