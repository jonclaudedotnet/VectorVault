#!/usr/bin/env python3
"""
VectorVault Journal Extractor
Extract and analyze Apple Journal entries for personal narrative archaeology
"""

import os
import json
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime
import re

class JournalExtractor:
    def __init__(self, journal_path):
        self.journal_path = Path(journal_path)
        self.entries = []
        
    def extract_all_entries(self):
        """Extract all journal entries from Apple Journal export"""
        
        entries_dir = self.journal_path / "Entries"
        resources_dir = self.journal_path / "Resources"
        
        print(f"🗓️ Processing Apple Journal entries from: {self.journal_path}")
        
        # Process HTML entries
        html_files = list(entries_dir.glob("*.html"))
        print(f"Found {len(html_files)} journal entries")
        
        for html_file in html_files:
            entry = self.extract_entry_from_html(html_file)
            if entry:
                self.entries.append(entry)
        
        # Sort by date
        self.entries.sort(key=lambda x: x['date'])
        
        print(f"📚 Extracted {len(self.entries)} journal entries")
        return self.entries
    
    def extract_entry_from_html(self, html_file):
        """Extract content from HTML journal entry"""
        
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract title from filename
            title = html_file.stem.replace('_', ' ')
            
            # Extract date
            date_match = re.match(r'(\d{4}-\d{2}-\d{2})', html_file.name)
            date_str = date_match.group(1) if date_match else "unknown"
            
            # Extract text content
            text_content = soup.get_text(strip=True, separator=' ')
            
            # Clean up the text
            text_content = re.sub(r'\s+', ' ', text_content)
            
            # Remove HTML artifacts
            text_content = text_content.replace('•', '').strip()
            
            entry = {
                'title': title,
                'date': date_str,
                'filename': html_file.name,
                'content': text_content,
                'word_count': len(text_content.split()),
                'themes': self.extract_themes(text_content)
            }
            
            return entry
            
        except Exception as e:
            print(f"Error processing {html_file}: {e}")
            return None
    
    def extract_themes(self, content):
        """Extract themes and topics from journal content"""
        
        content_lower = content.lower()
        
        themes = {
            'technology': any(word in content_lower for word in ['ai', 'computer', 'coding', 'tech', 'digital', 'app', 'software']),
            'relationships': any(word in content_lower for word in ['friend', 'family', 'love', 'relationship', 'maya', 'paul']),
            'work': any(word in content_lower for word in ['work', 'job', 'career', 'project', 'business', 'client']),
            'health': any(word in content_lower for word in ['health', 'doctor', 'medicine', 'prescription', 'surgery', 'vision']),
            'food': any(word in content_lower for word in ['food', 'eating', 'restaurant', 'cook', 'meal', 'burger', 'chinese']),
            'travel': any(word in content_lower for word in ['travel', 'trip', 'visit', 'lake george', 'vacation']),
            'creativity': any(word in content_lower for word in ['video', 'production', 'creative', 'film', 'vr', 'immersive']),
            'learning': any(word in content_lower for word in ['learn', 'study', 'teach', 'education', 'english', 'language']),
            'reflection': any(word in content_lower for word in ['think', 'feel', 'realize', 'understand', 'remember', 'want'])
        }
        
        return {theme: present for theme, present in themes.items() if present}
    
    def create_semantic_vectors(self):
        """Create semantic vectors from journal entries"""
        
        vectors = []
        
        for i, entry in enumerate(self.entries):
            # Create features for each entry
            features = {
                'word_count': entry['word_count'],
                'theme_diversity': len(entry['themes']),
                'personal_reflection_score': self.calculate_reflection_score(entry['content']),
                'emotional_intensity': self.calculate_emotional_intensity(entry['content']),
                'temporal_gap': self.calculate_temporal_gap(i)
            }
            
            # Create dense vector
            dense_vector = [
                min(features['word_count'] / 1000.0, 1.0),  # Normalized word count
                features['theme_diversity'] / 10.0,         # Theme diversity
                features['personal_reflection_score'],       # Reflection score
                features['emotional_intensity'],             # Emotional intensity
                features['temporal_gap']                     # Time gap normalized
            ]
            
            vector = {
                'entry_index': i,
                'date': entry['date'],
                'title': entry['title'],
                'content_preview': entry['content'][:200] + "...",
                'themes': entry['themes'],
                'features': features,
                'dense_vector': dense_vector
            }
            
            vectors.append(vector)
        
        return vectors
    
    def calculate_reflection_score(self, content):
        """Calculate how reflective/personal the entry is"""
        reflection_words = ['i think', 'i feel', 'i realize', 'i want', 'i need', 'i hope', 'i remember', 'i understand']
        content_lower = content.lower()
        
        score = sum(content_lower.count(word) for word in reflection_words)
        return min(score / 10.0, 1.0)  # Normalize
    
    def calculate_emotional_intensity(self, content):
        """Calculate emotional intensity of the entry"""
        emotional_words = ['love', 'hate', 'angry', 'sad', 'happy', 'excited', 'worried', 'anxious', 'grateful', 'frustrated', 'amazing', 'terrible', 'wonderful', 'awful']
        content_lower = content.lower()
        
        score = sum(content_lower.count(word) for word in emotional_words)
        return min(score / 5.0, 1.0)  # Normalize
    
    def calculate_temporal_gap(self, index):
        """Calculate gap between this entry and previous"""
        if index == 0:
            return 0.0
        
        # Simple index-based gap for now
        return min(index / len(self.entries), 1.0)
    
    def save_analysis(self, output_file):
        """Save journal analysis to file"""
        
        vectors = self.create_semantic_vectors()
        
        analysis = {
            'metadata': {
                'total_entries': len(self.entries),
                'date_range': f"{self.entries[0]['date']} to {self.entries[-1]['date']}" if self.entries else "None",
                'total_words': sum(entry['word_count'] for entry in self.entries),
                'vector_count': len(vectors)
            },
            'entries': self.entries,
            'vectors': vectors,
            'theme_summary': self.get_theme_summary()
        }
        
        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"💾 Journal analysis saved to: {output_file}")
        return analysis
    
    def get_theme_summary(self):
        """Get summary of themes across all entries"""
        theme_counts = {}
        
        for entry in self.entries:
            for theme in entry['themes']:
                theme_counts[theme] = theme_counts.get(theme, 0) + 1
        
        return dict(sorted(theme_counts.items(), key=lambda x: x[1], reverse=True))

def main():
    """Extract and analyze journal entries"""
    
    journal_path = "/home/jonclaude/Downloads/AppleJournalEntries"
    
    print("📖 APPLE JOURNAL ANALYSIS - Personal Narrative Archaeology")
    print("=" * 60)
    
    extractor = JournalExtractor(journal_path)
    
    # Extract entries
    entries = extractor.extract_all_entries()
    
    if not entries:
        print("❌ No journal entries found!")
        return
    
    # Show summary
    print(f"\n📊 JOURNAL SUMMARY:")
    print(f"Date range: {entries[0]['date']} to {entries[-1]['date']}")
    print(f"Total words: {sum(entry['word_count'] for entry in entries):,}")
    print(f"Average entry length: {sum(entry['word_count'] for entry in entries) // len(entries)} words")
    
    # Show themes
    theme_summary = extractor.get_theme_summary()
    print(f"\n🎯 DOMINANT THEMES:")
    for theme, count in list(theme_summary.items())[:7]:
        print(f"  {theme}: {count} entries")
    
    # Show sample entries
    print(f"\n📝 RECENT ENTRIES:")
    for entry in entries[-3:]:  # Last 3 entries
        print(f"\n  {entry['date']} - {entry['title']}")
        print(f"  \"{entry['content'][:100]}...\"")
        print(f"  Themes: {', '.join(entry['themes'].keys())}")
    
    # Save analysis
    output_file = "/home/jonclaude/Agents/Claude on Studio/VectorVault/projects/google_meet_analysis/journal_analysis.json"
    analysis = extractor.save_analysis(output_file)
    
    print(f"\n✅ Journal processing complete!")
    print(f"Ready to correlate with conversation patterns...")

if __name__ == "__main__":
    main()