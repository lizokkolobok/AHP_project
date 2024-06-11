from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost:5434/ahp_project'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model Definitions
class Criteria(db.Model):
    __tablename__ = 'criteria'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    weight = db.Column(db.Numeric, nullable=True)

class Alternatives(db.Model):
    __tablename__ = 'alternatives'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    weight = db.Column(db.Numeric, nullable=True)

class CriteriaComparison(db.Model):
    __tablename__ = 'criteria_comparisons'
    id = db.Column(db.Integer, primary_key=True)
    criteria1_id = db.Column(db.Integer, nullable=False)
    criteria2_id = db.Column(db.Integer, nullable=False)
    value = db.Column(db.Numeric, nullable=False)

class AlternativeComparison(db.Model):
    __tablename__ = 'alternative_comparisons'
    id = db.Column(db.Integer, primary_key=True)
    alternative1_id = db.Column(db.Integer, nullable=False)
    alternative2_id = db.Column(db.Integer, nullable=False)
    criteria_id = db.Column(db.Integer, nullable=False)
    value = db.Column(db.Numeric, nullable=False)

# Initialize the database
def initialize_db():
    try:
        # Check if the database exists
        if not database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
            print("Database does not exist. Creating database...")
            create_database(app.config['SQLALCHEMY_DATABASE_URI'])
            print("Database created.")
        else:
            print("Database already exists.")
        return True
    except Exception as e:
        print(f"Error during database initialization: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_criteria', methods=['POST'])
def add_criteria():
    data = request.get_json()
    names = data.get('names', [])
    for name in names:
        if not name or len(name.strip()) == 0:
            return jsonify({"status": "error", "message": "Name field cannot be null or empty"})
        criteria = Criteria(name=name)
        db.session.add(criteria)
    db.session.commit()
    return jsonify({"status": "success"})

@app.route('/add_alternatives', methods=['POST'])
def add_alternatives():
    data = request.get_json()
    names = data.get('names', [])
    for name in names:
        if not name or len(name.strip()) == 0:
            return jsonify({"status": "error", "message": "Name field cannot be null or empty"})
        alternative = Alternatives(name=name)
        db.session.add(alternative)
    db.session.commit()
    return jsonify({"status": "success"})
def get_criteria_id(criteria_value):
    criteria_id = 0
    try:
        # Try to cast to integer
        criteria_id = int(criteria_value)
        #print("criteria id is int")
    except ValueError:
        # If not an integer, look up by name
        result = db.session.execute(text("SELECT id FROM criteria WHERE name = :name"), {'name': criteria_value}).fetchone()
        #print(f"criteria ValueError id {result}")
        if result is None:
            raise ValueError(f"Criteria '{criteria_value}' not found")
        criteria_id = result.id
    return criteria_id
@app.route('/add_criteria_comparison', methods=['POST'])
def add_criteria_comparison():
    try:
        data = request.get_json()
        comparisons = data.get('comparisons')

        # Check if comparisons is empty, null, or undefined
        if not comparisons:
            return jsonify({"status": "error", "message": "No criteria comparison data provided"})

        for comparison in comparisons:
            criteria1_id = comparison.get('criteria1_id')
            criteria2_id = comparison.get('criteria2_id')
            value = comparison.get('value')
            #print(f"add_criteria_comparison : criteria1_id: {criteria1_id}")
            # Check if all required fields are provided
            #if criteria1_id is None or criteria2_id is None or value is None:
            #    return jsonify({"status": "error", "message": "criteria comparison Missing required fields"})


            
            try:
                #print("adding criteria1id ")
                criteria1_id = get_criteria_id(criteria1_id)
                criteria2_id = get_criteria_id(criteria2_id)
                comparison['criteria1_id'] = criteria1_id
                comparison['criteria2_id'] = criteria2_id

                #print(f"adding criteria1_id_response {criteria1_id}")
            except ValueError as e:
                return jsonify({"status": "error", "message": str(e)})
            #print(f"after criteria1_id {criteria1_id}")
            required_fields = ['criteria1_id', 'criteria2_id', 'value']
            for field in required_fields:
                if comparison.get(field) is None:
                    return jsonify({"status": "error", "message": f"criteria comparison Missing required field: {field}"})
        
            # Check if criteria IDs are valid
            #if not Criteria.query.get(criteria1_id) or not Criteria.query.get(criteria2_id):
            #    return jsonify({"status": "error", "message": "criteria comparison Invalid criteria IDs"})
            for field in required_fields[:-1]:
                if not Criteria.query.get(comparison.get(field)):
                    return jsonify({"status": "error", "message": f"criteria comparison Invalid criteria ID: {field}"})
             # Function to handle criteria ID as string or integer
           
            #print(f" add criteria_comparison: {criteria1_id} ")
            criteria_comparison = CriteriaComparison(
                criteria1_id=criteria1_id,
                criteria2_id=criteria2_id,
                value=value
            )
            db.session.add(criteria_comparison)
       
        #print("add_criteria_comparison commiting to db")
        # Commit changes to the database
        db.session.commit()
        return jsonify({"status": "success","message": str("ok")})
    except Exception as e:
        # Rollback changes if an error occurs
        db.session.rollback()
        print(f"add_criteria_comparison exception {e}")
        return jsonify({"status": "error", "message criteria comparison Exception ": str(e)})


@app.route('/add_alternative_comparison', methods=['POST'])
def add_alternative_comparison():
    try:
        data = request.get_json()
        comparisons = data.get('comparisons', [])
        if not comparisons:
            return jsonify({"status": "error", "message": "No alterinative comparison data provided"})
        
        for comparison in comparisons:
            alternative1_id = comparison.get('alternative1_id')
            alternative2_id = comparison.get('alternative2_id')
            criteria_id = comparison.get('criteria_id')
            value = comparison.get('value')

            # Check if all required fields are provided
            #if alternative1_id is None or alternative2_id is None or criteria_id is None or value is None:
            #    return jsonify({"status": "error", "message": "alterinative comparison Missing required fields"})

            try:
                criteria_id = get_criteria_id(criteria_id)
                comparison['criteria_id'] = criteria_id
            except ValueError as e:
                return jsonify({"status": "error", "message": str(e)})


            # Function to handle alternative ID as string or integer
            def get_alternative_id(alternative_value):
                try:
                    # Try to cast to integer
                    alternative_id = int(alternative_value)
                except ValueError:
                    # If not an integer, look up by name
                    result = db.session.execute(text("SELECT id FROM alternatives WHERE name = :name"), {'name': alternative_value}).fetchone()
                    if result is None:
                        raise ValueError(f"alternative '{alternative_value}' not found")
                    alternative_id = result.id
                return alternative_id

            try:
                alternative1_id = get_alternative_id(alternative1_id)
                alternative2_id = get_alternative_id(alternative2_id)
                comparison['alternative1_id'] = alternative1_id
                comparison['alternative2_id'] = alternative2_id
            except ValueError as e:
                return jsonify({"status": "error", "message": str(e)})
                


            required_fields = ['alternative1_id', 'alternative2_id', 'criteria_id','value']
            for field in required_fields:
                if comparison.get(field) is None:
                    print(f"alterinative comparison Missing required field: {field}")
                    return jsonify({"status": "error", "message": f"alterinative comparison Missing required field: {field}"})
            # Check if alternative and criteria IDs are valid
            #if not Alternatives.query.get(alternative1_id) or not Alternatives.query.get(alternative2_id) \
            #        or not Criteria.query.get(criteria_id):
            #    return jsonify({"status": "error", "message": "alterinative comparison Invalid IDs"})
            for field in required_fields[:-2]:
                if not Alternatives.query.get(comparison.get(field)):
                   return jsonify({"status": "error", "message": f"alterinative comparison Invalid alterinative ID: {field}"})
            if not Criteria.query.get(criteria_id):
                return jsonify({"status": "error", "message": f"alterinative comparison Invalid criteria_id: {criteria_id}"})


            

            alternative_comparison = AlternativeComparison(
                alternative1_id=alternative1_id,
                alternative2_id=alternative2_id,
                criteria_id=criteria_id,
                value=value
            )
            db.session.add(alternative_comparison)
        
        # Commit changes to the database
        db.session.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        # Rollback changes if an error occurs
        db.session.rollback()
        return jsonify({"status": "error", "message: alterinative comparison Exception ": str(e)})

@app.route('/get_criteria', methods=['GET'])
def get_criteria():
    criteria = Criteria.query.all()
    return jsonify([{"id": c.id, "name": c.name, "weight": c.weight} for c in criteria])

@app.route('/get_alternatives', methods=['GET'])
def get_alternatives():
    alternatives = Alternatives.query.all()
    return jsonify([{"id": a.id, "name": a.name, "weight": a.weight} for a in alternatives])
@app.route('/get_criteria_comparison', methods=['GET'])
def get_criteria_comparison():
    comparisons = CriteriaComparison.query.all()
    return jsonify([
        {
            "id": c.id,
            "criteria1_id": c.criteria1_id,
            "criteria2_id": c.criteria2_id,
            "value": c.value
        } for c in comparisons
    ])

@app.route('/get_alternative_comparison', methods=['GET'])
def get_alternative_comparison():
    comparisons = AlternativeComparison.query.all()
    return jsonify([
        {
            "id": a.id,
            "alternative1_id": a.alternative1_id,
            "alternative2_id": a.alternative2_id,
            "criteria_id": a.criteria_id,
            "value": a.value
        } for a in comparisons
    ])
@app.route('/insert_criteria_reciprocal_comparisons', methods=['POST'])
def insert_criteria_reciprocal_comparisons():
    try:
        db.session.execute(text("SELECT insert_criteria_reciprocal_comparisons()"))
        db.session.commit()
        return jsonify({"status": "success", "message": "Criteria reciprocal comparisons inserted successfully"})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Database error occurred.", "details": str(e)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/ensure_criteria_self_comparisons', methods=['POST'])
def ensure_criteria_self_comparisons():
    try:
        db.session.execute(text("SELECT ensure_criteria_self_comparisons()"))
        db.session.commit()
        return jsonify({"status": "success", "message": "Criteria self comparisons ensured successfully"})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Database error occurred.", "details": str(e)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/insert_alternative_reciprocal_comparisons', methods=['POST'])
def insert_alternative_reciprocal_comparisons():
    try:
        criteria_name = request.get_json().get('criteria_name')
        if not criteria_name:
            return jsonify({"status": "error", "message": "Criteria name is required"})

        # Check if the criteria name is not an empty string
        if not criteria_name.strip():
            return jsonify({"status": "error", "message": "Criteria name cannot be empty"})

        # Check if the criteria name exists in the database
        #criteria = Criteria.query.filter_by(name=criteria_name).first()
        #if not criteria:
        #    return jsonify({"status": "error", "message": "Criteria with the given name does not exist"})

        # Your logic for inserting alternative reciprocal comparisons
        db.session.execute(text("SELECT insert_alternative_reciprocal_comparisons(:criteria_name)"), {"criteria_name": criteria_name})
        db.session.commit()
        return jsonify({"status": "success", "message": "Alternatives  reciprocal comparisons generation done successfully"})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Database error occurred: {str(e)}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/ensure_alternatives_self_comparisons', methods=['POST'])
def ensure_alternatives_self_comparisons():
    try:
        criteria_name = request.get_json().get('criteria_name')
        if not criteria_name:
            return jsonify({"status": "error", "message": "Criteria name is required"})

        # Check if the criteria name is not an empty string
        if not criteria_name.strip():
            return jsonify({"status": "error", "message": "Criteria name cannot be empty"})

        # Check if the criteria name exists in the database
        #criteria = Criteria.query.filter_by(name=criteria_name).first()
        #if not criteria:
        #    return jsonify({"status": "error", "message": "Criteria with the given name does not exist"})

        # Your logic for ensuring alternatives self comparisons
        db.session.execute(text("SELECT ensure_alternatives_self_comparisons(:criteria_name)"), {"criteria_name": criteria_name})
        db.session.commit()


        return jsonify({"status": "success", "message": "Alternatives self comparisons ensured successfully"})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Database error occurred.", "details": str(e)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/delete_alternatives', methods=['POST'])
def delete_alternatives():
    try:
        db.session.execute(text("ALTER TABLE alternatives DISABLE TRIGGER ALL"))
        db.session.execute(text("DELETE FROM alternatives"))
        db.session.execute(text("ALTER TABLE alternatives ENABLE TRIGGER ALL"))
        db.session.execute(text("ALTER SEQUENCE alternatives_id_seq RESTART WITH 1;"))
        db.session.commit()
        return jsonify({"status": "success", "message": "Alternatives deleted successfully"})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Database error occurred.", "details": str(e)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/delete_alternative_comparisons', methods=['POST'])
def delete_alternative_comparisons():
    try:
        db.session.execute(text("ALTER TABLE alternative_comparisons DISABLE TRIGGER ALL"))
        db.session.execute(text("DELETE FROM alternative_comparisons"))
        db.session.execute(text("ALTER TABLE alternative_comparisons ENABLE TRIGGER ALL"))
        db.session.execute(text("ALTER SEQUENCE alternative_comparisons_id_seq RESTART WITH 1;"))

        db.session.commit()
        return jsonify({"status": "success", "message": "Alternative comparisons deleted successfully"})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Database error occurred.", "details": str(e)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/delete_criteria_comparisons', methods=['POST'])
def delete_criteria_comparisons():
    try:
        db.session.execute(text("ALTER TABLE criteria_comparisons DISABLE TRIGGER ALL"))
        db.session.execute(text("DELETE FROM criteria_comparisons"))
        db.session.execute(text("ALTER TABLE criteria_comparisons ENABLE TRIGGER ALL"))
        db.session.execute(text("ALTER SEQUENCE criteria_comparisons_id_seq RESTART WITH 1;"))

        db.session.commit()
        return jsonify({"status": "success", "message": "Criteria comparisons deleted successfully"})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Database error occurred.", "details": str(e)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/delete_criteria', methods=['POST'])
def delete_criteria():
    try:
        db.session.execute(text("ALTER TABLE criteria DISABLE TRIGGER ALL"))
        db.session.execute(text("DELETE FROM criteria"))
        db.session.execute(text("ALTER TABLE criteria ENABLE TRIGGER ALL"))
        db.session.execute(text("ALTER SEQUENCE criteria_id_seq RESTART WITH 1;"))

        db.session.commit()
        return jsonify({"status": "success", "message": "Criteria deleted successfully"})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Database error occurred.", "details": str(e)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


def execute_dynamic_sql(insert_table, select_table, select_columns, conditions, additional_values):
    try:
        condition_statements = []
        for condition in conditions:
            column = condition.get('column')
            value = condition.get('value')
            condition_statements.append(f"{column} = '{value}'")
        
        conditions_str = ' AND '.join(condition_statements)
        
        sql = f"""
            INSERT INTO {insert_table} ({', '.join(select_columns)}, value)
            SELECT {', '.join(select_columns)}, {additional_values}
            FROM {select_table}
            WHERE {conditions_str};
        """
        
        #db.session.execute(text(sql))
        #db.session.commit()
        #return jsonify({"status": "success", "message": "Query executed successfully"})
        return jsonify({"status": "success", "message": sql})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/execute_query', methods=['POST'])
def execute_query():
    try:
        data = request.get_json()
        sql_query = data.get('sqlQuery')

        if not sql_query:
            return jsonify({"status": "error", "message": "SQL query is required"})

        # Execute the SQL query
        db.session.execute(text(sql_query))
        db.session.commit()

        return jsonify({"status": "success", "message": "Query executed successfully"})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Database error occurred.", "details": str(e)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        # Execute PostgreSQL functions using SQLAlchemy
        db.session.execute(text("SELECT calculate_criteria_weights()"))
        db.session.execute(text("SELECT calculate_alternative_weights()"))
        db.session.commit()
        
        # Fetch criteria and alternatives data
        criteria = Criteria.query.all()
        alternatives = Alternatives.query.all()
        
        # Convert data to JSON format
        criteria_data = [{"id": c.id, "name": c.name, "weight": c.weight} for c in criteria]
        alternatives_data = [{"id": a.id, "name": a.name, "weight": a.weight} for a in alternatives]
        
        # Return the results
        return jsonify({"status": "success", "criteria": criteria_data, "alternatives": alternatives_data})
    except SQLAlchemyError as e:
        print(" sqlAclhemy error")
        db.session.rollback()
        return jsonify({"status": "error", "message": "calculate Database error occurred.", "details": str(e)})
    except Exception as e:
        # Return error message if any exception occurs
        return jsonify({"status": "error", "calculate exception message": str(e)})

if __name__ == '__main__':
    with app.app_context():
        if not initialize_db():
            print("Failed to initialize the database.")
        db.create_all()
    app.run(debug=True)
