from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import json

app = Flask(__name__)
CORS(app)

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    DATABASE_URL = "postgresql://username:password@host:port/database"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Irys Gallery API is running on Vercel'
    })

@app.route('/api/users/connect', methods=['POST'])
def connect_wallet():
    try:
        data = request.get_json()
        wallet_address = data.get('wallet_address')
        
        if not wallet_address:
            return jsonify({'error': 'Wallet address is required'}), 400
        
        session = SessionLocal()
        
        # Check if user exists
        result = session.execute(
            text("SELECT * FROM users WHERE wallet_address = :wallet_address"),
            {"wallet_address": wallet_address}
        )
        user = result.fetchone()
        
        if user:
            user_dict = {
                'id': user[0],
                'wallet_address': user[1],
                'username': user[2],
                'avatar_url': user[3],
                'bio': user[4],
                'x_handle': user[5],
                'discord_handle': user[6],
                'created_at': user[7].isoformat() if user[7] else None
            }
            session.close()
            return jsonify({'user': user_dict})
        
        # Create new user
        result = session.execute(
            text("INSERT INTO users (wallet_address) VALUES (:wallet_address) RETURNING *"),
            {"wallet_address": wallet_address}
        )
        session.commit()
        new_user = result.fetchone()
        
        user_dict = {
            'id': new_user[0],
            'wallet_address': new_user[1],
            'username': new_user[2],
            'avatar_url': new_user[3],
            'bio': new_user[4],
            'x_handle': new_user[5],
            'discord_handle': new_user[6],
            'created_at': new_user[7].isoformat() if new_user[7] else None
        }
        
        session.close()
        return jsonify({'user': user_dict}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/artworks', methods=['GET'])
def get_artworks():
    try:
        session = SessionLocal()
        
        # Get query parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 12))
        search = request.args.get('search', '')
        
        offset = (page - 1) * limit
        
        # Build query
        query = """
        SELECT a.*, u.username, u.avatar_url 
        FROM artworks a 
        JOIN users u ON a.user_id = u.id
        """
        params = {}
        
        if search:
            query += " WHERE a.title ILIKE :search OR a.description ILIKE :search"
            params['search'] = f"%{search}%"
        
        query += " ORDER BY a.created_at DESC LIMIT :limit OFFSET :offset"
        params.update({'limit': limit, 'offset': offset})
        
        result = session.execute(text(query), params)
        artworks = result.fetchall()
        
        artworks_list = []
        for artwork in artworks:
            artworks_list.append({
                'id': artwork[0],
                'user_id': artwork[1],
                'title': artwork[2],
                'description': artwork[3],
                'file_type': artwork[4],
                'irys_id': artwork[5],
                'file_url': artwork[6],
                'thumbnail_url': artwork[7],
                'file_size': artwork[8],
                'mime_type': artwork[9],
                'created_at': artwork[10].isoformat() if artwork[10] else None,
                'updated_at': artwork[11].isoformat() if artwork[11] else None,
                'views': artwork[12],
                'likes': artwork[13],
                'artist_name': artwork[14],
                'artist_avatar': artwork[15]
            })
        
        session.close()
        return jsonify({'artworks': artworks_list})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Add more routes as needed...

if __name__ == '__main__':
    app.run(debug=True)