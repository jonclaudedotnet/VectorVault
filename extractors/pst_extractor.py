#!/usr/bin/env python3
"""
VectorVault PST Email Extractor
Extract important narrative content from years of email archives
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime, timedelta
import subprocess
from collections import defaultdict

class PSTExtractor:
    def __init__(self, pst_path=None):
        self.pst_path = pst_path
        self.emails = []
        self.importance_scores = {}
        self.narrative_threads = []
        
    def find_pst_files(self, search_dir="/home/jonclaude"):
        """Find all PST files in directory"""
        
        print("🔍 SEARCHING FOR PST FILES...")
        pst_files = []
        
        search_path = Path(search_dir)
        for pst_file in search_path.rglob("*.pst"):
            size_mb = pst_file.stat().st_size / (1024 * 1024)
            pst_files.append({
                "path": str(pst_file),
                "size_mb": round(size_mb, 2),
                "name": pst_file.name
            })
            
        return sorted(pst_files, key=lambda x: x["size_mb"], reverse=True)
    
    def extract_with_readpst(self, pst_file, output_dir):
        """Extract PST using readpst tool (if available)"""
        
        print(f"📧 Extracting {pst_file} with readpst...")
        
        try:
            # Check if readpst is available
            subprocess.run(["which", "readpst"], check=True, capture_output=True)
            
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Extract PST to mbox format
            cmd = [
                "readpst", 
                "-M",  # Output in mbox format
                "-o", output_dir,
                pst_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Extraction successful to {output_dir}")
                return True
            else:
                print(f"❌ Extraction failed: {result.stderr}")
                return False
                
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ readpst not available, trying alternative method...")
            return False
    
    def analyze_email_importance(self, email_data):
        """Score email importance for narrative archaeology"""
        
        score = 0
        content = email_data.get("content", "").lower()
        subject = email_data.get("subject", "").lower()
        sender = email_data.get("from", "").lower()
        
        # Personal indicators (high value)
        personal_indicators = [
            "family", "friend", "love", "relationship", "personal", 
            "maya", "paul", "caitlin", "mom", "dad", "brother", "sister",
            "wedding", "birthday", "anniversary", "holiday", "vacation"
        ]
        
        for indicator in personal_indicators:
            if indicator in content or indicator in subject:
                score += 10
        
        # Creative/work project indicators
        creative_indicators = [
            "project", "creative", "video", "film", "vr", "production", 
            "sea robin", "client", "idea", "concept", "story", "script"
        ]
        
        for indicator in creative_indicators:
            if indicator in content or indicator in subject:
                score += 8
        
        # Life event indicators
        life_events = [
            "new job", "moving", "house", "travel", "surgery", "health",
            "achievement", "success", "failure", "learn", "decision"
        ]
        
        for event in life_events:
            if event in content or event in subject:
                score += 12
        
        # Reduce score for spam/commercial
        spam_indicators = [
            "unsubscribe", "newsletter", "promotion", "sale", "deal",
            "click here", "limited time", "act now", "free", "viagra"
        ]
        
        for spam in spam_indicators:
            if spam in content or spam in subject:
                score -= 5
        
        # Thread analysis bonus
        if email_data.get("thread_length", 1) > 3:
            score += 5
        
        # Length analysis (detailed emails are more valuable)
        content_length = len(content)
        if content_length > 500:
            score += 3
        if content_length > 1000:
            score += 5
        
        return max(0, score)
    
    def extract_email_threads(self, emails):
        """Group emails into conversation threads"""
        
        threads = defaultdict(list)
        
        for email in emails:
            subject = email.get("subject", "")
            # Remove RE: and FW: prefixes for threading
            clean_subject = re.sub(r'^(RE:|FW:|FWD:)\s*', '', subject, flags=re.IGNORECASE).strip()
            
            # Group by subject and participants
            participants = set()
            participants.add(email.get("from", ""))
            participants.update(email.get("to", []))
            
            thread_key = (clean_subject, frozenset(participants))
            threads[thread_key].append(email)
        
        # Convert to list and add thread info
        thread_list = []
        for (subject, participants), thread_emails in threads.items():
            if len(thread_emails) > 1:  # Only keep actual threads
                thread_list.append({
                    "subject": subject,
                    "participants": list(participants),
                    "emails": sorted(thread_emails, key=lambda x: x.get("date", "")),
                    "thread_length": len(thread_emails)
                })
        
        return sorted(thread_list, key=lambda x: x["thread_length"], reverse=True)
    
    def create_narrative_summary(self, important_emails):
        """Create narrative summary of important email patterns"""
        
        # Timeline analysis
        email_dates = [email.get("date", "") for email in important_emails if email.get("date")]
        date_range = f"{min(email_dates)} to {max(email_dates)}" if email_dates else "Unknown"
        
        # Sender analysis
        senders = defaultdict(int)
        for email in important_emails:
            sender = email.get("from", "Unknown")
            senders[sender] += 1
        
        top_senders = dict(sorted(senders.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # Theme extraction
        themes = defaultdict(int)
        for email in important_emails:
            content = email.get("content", "").lower()
            subject = email.get("subject", "").lower()
            full_text = content + " " + subject
            
            # Count theme occurrences
            theme_words = {
                "work": ["work", "job", "client", "business", "project", "meeting"],
                "family": ["family", "mom", "dad", "sister", "brother", "parent"],
                "friends": ["friend", "maya", "paul", "buddy", "pal"],
                "creative": ["video", "film", "creative", "vr", "production", "story"],
                "technology": ["computer", "tech", "software", "digital", "ai"],
                "health": ["health", "doctor", "surgery", "medical", "vision"],
                "travel": ["travel", "trip", "vacation", "visit", "journey"],
                "life_events": ["wedding", "birthday", "anniversary", "graduation", "move"]
            }
            
            for theme, words in theme_words.items():
                if any(word in full_text for word in words):
                    themes[theme] += 1
        
        return {
            "total_important_emails": len(important_emails),
            "date_range": date_range,
            "top_senders": top_senders,
            "themes": dict(themes),
            "narrative_patterns": self.extract_narrative_patterns(important_emails)
        }
    
    def extract_narrative_patterns(self, emails):
        """Extract story-worthy patterns from email history"""
        
        patterns = []
        
        # Life transition periods (job changes, moves, etc.)
        transitions = self.find_life_transitions(emails)
        patterns.extend(transitions)
        
        # Relationship evolution
        relationships = self.analyze_relationship_evolution(emails)
        patterns.extend(relationships)
        
        # Creative project arcs
        projects = self.find_creative_projects(emails)
        patterns.extend(projects)
        
        return patterns
    
    def find_life_transitions(self, emails):
        """Find major life transitions in email history"""
        
        transitions = []
        transition_keywords = [
            ("job_change", ["new job", "career", "resignation", "hired", "interview"]),
            ("moving", ["moving", "new address", "apartment", "house", "relocat"]),
            ("education", ["school", "degree", "graduate", "study", "learn"]),
            ("health", ["surgery", "hospital", "doctor", "treatment", "recover"])
        ]
        
        for trans_type, keywords in transition_keywords:
            relevant_emails = []
            for email in emails:
                content = email.get("content", "").lower()
                if any(keyword in content for keyword in keywords):
                    relevant_emails.append(email)
            
            if len(relevant_emails) > 2:
                transitions.append({
                    "type": trans_type,
                    "email_count": len(relevant_emails),
                    "date_range": self.get_date_range(relevant_emails),
                    "sample_subjects": [e.get("subject", "")[:50] for e in relevant_emails[:3]]
                })
        
        return transitions
    
    def analyze_relationship_evolution(self, emails):
        """Track relationship patterns over time"""
        
        # Group emails by sender
        sender_timelines = defaultdict(list)
        for email in emails:
            sender = email.get("from", "")
            if sender and "@" in sender:  # Valid email
                sender_timelines[sender].append(email)
        
        relationships = []
        for sender, sender_emails in sender_timelines.items():
            if len(sender_emails) > 10:  # Significant correspondence
                relationships.append({
                    "person": sender,
                    "email_count": len(sender_emails),
                    "date_range": self.get_date_range(sender_emails),
                    "relationship_intensity": self.calculate_relationship_intensity(sender_emails)
                })
        
        return sorted(relationships, key=lambda x: x["email_count"], reverse=True)[:5]
    
    def find_creative_projects(self, emails):
        """Identify creative project threads"""
        
        project_keywords = [
            "video", "film", "production", "vr", "creative", "story", 
            "script", "edit", "shoot", "camera", "project"
        ]
        
        project_emails = []
        for email in emails:
            content = email.get("content", "").lower()
            subject = email.get("subject", "").lower()
            
            if any(keyword in content or keyword in subject for keyword in project_keywords):
                project_emails.append(email)
        
        if len(project_emails) > 5:
            return [{
                "type": "creative_projects",
                "email_count": len(project_emails),
                "date_range": self.get_date_range(project_emails),
                "sample_subjects": [e.get("subject", "")[:50] for e in project_emails[:5]]
            }]
        
        return []
    
    def get_date_range(self, emails):
        """Get date range for email list"""
        dates = [email.get("date", "") for email in emails if email.get("date")]
        if dates:
            return f"{min(dates)} to {max(dates)}"
        return "Unknown"
    
    def calculate_relationship_intensity(self, emails):
        """Calculate relationship intensity score"""
        # Simple metric based on frequency and recency
        total_emails = len(emails)
        
        # Check for recent activity
        recent_emails = 0
        try:
            one_year_ago = datetime.now() - timedelta(days=365)
            for email in emails:
                # This would need proper date parsing
                recent_emails += 1  # Simplified for now
        except:
            pass
        
        return min(total_emails * 2 + recent_emails, 100)
    
    def process_pst_file(self, pst_file_path, output_dir=None):
        """Main processing function for PST files"""
        
        if not output_dir:
            output_dir = "/tmp/pst_extraction"
        
        print("📧 PST EMAIL EXTRACTION - VectorVault Integration")
        print("=" * 60)
        print(f"Processing: {pst_file_path}")
        
        # Try extraction methods
        if not self.extract_with_readpst(pst_file_path, output_dir):
            print("❌ Automatic extraction failed")
            print("\n🔧 MANUAL EXTRACTION NEEDED:")
            print("1. Install readpst: sudo apt-get install readpst")
            print("2. Or convert PST to mbox format manually")
            print("3. Then run this script again")
            return None
        
        # Process extracted emails (placeholder - would read mbox files)
        sample_analysis = self.create_sample_analysis()
        
        return sample_analysis
    
    def create_sample_analysis(self):
        """Create sample analysis structure"""
        
        return {
            "extraction_method": "Manual processing required",
            "recommended_approach": {
                "step_1": "Convert PST to searchable format (mbox/EML)",
                "step_2": "Parse emails with Python email library", 
                "step_3": "Score importance using narrative archaeology criteria",
                "step_4": "Extract high-value threads and life events",
                "step_5": "Integrate with VectorVault for cross-modal correlation"
            },
            "importance_criteria": {
                "personal_correspondence": "Family, friends, life events",
                "creative_projects": "Video, VR, production discussions", 
                "life_transitions": "Job changes, moves, major decisions",
                "relationship_evolution": "Long-term correspondence patterns",
                "narrative_threads": "Story-worthy email exchanges"
            },
            "filtering_strategy": {
                "keep": "Personal, creative, life events, important decisions",
                "discard": "Spam, newsletters, automated messages, receipts",
                "maybe": "Work emails (context dependent), notifications"
            }
        }

def main():
    """Find and analyze PST files for narrative extraction"""
    
    extractor = PSTExtractor()
    
    # Find PST files
    pst_files = extractor.find_pst_files()
    
    if not pst_files:
        print("❌ No PST files found in home directory")
        print("💡 Place PST files in accessible location and try again")
        return
    
    print(f"📧 FOUND {len(pst_files)} PST FILE(S):")
    for pst in pst_files:
        print(f"  {pst['name']}: {pst['size_mb']} MB")
    
    # Process largest PST file
    if pst_files:
        largest_pst = pst_files[0]
        print(f"\n🎯 Processing largest file: {largest_pst['name']}")
        
        analysis = extractor.process_pst_file(largest_pst['path'])
        
        # Save analysis
        output_file = "/home/jonclaude/Agents/Claude on Studio/VectorVault/projects/email_analysis/pst_analysis.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"\n💾 Analysis saved to: {output_file}")
        print("\n✨ Ready for email narrative archaeology!")

if __name__ == "__main__":
    main()