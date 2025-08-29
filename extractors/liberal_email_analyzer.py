#!/usr/bin/env python3
"""
Liberal Email Analyzer - Cast wider net for personal emails
"""

import os
import json
import re
from pathlib import Path
from collections import defaultdict

class LiberalEmailAnalyzer:
    def __init__(self, raw_dir):
        self.raw_dir = Path(raw_dir)
        
    def analyze_email_liberal(self, email_path):
        """More liberal analysis - catch more potential personal emails"""
        
        try:
            with open(email_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extract key fields
            subject_match = re.search(r'^Subject: (.+)$', content, re.MULTILINE)
            from_match = re.search(r'^From: (.+)$', content, re.MULTILINE)
            date_match = re.search(r'^Date: (.+)$', content, re.MULTILINE)
            
            subject = subject_match.group(1) if subject_match else ""
            sender = from_match.group(1) if from_match else ""
            date_str = date_match.group(1) if date_match else ""
            
            # Get more body content
            body_start = content.find('\n\n')
            body = content[body_start:body_start+1000] if body_start > 0 else content[:1000]
            
            # Liberal classification
            email_type = self.classify_email_liberal(subject, sender, body)
            
            return {
                "file": email_path.name,
                "subject": subject[:150],
                "from": sender[:150], 
                "date": date_str[:50],
                "body_preview": body.strip()[:300],
                "classification": email_type,
                "year": self.extract_year(date_str)
            }
            
        except Exception as e:
            return {
                "file": email_path.name,
                "error": str(e),
                "classification": "error"
            }
    
    def classify_email_liberal(self, subject, sender, body):
        """Liberal classification - multiple categories"""
        
        text = (subject + " " + sender + " " + body).lower()
        
        # Definitely automated/spam
        if any(term in text for term in [
            "unsubscribe", "newsletter", "automated", "noreply", "no-reply",
            "mailchimp", "constant contact", "promotional", "marketing"
        ]):
            return "automated"
        
        # Definitely personal (human names, personal domains)
        if any(term in text for term in [
            "@gmail.com", "@yahoo.com", "@hotmail.com", "@aol.com",
            "thanks", "hello", "hi ", "hey", "dear", "sincerely",
            "maya", "paul", "caitlin", "mom", "dad", "jim", "cary"
        ]):
            return "personal"
        
        # Business/work related
        if any(term in text for term in [
            "meeting", "project", "invoice", "payment", "client", "work",
            "business", "proposal", "contract", "estimate"
        ]):
            return "business"
        
        # Services (could be important)
        if any(term in text for term in [
            "bank", "account", "statement", "bill", "payment", "ups", "fedex",
            "amazon", "paypal", "credit", "insurance", "medical", "health"
        ]):
            return "services"
        
        # Subscriptions/newsletters (might have personal value)
        if any(term in text for term in [
            "news", "update", "digest", "weekly", "monthly", "blog",
            "podcast", "video", "youtube", "tech"
        ]):
            return "subscriptions"
        
        return "unknown"
    
    def extract_year(self, date_str):
        """Extract year from date"""
        match = re.search(r'\b(20\d{2})\b', date_str)
        return match.group(1) if match else None
    
    def analyze_all_categories(self, limit=1000):
        """Analyze emails with liberal categorization"""
        
        print("📧 LIBERAL EMAIL ANALYSIS - Cast Wider Net")
        print("=" * 55)
        
        # Find inbox emails
        inbox_files = []
        for root, dirs, files in os.walk(self.raw_dir):
            if "Inbox" in root:
                for file in files:
                    if file.isdigit():
                        inbox_files.append(Path(root) / file)
        
        print(f"📥 Found {len(inbox_files)} inbox emails")
        print(f"🔍 Analyzing first {min(limit, len(inbox_files))} emails...")
        
        # Analyze emails
        categories = defaultdict(list)
        year_stats = defaultdict(lambda: defaultdict(int))
        
        for i, email_path in enumerate(inbox_files[:limit]):
            email_data = self.analyze_email_liberal(email_path)
            
            category = email_data.get("classification", "unknown")
            categories[category].append(email_data)
            
            # Year stats
            year = email_data.get("year")
            if year:
                year_stats[year][category] += 1
            
            if (i + 1) % 200 == 0:
                print(f"   Processed {i + 1} emails...")
        
        print(f"✅ Analysis complete!")
        
        # Show category breakdown
        print(f"\n📊 EMAIL CATEGORIES:")
        for category, emails in sorted(categories.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"   {category}: {len(emails)} emails")
        
        # Show samples from each category
        print(f"\n🎯 SAMPLE EMAILS BY CATEGORY:")
        
        for category in ["personal", "business", "services", "subscriptions"]:
            if category in categories and categories[category]:
                print(f"\n  {category.upper()} SAMPLES:")
                for email in categories[category][:3]:
                    print(f"    From: {email.get('from', 'Unknown')[:60]}")
                    print(f"    Subject: {email.get('subject', 'No subject')[:80]}")
                    if email.get('body_preview'):
                        print(f"    Preview: {email['body_preview'][:100]}...")
                    print()
        
        # Create analysis summary
        analysis = {
            "total_emails_analyzed": min(limit, len(inbox_files)),
            "total_inbox_emails": len(inbox_files),
            "category_breakdown": {k: len(v) for k, v in categories.items()},
            "year_statistics": dict(year_stats),
            "potentially_personal": len(categories["personal"]) + len(categories["business"]),
            "samples_by_category": {
                category: emails[:5] for category, emails in categories.items() if len(emails) > 0
            }
        }
        
        return analysis

def main():
    """Liberal email analysis for better narrative discovery"""
    
    raw_dir = "/home/jonclaude/Agents/Claude on Studio/VectorVault/projects/email_analysis/raw"
    
    analyzer = LiberalEmailAnalyzer(raw_dir)
    analysis = analyzer.analyze_all_categories()
    
    # Save results
    output_file = "/home/jonclaude/Agents/Claude on Studio/VectorVault/projects/email_analysis/liberal_email_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(analysis, f, indent=2)
    
    print(f"\n💾 Analysis saved to: {output_file}")
    
    # Summary
    print(f"\n📊 LIBERAL ANALYSIS SUMMARY:")
    print(f"   Total emails analyzed: {analysis['total_emails_analyzed']}")
    print(f"   Personal: {analysis['category_breakdown'].get('personal', 0)}")
    print(f"   Business: {analysis['category_breakdown'].get('business', 0)}")
    print(f"   Services: {analysis['category_breakdown'].get('services', 0)}")
    print(f"   Subscriptions: {analysis['category_breakdown'].get('subscriptions', 0)}")
    print(f"   Potentially narrative-worthy: {analysis['potentially_personal']}")
    
    return analysis

if __name__ == "__main__":
    main()