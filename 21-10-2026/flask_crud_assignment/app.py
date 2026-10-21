from flask import Flask,jsonify,request
app=Flask(__name__)
students = [
    {
        "id": 1,
        "name": "Rhea Kapoor",
        "course": "Python",
        "score": 82
    },
    {
        "id": 2,
        "name": "Zain Malik",
        "course": "SQL",
        "score": 76
    },
    {
        "id": 3,
        "name": "Devika Rao",
        "course": "Cloud",
        "score": 91
    }
]

@app.route("/students")
def get_students():
    return jsonify(students)

@app.route("/students/<int:id>",methods=["GET"])
def get_student(id):
    for item in students:
        if item["id"]==id:
            return jsonify(item)
    return jsonify({"message":"Student not found"}),404

@app.route("/students",methods=["POST"])
def post_student():
    data=request.get_json()
    students.append(data)
    return jsonify({"message":"Student added successfully"})

@app.route("/students/<int:id>",methods=["PUT"])
def update_student(id):
    data=request.get_json()
    for item in students:
        if item["id"]==id:
            item['name']=data['name']
            item['course']=data['course']
            item['score']=data['score']
            return jsonify({"message":"Student updated successfully"})
    return jsonify({"message":"Student not found"}),404

@app.route("/students/<int:id>",methods=["DELETE"])
def delete_student(id):
    for item in students:
        if item["id"]==id:
            students.remove(item)
            return jsonify({"message":"Student deleted successfully"})
    return jsonify({"message":"Student not found"}),404

if __name__ == "__main__":
    app.run(debug=True)