from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__, static_folder='static')
CORS(app)

DATABASE = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category_id INTEGER,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            image TEXT,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')
    
    # Seed initial sample data in INR if database is empty
    cursor.execute('SELECT COUNT(*) FROM products')
    if cursor.fetchone()[0] == 0:
        categories = ['Electronics', 'Footwear', 'Accessories']
        for cat in categories:
            cursor.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (cat,))
        
        products = [
            ('Wireless Headphones', 1, 2499.00, 15, 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400'),
            ('Smart Watch', 1, 4999.00, 8, 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400'),
            ('Running Shoes', 2, 1899.00, 20, 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400'),
            ('Leather Backpack', 3, 1299.00, 5, 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400'),
            ('Mechanical Keyboard', 1, 3499.00, 12, 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=400'),
            ('Classic Sunglasses', 3, 799.00, 30, 'https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=400')
        ]
        
        cursor.executemany('''
            INSERT INTO products (title, category_id, price, stock, image)
            VALUES (?, ?, ?, ?, ?)
        ''', products)
        
    conn.commit()
    conn.close()

# Routes
@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/categories', methods=['GET'])
def get_categories():
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM categories').fetchall()
    conn.close()
    return jsonify([dict(c) for c in categories])

@app.route('/api/products', methods=['GET'])
def get_products():
    search = request.args.get('search', '')
    category_id = request.args.get('category', '')
    max_price = request.args.get('max_price', '')

    query = '''
        SELECT p.id, p.title, p.price, p.stock, p.image, c.name as category 
        FROM products p
        JOIN categories c ON p.category_id = c.id
        WHERE 1=1
    '''
    params = []

    if search:
        query += " AND p.title LIKE ?"
        params.append(f"%{search}%")
    if category_id:
        query += " AND p.category_id = ?"
        params.append(category_id)
    if max_price:
        query += " AND p.price <= ?"
        params.append(float(max_price))

    conn = get_db_connection()
    products = conn.execute(query, params).fetchall()
    conn.close()
    
    return jsonify([dict(p) for p in products])

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)