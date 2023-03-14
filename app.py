import os
import psycopg2.pool
from flask import Flask, g, jsonify, request
from configparser import ConfigParser

app = Flask(__name__)

def get_db():
    if 'db' not in g:
        db_url = os.environ.get('DATABASE_URL')
        pool = psycopg2.pool.SimpleConnectionPool(1, 10, dsn=db_url)
        g.db = pool.getconn()
    
    return g.db

def dict_factory(cursor, row):
    d = {}

    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]

    return d

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    
    if db is not None:
        db.close() 
        
@app.route('/', methods=['GET'])
def query_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT Version()')
    version = cur.fetchone()

    cur.close()
    
    return jsonify(version)   

@app.route('/api/v1/resources/referrals/all', methods=['GET'])
def get_all_referrals():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM referrals')
    results = cur.fetchall()
    cur.close()
    print(results)
    
    columns = [col[0] for col in cur.description]
    print(cur.description)
    
    data = [dict(zip(columns, row)) for row in results]
    
    return jsonify(data)
# test

@app.route('/api/v1/resources/referrals', methods=['POST'])
def post_referral():
    
    data = request.get_json()
    print(data)
    
    conn = get_db()
    cur = conn.cursor()
    
    insert_statement = """
                    INSERT INTO referrals (firm_code, file_type, name, email, phone, street_address_1, street_address_2, city, province, postal_code)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                    
    insert_data = (
        data['firm_code'],
        data['file_type'],
        data['name'],
        data['email'],
        data['phone'],
        data['street_address_1'],
        data['street_address_2'],
        data['city'],
        data['province'],
        data['postal_code']
        )
    
    cur.execute(insert_statement, insert_data)
    referral_id = cur.lastrowid
    
    conn.commit()
    cur.close()
    conn.close()
    
    print("record inserted")
    
    return jsonify({'message': 'Referral added successfully', 'referral_id': referral_id})

if __name__ == '__main__':
    app.run(debug=True)