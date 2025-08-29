#!/usr/bin/env python3
"""
VectorVault Simple Vector Database
Store and query multimodal vectors using basic Python
"""

import json
import math
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import tempfile

class SimpleVectorDB:
    def __init__(self, db_path: str):
        """
        Initialize simple vector database using SQLite
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self.conn = sqlite3.connect(db_path)
        self.create_tables()
    
    def create_tables(self):
        """Create database tables for storing vectors"""
        
        cursor = self.conn.cursor()
        
        # Main vectors table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vectors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_type TEXT NOT NULL,      -- 'audio', 'visual', 'semantic'
                source_file TEXT NOT NULL,      -- Original file path
                timestamp REAL NOT NULL,        -- Time in seconds
                vector_data TEXT NOT NULL,      -- JSON-encoded vector
                metadata TEXT,                  -- JSON-encoded metadata
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Index for fast timestamp queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON vectors(timestamp)
        ''')
        
        # Index for source type queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_source_type 
            ON vectors(source_type)
        ''')
        
        self.conn.commit()
        
    def store_audio_vectors(self, vectors: List[Dict], source_file: str):
        """Store audio feature vectors"""
        
        cursor = self.conn.cursor()
        
        for vector in vectors:
            cursor.execute('''
                INSERT INTO vectors (source_type, source_file, timestamp, vector_data, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                'audio',
                source_file,
                vector['timestamp'],
                json.dumps(vector['dense_vector']),
                json.dumps(vector['features'])
            ))
        
        self.conn.commit()
        print(f"Stored {len(vectors)} audio vectors")
    
    def store_visual_vectors(self, vectors: List[Dict], source_file: str):
        """Store visual feature vectors"""
        
        cursor = self.conn.cursor()
        
        for vector in vectors:
            cursor.execute('''
                INSERT INTO vectors (source_type, source_file, timestamp, vector_data, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                'visual', 
                source_file,
                vector['timestamp'],
                json.dumps(vector['dense_vector']),
                json.dumps(vector['features'])
            ))
        
        self.conn.commit()
        print(f"Stored {len(vectors)} visual vectors")
    
    def store_semantic_vectors(self, vectors: List[Dict], source_file: str):
        """Store semantic/text vectors"""
        
        cursor = self.conn.cursor()
        
        for vector in vectors:
            cursor.execute('''
                INSERT INTO vectors (source_type, source_file, timestamp, vector_data, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                'semantic',
                source_file,
                vector['timestamp'], 
                json.dumps(vector['dense_vector']),
                json.dumps(vector['features'])
            ))
        
        self.conn.commit()
        print(f"Stored {len(vectors)} semantic vectors")
    
    def query_by_timerange(self, start_time: float, end_time: float, 
                          source_type: Optional[str] = None) -> List[Dict]:
        """Query vectors within a time range"""
        
        cursor = self.conn.cursor()
        
        if source_type:
            cursor.execute('''
                SELECT id, source_type, source_file, timestamp, vector_data, metadata
                FROM vectors
                WHERE timestamp >= ? AND timestamp <= ? AND source_type = ?
                ORDER BY timestamp
            ''', (start_time, end_time, source_type))
        else:
            cursor.execute('''
                SELECT id, source_type, source_file, timestamp, vector_data, metadata
                FROM vectors  
                WHERE timestamp >= ? AND timestamp <= ?
                ORDER BY timestamp
            ''', (start_time, end_time))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'source_type': row[1],
                'source_file': row[2],
                'timestamp': row[3],
                'vector': json.loads(row[4]),
                'metadata': json.loads(row[5]) if row[5] else {}
            })
        
        return results
    
    def get_conversation_summary(self) -> Dict:
        """Get summary statistics of stored vectors"""
        
        cursor = self.conn.cursor()
        
        # Count by source type
        cursor.execute('''
            SELECT source_type, COUNT(*), MIN(timestamp), MAX(timestamp)
            FROM vectors
            GROUP BY source_type
        ''')
        
        summary = {
            'total_vectors': 0,
            'duration': 0,
            'sources': {}
        }
        
        for row in cursor.fetchall():
            source_type, count, min_time, max_time = row
            summary['sources'][source_type] = {
                'count': count,
                'min_timestamp': min_time,
                'max_timestamp': max_time,
                'duration': max_time - min_time if max_time and min_time else 0
            }
            summary['total_vectors'] += count
            summary['duration'] = max(summary['duration'], max_time if max_time else 0)
        
        return summary
    
    def find_similar_moments(self, target_timestamp: float, 
                            window_size: float = 30.0,
                            source_type: Optional[str] = None) -> List[Dict]:
        """Find moments similar to a target timestamp"""
        
        # Get vectors around target time
        target_vectors = self.query_by_timerange(
            target_timestamp - 5, 
            target_timestamp + 5,
            source_type
        )
        
        if not target_vectors:
            return []
        
        # Use first target vector for comparison
        target_vector = target_vectors[0]['vector']
        
        # Get all vectors for comparison
        all_vectors = self.query_by_timerange(0, float('inf'), source_type)
        
        similarities = []
        
        for vector_data in all_vectors:
            # Skip vectors too close to target
            if abs(vector_data['timestamp'] - target_timestamp) < window_size:
                continue
                
            # Calculate simple cosine similarity
            similarity = self.cosine_similarity(target_vector, vector_data['vector'])
            
            similarities.append({
                'timestamp': vector_data['timestamp'],
                'similarity': similarity,
                'metadata': vector_data['metadata']
            })
        
        # Sort by similarity
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        return similarities[:10]  # Top 10 similar moments
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        
        if len(vec1) != len(vec2):
            return 0.0
            
        # Calculate dot product
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        
        # Calculate magnitudes
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        
        # Avoid division by zero
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
            
        return dot_product / (magnitude1 * magnitude2)
    
    def close(self):
        """Close database connection"""
        self.conn.close()

def main():
    """Test the vector database with our extracted features"""
    
    # Initialize database
    db_path = "/home/jonclaude/Agents/Claude on Studio/VectorVault/projects/google_meet_analysis/conversation.db"
    db = SimpleVectorDB(db_path)
    
    print("🗄️ VectorVault Database Initialized")
    
    # Load and store audio vectors
    audio_file = "/home/jonclaude/Agents/Claude on Studio/VectorVault/projects/google_meet_analysis/audio_vectors.json"
    if Path(audio_file).exists():
        with open(audio_file, 'r') as f:
            audio_data = json.load(f)
            
        db.store_audio_vectors(audio_data['vectors'], 'conversation_audio.wav')
    
    # Load and store visual vectors (if available)
    visual_file = "/home/jonclaude/Agents/Claude on Studio/VectorVault/projects/google_meet_analysis/visual_vectors.json"
    if Path(visual_file).exists():
        with open(visual_file, 'r') as f:
            visual_data = json.load(f)
            
        db.store_visual_vectors(visual_data['vectors'], 'google_meet.mp4')
    
    # Show summary
    summary = db.get_conversation_summary()
    print(f"\n📊 Conversation Database Summary:")
    print(f"Total vectors: {summary['total_vectors']}")
    print(f"Duration: {summary['duration']:.1f} seconds")
    
    for source_type, info in summary['sources'].items():
        print(f"\n{source_type.upper()} vectors:")
        print(f"  Count: {info['count']}")
        print(f"  Duration: {info['duration']:.1f}s")
        print(f"  Time range: {info['min_timestamp']:.1f}s - {info['max_timestamp']:.1f}s")
    
    # Test similarity search
    if summary['total_vectors'] > 0:
        test_time = summary['duration'] / 2  # Middle of conversation
        print(f"\n🔍 Finding moments similar to {test_time:.1f}s...")
        
        similar = db.find_similar_moments(test_time, source_type='audio')
        if similar:
            print("Top similar moments:")
            for i, moment in enumerate(similar[:5]):
                print(f"  {i+1}. {moment['timestamp']:.1f}s (similarity: {moment['similarity']:.3f})")
    
    db.close()
    print("\n✅ VectorVault database ready for analysis")

if __name__ == "__main__":
    main()