#!/usr/bin/env python3
"""
VectorVault Inbox Analyzer - Focus on actual personal emails
"""

import os
import json
import email
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class InboxAnalyzer:
    def __init__(self, raw_dir):
        self.raw_dir = Path(raw_dir)
        self.emails = []
        
    def find_inbox_emails(self):
        """Find inbox emails specifically"""
        inbox_files = []
        
        for root, dirs, files in os.walk(self.raw_dir):
            if "Inbox" in root:
                for file in files:
                    if file.isdigit():
                        inbox_files.append(Path(root) / file)
        
        return sorted(inbox_files)
    
    def quick_analyze_email(self, email_path):
        """Quick analysis of email content"""
        
        try:
            with open(email_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Quick extraction without full parsing
            subject_match = re.search(r'^Subject: (.+)$', content, re.MULTILINE)
            from_match = re.search(r'^From: (.+)$', content, re.MULTILINE)
            date_match = re.search(r'^Date: (.+)$', content, re.MULTILINE)
            
            subject = subject_match.group(1) if subject_match else ""
            sender = from_match.group(1) if from_match else ""
            date_str = date_match.group(1) if date_match else ""
            
            # Extract body (simple approach)
            body_start = content.find('\n\n')
            body = content[body_start:body_start+500] if body_start > 0 else content[:500]
            
            return {
                "file": email_path.name,
                "subject": subject[:100],
                "from": sender[:100], 
                "date": date_str[:50],
                "body_preview": body.strip()[:200],
                "is_personal": self.is_personal_email(subject, sender, body)
            }
            
        except Exception as e:
            return {
                "file": email_path.name,
                "error": str(e),
                "is_personal": False
            }
    
    def is_personal_email(self, subject, sender, body):
        """Quick check if email seems personal"""
        
        text = (subject + " " + sender + " " + body).lower()
        
        # Personal indicators
        personal_signs = [
            "@gmail.com", "@yahoo.com", "@hotmail.com",  # Personal email providers
            "friend", "family", "personal", "thanks", "hello", "hi ",
            "maya", "paul", "caitlin", "mom", "dad"  # Your known contacts
        ]
        
        # Automated/commercial indicators
        spam_signs = [
            "unsubscribe", "newsletter", "promotion", "no-reply",
            "automated", "marketing", "advertisement", "offers"
        ]
        
        personal_score = sum(1 for sign in personal_signs if sign in text)
        spam_score = sum(1 for sign in spam_signs if sign in text)
        
        return personal_score > spam_score and personal_score > 0
    
    def analyze_inbox(self, limit=500):
        """Analyze inbox emails for narrative content"""
        
        print("📧 INBOX NARRATIVE ANALYSIS")
        print("=" * 50)
        
        # Find inbox emails
        inbox_files = self.find_inbox_emails()
        print(f"📥 Found {len(inbox_files)} inbox emails")
        
        # Analyze subset
        analysis_files = inbox_files[:limit]
        print(f"🔍 Analyzing first {len(analysis_files)} emails...")
        
        personal_emails = []
        all_emails = []
        
        for i, email_path in enumerate(analysis_files):
            email_data = self.quick_analyze_email(email_path)
            all_emails.append(email_data)
            
            if email_data.get("is_personal", False):
                personal_emails.append(email_data)
            
            if (i + 1) % 100 == 0:
                print(f"   Processed {i + 1} emails...")
        
        print(f"✅ Analysis complete!")
        print(f"📊 Personal emails found: {len(personal_emails)}")
        
        # Show samples
        if personal_emails:
            print(f"\n🎯 SAMPLE PERSONAL EMAILS:")
            for email in personal_emails[:5]:
                print(f"\n  From: {email.get('from', 'Unknown')}")
                print(f"  Subject: {email.get('subject', 'No subject')}")
                print(f"  Preview: {email.get('body_preview', '')[:100]}...")
        
        # Analyze patterns
        sender_analysis = defaultdict(int)
        year_analysis = defaultdict(int)
        
        for email in personal_emails:
            # Count senders
            sender = email.get('from', '').split('<')[0].strip().split('@')[0]
            if sender:
                sender_analysis[sender] += 1
            
            # Count years
            date_str = email.get('date', '')
            year_match = re.search(r'\b(20\d{2})\b', date_str)
            if year_match:
                year_analysis[year_match.group(1)] += 1
        
        analysis = {
            "total_inbox_emails": len(inbox_files),
            "emails_analyzed": len(all_emails),
            "personal_emails_found": len(personal_emails),
            "personal_percentage": round(len(personal_emails) / len(all_emails) * 100, 1) if all_emails else 0,
            "top_senders": dict(sorted(sender_analysis.items(), key=lambda x: x[1], reverse=True)[:10]),
            "years_active": dict(sorted(year_analysis.items())),
            "sample_personal_emails": personal_emails[:10],
            "narrative_assessment": "High potential" if len(personal_emails) > 50 else "Moderate potential"
        }
        
        return analysis

def main():
    """Quick inbox analysis for narrative archaeology"""
    
    raw_dir = "/home/jonclaude/Agents/Claude on Studio/VectorVault/projects/email_analysis/raw"
    
    analyzer = InboxAnalyzer(raw_dir)
    analysis = analyzer.analyze_inbox()
    
    # Save results
    output_file = "/home/jonclaude/Agents/Claude on Studio/VectorVault/projects/email_analysis/inbox_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(analysis, f, indent=2)
    
    print(f"\n💾 Analysis saved to: {output_file}")
    
    # Summary
    print(f"\n📊 INBOX SUMMARY:")
    print(f"   Total inbox emails: {analysis['total_inbox_emails']}")
    print(f"   Personal emails: {analysis['personal_emails_found']} ({analysis['personal_percentage']}%)")
    print(f"   Top senders: {list(analysis['top_senders'].keys())[:5]}")
    print(f"   Years active: {list(analysis['years_active'].keys())}")
    print(f"   Narrative potential: {analysis['narrative_assessment']}")
    
    return analysis

if __name__ == "__main__":
    main()