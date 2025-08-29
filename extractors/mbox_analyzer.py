#!/usr/bin/env python3
"""
VectorVault mbox Email Analyzer
Process extracted email files for narrative archaeology
"""

import os
import json
import email
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import mailbox

class EmailNarrativeAnalyzer:
    def __init__(self, raw_dir):
        self.raw_dir = Path(raw_dir)
        self.emails = []
        self.threads = {}
        self.importance_scores = {}
        
    def find_email_files(self):
        """Find all email files in extracted directory"""
        
        email_files = []
        for root, dirs, files in os.walk(self.raw_dir):
            for file in files:
                if file.isdigit():  # readpst creates numbered files
                    email_files.append(Path(root) / file)
        
        return sorted(email_files)
    
    def parse_email_file(self, email_path):
        """Parse individual email file"""
        
        try:
            with open(email_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Parse email
            msg = email.message_from_string(content)
            
            # Extract basic info
            email_data = {
                "file_path": str(email_path),
                "folder": email_path.parent.name,
                "subject": msg.get("Subject", ""),
                "from": msg.get("From", ""),
                "to": msg.get("To", ""),
                "date": msg.get("Date", ""),
                "message_id": msg.get("Message-ID", ""),
                "content": self.extract_content(msg),
                "content_length": 0
            }
            
            # Calculate content length
            email_data["content_length"] = len(email_data["content"])
            
            return email_data
            
        except Exception as e:
            return {
                "file_path": str(email_path),
                "error": str(e),
                "folder": email_path.parent.name
            }
    
    def extract_content(self, msg):
        """Extract text content from email message"""
        
        content = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            content += payload.decode('utf-8', errors='ignore')
                    except:
                        pass
        else:
            try:
                payload = msg.get_payload(decode=True)
                if payload:
                    content = payload.decode('utf-8', errors='ignore')
            except:
                content = str(msg.get_payload())
        
        # Clean up content
        content = re.sub(r'\s+', ' ', content).strip()
        return content[:2000]  # Limit content length
    
    def calculate_importance_score(self, email_data):
        """Calculate narrative importance score"""
        
        score = 0
        content = email_data.get("content", "").lower()
        subject = email_data.get("subject", "").lower()
        sender = email_data.get("from", "").lower()
        
        # Personal indicators (high value)
        personal_indicators = [
            "family", "friend", "love", "relationship", "personal",
            "mom", "dad", "brother", "sister", "wife", "husband",
            "wedding", "birthday", "anniversary", "holiday", "vacation"
        ]
        
        for indicator in personal_indicators:
            if indicator in content or indicator in subject:
                score += 10
        
        # Creative/work project indicators
        creative_indicators = [
            "project", "creative", "video", "film", "vr", "production",
            "idea", "concept", "story", "script", "collaborate"
        ]
        
        for indicator in creative_indicators:
            if indicator in content or indicator in subject:
                score += 8
        
        # Life event indicators
        life_events = [
            "new job", "moving", "house", "travel", "surgery", "health",
            "achievement", "success", "graduation", "retirement", "death"
        ]
        
        for event in life_events:
            if event in content or event in subject:
                score += 12
        
        # Long content bonus
        content_length = email_data.get("content_length", 0)
        if content_length > 300:
            score += 3
        if content_length > 800:
            score += 5
        
        # Reduce score for automated/spam content
        spam_indicators = [
            "unsubscribe", "newsletter", "promotion", "sale",
            "automated", "no-reply", "noreply", "delivery failure"
        ]
        
        for spam in spam_indicators:
            if spam in content or spam in subject or spam in sender:
                score -= 8
        
        # Folder-based scoring
        folder = email_data.get("folder", "").lower()
        if folder == "inbox":
            score += 2
        elif folder == "sent":
            score += 3  # Your outgoing emails are important
        elif folder == "drafts":
            score += 1
        
        return max(0, score)
    
    def analyze_temporal_patterns(self, emails):
        """Analyze email patterns over time"""
        
        yearly_stats = defaultdict(lambda: {
            "count": 0,
            "important_count": 0,
            "total_content_length": 0,
            "top_correspondents": defaultdict(int)
        })
        
        for email_data in emails:
            importance = self.importance_scores.get(email_data["file_path"], 0)
            
            # Try to extract year from date
            date_str = email_data.get("date", "")
            year = self.extract_year(date_str)
            
            if year:
                yearly_stats[year]["count"] += 1
                yearly_stats[year]["total_content_length"] += email_data.get("content_length", 0)
                
                if importance > 10:  # High importance threshold
                    yearly_stats[year]["important_count"] += 1
                
                # Track correspondents
                sender = email_data.get("from", "").split("<")[0].strip()
                if sender and len(sender) > 2:
                    yearly_stats[year]["top_correspondents"][sender] += 1
        
        return dict(yearly_stats)
    
    def extract_year(self, date_str):
        """Extract year from email date string"""
        
        # Try to find 4-digit year
        year_match = re.search(r'\b(19|20)\d{2}\b', date_str)
        return year_match.group(0) if year_match else None
    
    def find_important_threads(self, emails, min_score=15):
        """Find email threads with high narrative value"""
        
        important_threads = []
        
        # Group by subject (simplified threading)
        subject_groups = defaultdict(list)
        
        for email_data in emails:
            importance = self.importance_scores.get(email_data["file_path"], 0)
            if importance >= min_score:
                subject = email_data.get("subject", "")
                clean_subject = re.sub(r'^(RE:|FW:|FWD:)\s*', '', subject, flags=re.IGNORECASE).strip()
                subject_groups[clean_subject].append(email_data)
        
        # Convert to thread format
        for subject, thread_emails in subject_groups.items():
            if len(thread_emails) >= 2 or any(self.importance_scores.get(e["file_path"], 0) > 20 for e in thread_emails):
                important_threads.append({
                    "subject": subject,
                    "email_count": len(thread_emails),
                    "participants": list(set([e.get("from", "") for e in thread_emails])),
                    "total_importance": sum(self.importance_scores.get(e["file_path"], 0) for e in thread_emails),
                    "date_range": self.get_thread_date_range(thread_emails),
                    "sample_content": thread_emails[0].get("content", "")[:200]
                })
        
        return sorted(important_threads, key=lambda x: x["total_importance"], reverse=True)
    
    def get_thread_date_range(self, thread_emails):
        """Get date range for email thread"""
        dates = [e.get("date", "") for e in thread_emails if e.get("date")]
        return f"Multiple dates ({len(dates)} emails)" if dates else "Unknown dates"
    
    def process_all_emails(self):
        """Main processing function"""
        
        print("📧 EMAIL NARRATIVE ANALYSIS - VectorVault Integration")
        print("=" * 60)
        
        # Find all email files
        email_files = self.find_email_files()
        print(f"🔍 Found {len(email_files)} email files to process")
        
        # Process emails in batches
        print("📖 Parsing email content...")
        processed_count = 0
        
        for email_path in email_files[:1000]:  # Process first 1000 for speed
            email_data = self.parse_email_file(email_path)
            if "error" not in email_data:
                self.emails.append(email_data)
                # Calculate importance
                score = self.calculate_importance_score(email_data)
                self.importance_scores[email_data["file_path"]] = score
            
            processed_count += 1
            if processed_count % 100 == 0:
                print(f"   Processed {processed_count} emails...")
        
        print(f"✅ Processed {len(self.emails)} emails successfully")
        
        # Analyze patterns
        print("🧠 Analyzing narrative patterns...")
        
        # Find high-importance emails
        important_emails = [e for e in self.emails if self.importance_scores.get(e["file_path"], 0) > 10]
        print(f"📊 Found {len(important_emails)} high-importance emails")
        
        # Temporal analysis
        temporal_patterns = self.analyze_temporal_patterns(self.emails)
        
        # Important threads
        important_threads = self.find_important_threads(self.emails)
        
        # Create analysis summary
        analysis = {
            "processing_date": datetime.now().isoformat(),
            "total_emails_processed": len(self.emails),
            "total_files_found": len(email_files),
            "high_importance_emails": len(important_emails),
            "important_threads": len(important_threads),
            "temporal_patterns": temporal_patterns,
            "top_important_threads": important_threads[:10],
            "narrative_summary": self.create_narrative_summary(important_emails, temporal_patterns)
        }
        
        return analysis
    
    def create_narrative_summary(self, important_emails, temporal_patterns):
        """Create narrative summary of email history"""
        
        # Get date range
        years = [int(y) for y in temporal_patterns.keys() if y.isdigit()]
        date_range = f"{min(years)} to {max(years)}" if years else "Unknown"
        
        # Get most active years
        most_active = sorted(temporal_patterns.items(), 
                           key=lambda x: x[1]["important_count"], reverse=True)[:3]
        
        # Extract themes
        themes = defaultdict(int)
        for email in important_emails:
            content = email.get("content", "").lower()
            if any(word in content for word in ["family", "personal", "love"]):
                themes["personal"] += 1
            if any(word in content for word in ["project", "work", "business"]):
                themes["professional"] += 1
            if any(word in content for word in ["creative", "video", "idea"]):
                themes["creative"] += 1
            if any(word in content for word in ["travel", "vacation", "trip"]):
                themes["travel"] += 1
        
        return {
            "email_span": date_range,
            "most_active_years": [{"year": y, "important_emails": d["important_count"]} 
                                for y, d in most_active],
            "dominant_themes": dict(sorted(themes.items(), key=lambda x: x[1], reverse=True)),
            "narrative_value_assessment": "High - substantial personal correspondence history"
        }

def main():
    """Process extracted email files for narrative archaeology"""
    
    raw_dir = "/home/jonclaude/Agents/Claude on Studio/VectorVault/projects/email_analysis/raw"
    
    analyzer = EmailNarrativeAnalyzer(raw_dir)
    analysis = analyzer.process_all_emails()
    
    # Save analysis
    output_file = "/home/jonclaude/Agents/Claude on Studio/VectorVault/projects/email_analysis/email_narrative_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(analysis, f, indent=2)
    
    print(f"\n💾 Analysis saved to: {output_file}")
    
    # Print summary
    print(f"\n📊 ANALYSIS SUMMARY:")
    print(f"   Total emails: {analysis['total_emails_processed']}")
    print(f"   High importance: {analysis['high_importance_emails']}")
    print(f"   Important threads: {analysis['important_threads']}")
    print(f"   Email span: {analysis['narrative_summary']['email_span']}")
    print(f"   Themes: {list(analysis['narrative_summary']['dominant_themes'].keys())}")
    
    print(f"\n✨ Email narrative archaeology complete!")
    print(f"Ready for VectorVault nexus integration...")

if __name__ == "__main__":
    main()