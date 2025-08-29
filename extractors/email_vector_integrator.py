#!/usr/bin/env python3
"""
VectorVault Email Integration
Add email narrative vectors to the main nexus database
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime

class EmailVectorIntegrator:
    def __init__(self, db_path=None):
        if not db_path:
            db_path = "/home/jonclaude/Agents/Claude on Studio/VectorVault/storage/vectors.db"
        self.db_path = db_path
        self.ensure_database()
        
    def ensure_database(self):
        """Create database and tables if they don't exist"""
        
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create vectors table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vectors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_type TEXT NOT NULL,
                    timestamp REAL,
                    content TEXT,
                    metadata TEXT,
                    vector TEXT,
                    importance_score REAL DEFAULT 0
                )
            ''')
            
            # Create email index
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_email_type 
                ON vectors(data_type) WHERE data_type = 'email'
            ''')
            
            conn.commit()
    
    def create_email_vector(self, email_data):
        """Create vector representation of email"""
        
        # Extract key features
        subject = email_data.get('subject', '')
        sender = email_data.get('from', '')
        body = email_data.get('body_preview', '')
        classification = email_data.get('classification', 'unknown')
        year = email_data.get('year')
        
        # Create feature vector (simplified)
        features = {
            'has_personal_domain': any(domain in sender.lower() for domain in ['gmail', 'yahoo', 'aol', 'hotmail']),
            'subject_length': len(subject),
            'body_length': len(body),
            'is_reply': subject.lower().startswith(('re:', 'fwd:', 'fw:')),
            'classification': classification,
            'year': int(year) if year else 2020,  # Default year
            'sender_domain': self.extract_domain(sender)
        }
        
        # Create dense vector (normalized features)
        vector = [
            1.0 if features['has_personal_domain'] else 0.0,
            min(features['subject_length'] / 100.0, 1.0),  # Normalize to 0-1
            min(features['body_length'] / 1000.0, 1.0),    # Normalize to 0-1
            1.0 if features['is_reply'] else 0.0,
            self.classification_to_number(classification),
            (features['year'] - 2000) / 25.0,  # Normalize years 2000-2025 to 0-1
        ]
        
        return vector, features
    
    def extract_domain(self, sender):
        """Extract domain from email sender"""
        if '<' in sender and '>' in sender:
            email = sender.split('<')[1].split('>')[0]
        else:
            email = sender
        
        if '@' in email:
            return email.split('@')[1].lower()
        return 'unknown'
    
    def classification_to_number(self, classification):
        """Convert classification to numeric value"""
        mapping = {
            'personal': 1.0,
            'business': 0.8,
            'services': 0.6,
            'subscriptions': 0.4,
            'automated': 0.2,
            'unknown': 0.0
        }
        return mapping.get(classification, 0.0)
    
    def calculate_email_importance(self, email_data, features):
        """Calculate importance score for email"""
        
        score = 0.0
        classification = email_data.get('classification', 'unknown')
        
        # Base score by classification
        base_scores = {
            'personal': 10.0,
            'business': 7.0,
            'services': 5.0,
            'subscriptions': 3.0,
            'automated': 1.0,
            'unknown': 2.0
        }
        
        score += base_scores.get(classification, 2.0)
        
        # Length bonuses
        if features['body_length'] > 300:
            score += 2.0
        if features['subject_length'] > 20:
            score += 1.0
        
        # Personal domain bonus
        if features['has_personal_domain']:
            score += 3.0
        
        # Reply bonus (ongoing conversation)
        if features['is_reply']:
            score += 2.0
        
        return score
    
    def integrate_emails(self, email_analysis_file):
        """Integrate emails into vector database"""
        
        print("🔗 EMAIL VECTOR INTEGRATION - VectorVault Nexus")
        print("=" * 60)
        
        # Load email analysis
        with open(email_analysis_file, 'r') as f:
            analysis = json.load(f)
        
        # Get all categories of emails
        samples = analysis.get('samples_by_category', {})
        
        print(f"📧 Loading email data...")
        all_emails = []
        
        for category, emails in samples.items():
            if category not in ['error', 'unknown']:  # Skip error emails
                print(f"   {category}: {len(emails)} emails")
                all_emails.extend(emails)
        
        print(f"📊 Total emails to vectorize: {len(all_emails)}")
        
        # Process emails into vectors
        vectors_added = 0
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for i, email_data in enumerate(all_emails):
                
                # Skip error emails
                if 'error' in email_data:
                    continue
                
                # Create vector representation
                vector, features = self.create_email_vector(email_data)
                importance = self.calculate_email_importance(email_data, features)
                
                # Prepare data
                timestamp = self.parse_email_date(email_data.get('date', ''))
                content_summary = f"From: {email_data.get('from', '')[:50]} | Subject: {email_data.get('subject', '')[:100]}"
                
                metadata = {
                    'sender': email_data.get('from', ''),
                    'subject': email_data.get('subject', ''),
                    'classification': email_data.get('classification', ''),
                    'year': email_data.get('year'),
                    'file': email_data.get('file', ''),
                    'features': features
                }
                
                # Insert into database
                cursor.execute('''
                    INSERT INTO vectors 
                    (data_type, timestamp, content, metadata, vector, importance_score)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    'email',
                    timestamp,
                    content_summary,
                    json.dumps(metadata),
                    json.dumps(vector),
                    importance
                ))
                
                vectors_added += 1
                
                if (i + 1) % 50 == 0:
                    print(f"   Processed {i + 1} emails...")
            
            conn.commit()
        
        print(f"✅ Integration complete!")
        print(f"📊 Added {vectors_added} email vectors to database")
        
        # Get total vector count
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM vectors")
            total_vectors = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM vectors WHERE data_type = 'email'")
            email_vectors = cursor.fetchone()[0]
        
        print(f"📈 Total vectors in database: {total_vectors}")
        print(f"📧 Email vectors: {email_vectors}")
        
        return {
            'vectors_added': vectors_added,
            'total_vectors': total_vectors,
            'email_vectors': email_vectors
        }
    
    def parse_email_date(self, date_str):
        """Parse email date to timestamp"""
        
        # Extract year for basic timestamp
        import re
        year_match = re.search(r'\b(20\d{2})\b', date_str)
        
        if year_match:
            year = int(year_match.group(1))
            # Create basic timestamp (Jan 1 of that year)
            return datetime(year, 1, 1).timestamp()
        
        # Default to 2021 if no year found
        return datetime(2021, 1, 1).timestamp()

def main():
    """Integrate email analysis into VectorVault nexus"""
    
    integrator = EmailVectorIntegrator()
    
    # Load liberal email analysis
    analysis_file = "/home/jonclaude/Agents/Claude on Studio/VectorVault/projects/email_analysis/liberal_email_analysis.json"
    
    if not Path(analysis_file).exists():
        print(f"❌ Analysis file not found: {analysis_file}")
        return
    
    # Integrate emails
    result = integrator.integrate_emails(analysis_file)
    
    # Save integration report
    report = {
        'integration_date': datetime.now().isoformat(),
        'source_analysis': analysis_file,
        'results': result,
        'database_location': integrator.db_path
    }
    
    report_file = "/home/jonclaude/Agents/Claude on Studio/VectorVault/projects/email_analysis/vector_integration_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Integration report saved to: {report_file}")
    print(f"\n✨ Email vectors now available in VectorVault nexus!")
    print(f"Ready for cross-modal correlation with journal and conversation data...")

if __name__ == "__main__":
    main()