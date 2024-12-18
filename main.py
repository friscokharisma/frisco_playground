from flask import Flask, request, jsonify, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
import re

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///items.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/testing')
def testing():
    return render_template('testing.html')

@app.route('/playground')
def playground():
    try:
        items = Item.query.all()

        items_list = [{"id": item.id, "name": item.name, "description": item.description} for item in items]

        # return jsonify({"items": items_list}), 200
        return render_template('playground_index.html', items=items_list)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/script_list')
def script_list():
    return render_template('script_index.html')

# -------------------- endpoint --------------------

@app.route('/items', methods=['GET'])
def get_items():
    try:
        items = Item.query.all()

        items_list = [{"id": item.id, "name": item.name, "description": item.description} for item in items]

        return jsonify({"items": items_list}), 200
        # return render_template('playground_index.html', items=items_list)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/item/<int:item_id>', methods=['GET'])
def get_item(item_id):
    try:
        item = Item.query.get(item_id)

        if not item:
            return jsonify({"error": "Item not found"}), 404
        
        item_details = {
            "id": item.id,
            "name": item.name,
            "description": item.description
        }

        return jsonify({"item": item_details}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/create_item', methods=['POST'])
def create_item():
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')

        if not name:
            return jsonify({"error": "Create item : Name is required"}), 422
        
        if not re.match(r"^[a-zA-Z0-9\s]+$", name):
            return jsonify({"error": "Create item : Name must contain only letters, numbers and spaces"}), 422
        
        existing_item = Item.query.filter_by(name=name).first()
        if existing_item:
            return jsonify({"error": f"Create item : An item with the name '{name}' already exist"}), 422
        
        if len(name) < 3:
            return jsonify({"error": "Create item : Name must be at least 3 characters long"}), 422
        
        if len(name) > 100:
            return jsonify({"error": "Create item : Name must not exceed 100 characters long"}), 422
        
        if not description:
            return jsonify({"error": "Create item : Description is required"}), 422
        
        if not re.match(r"^[a-zA-Z0-9\s]+$", description):
            return jsonify({"error": "Create item : Description must contain only letters, numbers and spaces"}), 422
        
        if len(description) < 3:
            return jsonify({"error": "Create item : Description must be at least 3 characters long"}), 422
        
        if len(description) > 100:
            return jsonify({"error": "Create item : Description must not exceed 100 characters long"}), 422
        
        new_item = Item(name=name, description=description)
        db.session.add(new_item)
        db.session.commit()

        return jsonify({"message": "Item created", "item": {"id": new_item.id, "name": new_item.name, "description": new_item.description}}), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/update_item/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    try:
        data = request.json
        name = data.get('name')
        description = data.get('description')

        item = Item.query.get(item_id)

        if not item:
            return jsonify({"error": f"Item with ID {item} not found"}), 404
        
        if not name:
            return jsonify({"error": "Name is required"}), 422
        
        if not re.match(r"^[a-zA-Z0-9\s]+$", name):
            return jsonify({"error": "Name must contain only letters, numbers and spaces"}), 422
        
        existing_item = Item.query.filter_by(name=name).first()
        if existing_item:
            return jsonify({"error": f"An item with the name '{name}' already exist"}), 422
        
        if len(name) < 3:
            return jsonify({"error": "Name must be at least 3 characters long"}), 422
        
        if len(name) > 100:
            return jsonify({"error": "Name must not exceed 100 characters long"}), 422
        
        if name:
            item.name = name
        if description:
            item.description = description

        db.session.commit()

        update_item = {
            "id": item.id,
            "name": item.name,
            "description": item.description,
        }

        return jsonify({"message": "Item updated", "item": update_item}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/delete_item/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    # Logic to delete the item from the database
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return '', 200  # Return no content for DELETE success

# @app.route('/delete_item/<int:item_id>', methods=['DELETE'])
# def delete_item(item_id):
#     try:
#         item = Item.query.get(item_id)

#         if not item:
#             return jsonify({"error": f"Item with ID {item_id} not found"}), 404

#         db.session.delete(item)
#         db.session.commit()

#         return jsonify({"message" : f"Item with ID {item_id} deleted sucessfully"}), 200
    
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)