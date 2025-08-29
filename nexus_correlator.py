#!/usr/bin/env python3
"""
VectorVault Nexus Correlator
Cross-modal pattern discovery between conversations and journals
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
import math

class NexusCorrelator:
    def __init__(self):
        self.conversation_data = None
        self.journal_data = None
        self.correlations = []
        
    def load_data(self):
        """Load conversation and journal analysis data"""
        
        # Load conversation analysis
        conv_file = "/home/jonclaude/Agents/Claude on Studio/VectorVault/projects/google_meet_analysis/whisper_transcription.json"
        with open(conv_file, 'r') as f:
            self.conversation_data = json.load(f)
        
        # Load journal analysis
        journal_file = "/home/jonclaude/Agents/Claude on Studio/VectorVault/projects/google_meet_analysis/journal_analysis.json"
        with open(journal_file, 'r') as f:
            self.journal_data = json.load(f)
        
        print("📊 NEXUS DATA LOADED:")
        print(f"  Conversation: {len(self.conversation_data.get('words', []))} words")
        print(f"  Journal: {self.journal_data['metadata']['total_entries']} entries")
    
    def find_theme_correlations(self):
        """Find theme overlaps between conversation and journal"""
        
        # Extract conversation themes from text
        words_text = " ".join([w["word"] for w in self.conversation_data.get("words", [])])
        conv_themes = self.extract_conversation_themes(words_text)
        
        # Get journal themes
        journal_themes = self.journal_data.get("theme_summary", {})
        
        print("\n🔍 THEME CORRELATION ANALYSIS:")
        print(f"Conversation themes: {list(conv_themes.keys())}")
        print(f"Journal themes: {list(journal_themes.keys())}")
        
        # Find overlapping themes
        overlapping = set(conv_themes.keys()) & set(journal_themes.keys())
        
        correlations = []
        for theme in overlapping:
            correlation = {
                "theme": theme,
                "conversation_strength": conv_themes[theme],
                "journal_entries": journal_themes[theme],
                "correlation_score": self.calculate_theme_correlation(theme, conv_themes[theme], journal_themes[theme])
            }
            correlations.append(correlation)
        
        return sorted(correlations, key=lambda x: x["correlation_score"], reverse=True)
    
    def extract_conversation_themes(self, text):
        """Extract themes from conversation text"""
        text_lower = text.lower()
        
        themes = {
            'technology': text_lower.count('computer') + text_lower.count('ai') + text_lower.count('digital'),
            'relationships': text_lower.count('friend') + text_lower.count('maya') + text_lower.count('family'),
            'work': text_lower.count('work') + text_lower.count('job') + text_lower.count('business'),
            'creativity': text_lower.count('creative') + text_lower.count('video') + text_lower.count('film'),
            'food': text_lower.count('food') + text_lower.count('eat') + text_lower.count('restaurant'),
            'health': text_lower.count('health') + text_lower.count('doctor') + text_lower.count('vision'),
            'reflection': text_lower.count('think') + text_lower.count('feel') + text_lower.count('remember'),
            'travel': text_lower.count('travel') + text_lower.count('trip') + text_lower.count('visit'),
            'learning': text_lower.count('learn') + text_lower.count('teach') + text_lower.count('study')
        }
        
        return {theme: count for theme, count in themes.items() if count > 0}
    
    def calculate_theme_correlation(self, theme, conv_strength, journal_entries):
        """Calculate correlation strength between conversation and journal theme"""
        
        # Normalize conversation strength (per 1000 words)
        total_words = len(self.conversation_data.get("words", []))
        conv_normalized = (conv_strength / total_words) * 1000
        
        # Normalize journal entries (per 10 entries)
        total_journal_entries = self.journal_data['metadata']['total_entries']
        journal_normalized = (journal_entries / total_journal_entries) * 10
        
        # Calculate correlation score (geometric mean)
        return math.sqrt(conv_normalized * journal_normalized)
    
    def find_temporal_patterns(self):
        """Find temporal patterns in journal entries"""
        
        entries = self.journal_data["entries"]
        
        # Group by month
        monthly_patterns = {}
        theme_evolution = {}
        
        for entry in entries:
            try:
                date_obj = datetime.strptime(entry["date"], "%Y-%m-%d")
                month_key = date_obj.strftime("%Y-%m")
                
                if month_key not in monthly_patterns:
                    monthly_patterns[month_key] = {
                        "entry_count": 0,
                        "word_count": 0,
                        "themes": {}
                    }
                
                monthly_patterns[month_key]["entry_count"] += 1
                monthly_patterns[month_key]["word_count"] += entry["word_count"]
                
                # Track theme evolution
                for theme in entry["themes"]:
                    if theme not in theme_evolution:
                        theme_evolution[theme] = {}
                    if month_key not in theme_evolution[theme]:
                        theme_evolution[theme][month_key] = 0
                    theme_evolution[theme][month_key] += 1
                    
                    if theme not in monthly_patterns[month_key]["themes"]:
                        monthly_patterns[month_key]["themes"][theme] = 0
                    monthly_patterns[month_key]["themes"][theme] += 1
                    
            except ValueError:
                continue
        
        return monthly_patterns, theme_evolution
    
    def generate_narrative_insights(self):
        """Generate insights about the personal narrative"""
        
        insights = {
            "dominant_themes": [],
            "temporal_patterns": {},
            "conversation_journal_correlation": [],
            "narrative_evolution": {},
            "personal_reflection_score": 0
        }
        
        # Theme correlations
        theme_correlations = self.find_theme_correlations()
        insights["conversation_journal_correlation"] = theme_correlations
        
        # Temporal patterns
        monthly_patterns, theme_evolution = self.find_temporal_patterns()
        insights["temporal_patterns"] = monthly_patterns
        insights["narrative_evolution"] = theme_evolution
        
        # Calculate personal reflection score
        reflection_entries = [e for e in self.journal_data["entries"] if "reflection" in e["themes"]]
        insights["personal_reflection_score"] = len(reflection_entries) / self.journal_data['metadata']['total_entries']
        
        # Identify dominant themes
        theme_summary = self.journal_data.get("theme_summary", {})
        insights["dominant_themes"] = list(theme_summary.keys())[:5]
        
        return insights
    
    def save_nexus_analysis(self, output_file):
        """Save complete nexus analysis"""
        
        insights = self.generate_narrative_insights()
        
        nexus_analysis = {
            "metadata": {
                "analysis_date": datetime.now().isoformat(),
                "conversation_words": len(self.conversation_data.get("words", [])),
                "journal_entries": self.journal_data['metadata']['total_entries'],
                "date_range": self.journal_data['metadata']['date_range']
            },
            "insights": insights,
            "raw_correlations": self.correlations
        }
        
        with open(output_file, 'w') as f:
            json.dump(nexus_analysis, f, indent=2)
        
        print(f"\n💾 Nexus analysis saved to: {output_file}")
        return nexus_analysis
    
    def print_summary(self):
        """Print analysis summary"""
        
        insights = self.generate_narrative_insights()
        
        print("\n" + "=" * 70)
        print("🧠 PERSONAL NARRATIVE NEXUS - Analysis Complete")
        print("=" * 70)
        
        print(f"\n📊 DATA SCOPE:")
        print(f"  Journal entries: {self.journal_data['metadata']['total_entries']} ({self.journal_data['metadata']['date_range']})")
        print(f"  Conversation length: {len(self.conversation_data.get('words', []))} words")
        print(f"  Total words analyzed: {self.journal_data['metadata']['total_words'] + len(self.conversation_data.get('words', []))}")
        
        print(f"\n🎯 DOMINANT LIFE THEMES:")
        for theme in insights["dominant_themes"]:
            print(f"  {theme}")
        
        print(f"\n🔗 CONVERSATION-JOURNAL CORRELATIONS:")
        for corr in insights["conversation_journal_correlation"][:3]:
            print(f"  {corr['theme']}: {corr['correlation_score']:.2f} correlation score")
        
        print(f"\n🧘 REFLECTION SCORE: {insights['personal_reflection_score']:.2f}")
        print(f"   ({insights['personal_reflection_score']*100:.1f}% of journal entries contain personal reflection)")
        
        print(f"\n✨ NARRATIVE ARCHAEOLOGY COMPLETE")
        print(f"   Ready for pattern discovery and story extraction...")

def main():
    """Run complete nexus correlation analysis"""
    
    print("🔬 VECTORVAULT NEXUS CORRELATOR")
    print("Cross-modal Personal Narrative Analysis")
    print("=" * 60)
    
    correlator = NexusCorrelator()
    
    # Load all data
    correlator.load_data()
    
    # Generate analysis
    output_file = "/home/jonclaude/Agents/Claude on Studio/VectorVault/projects/google_meet_analysis/nexus_analysis.json"
    analysis = correlator.save_nexus_analysis(output_file)
    
    # Print summary
    correlator.print_summary()

if __name__ == "__main__":
    main()