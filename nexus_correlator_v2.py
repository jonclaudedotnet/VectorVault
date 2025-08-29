#!/usr/bin/env python3
"""
VectorVault Nexus Correlator v2
Cross-modal pattern discovery: Conversation + Journal + Email
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class UnifiedNexusCorrelator:
    def __init__(self):
        self.db_path = "/home/jonclaude/Agents/Claude on Studio/VectorVault/storage/vectors.db"
        self.conversation_data = None
        self.journal_data = None
        self.email_vectors = []
        
    def load_all_data(self):
        """Load conversation, journal, and email data"""
        
        print("🔗 UNIFIED NEXUS CORRELATOR V2")
        print("Cross-modal Personal Narrative Analysis")
        print("=" * 70)
        
        # Load conversation data
        conv_file = "/home/jonclaude/Agents/Claude on Studio/VectorVault/projects/google_meet_analysis/whisper_transcription.json"
        with open(conv_file, 'r') as f:
            self.conversation_data = json.load(f)
        
        # Load journal data
        journal_file = "/home/jonclaude/Agents/Claude on Studio/VectorVault/projects/google_meet_analysis/journal_analysis.json"
        with open(journal_file, 'r') as f:
            self.journal_data = json.load(f)
        
        # Load email vectors from database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT data_type, timestamp, content, metadata, importance_score 
                FROM vectors WHERE data_type = 'email'
            ''')
            
            email_rows = cursor.fetchall()
            
            for row in email_rows:
                self.email_vectors.append({
                    'data_type': row[0],
                    'timestamp': row[1],
                    'content': row[2],
                    'metadata': json.loads(row[3]) if row[3] else {},
                    'importance_score': row[4]
                })
        
        print(f"📊 DATA LOADED:")
        print(f"  Conversation: {len(self.conversation_data.get('words', []))} words")
        print(f"  Journal: {self.journal_data['metadata']['total_entries']} entries")
        print(f"  Email: {len(self.email_vectors)} vectors")
        
        return True
    
    def analyze_cross_modal_themes(self):
        """Analyze themes across all three data sources"""
        
        # Extract themes from conversation
        conv_text = " ".join([w["word"] for w in self.conversation_data.get("words", [])])
        conv_themes = self.extract_themes_from_text(conv_text, "conversation")
        
        # Get journal themes
        journal_themes = self.journal_data.get("theme_summary", {})
        
        # Extract email themes
        email_themes = defaultdict(int)
        for email in self.email_vectors:
            classification = email['metadata'].get('classification', 'unknown')
            email_themes[classification] += 1
        
        # Find cross-modal correlations
        cross_correlations = {}
        
        # Technology theme analysis
        tech_score = {
            'conversation': conv_themes.get('technology', 0),
            'journal': journal_themes.get('technology', 0),
            'email': email_themes.get('business', 0) + email_themes.get('subscriptions', 0)  # Tech-related emails
        }
        cross_correlations['technology'] = tech_score
        
        # Personal/relationship theme analysis
        personal_score = {
            'conversation': conv_themes.get('relationships', 0),
            'journal': journal_themes.get('relationships', 0),
            'email': email_themes.get('personal', 0)
        }
        cross_correlations['relationships'] = personal_score
        
        # Work/business theme analysis
        work_score = {
            'conversation': conv_themes.get('work', 0),
            'journal': journal_themes.get('work', 0),
            'email': email_themes.get('business', 0)
        }
        cross_correlations['work'] = work_score
        
        return cross_correlations, email_themes
    
    def extract_themes_from_text(self, text, source_type):
        """Extract themes from text content"""
        
        text_lower = text.lower()
        
        themes = {
            'technology': text_lower.count('computer') + text_lower.count('ai') + text_lower.count('tech'),
            'relationships': text_lower.count('friend') + text_lower.count('maya') + text_lower.count('family'),
            'work': text_lower.count('work') + text_lower.count('job') + text_lower.count('business'),
            'creativity': text_lower.count('creative') + text_lower.count('video') + text_lower.count('vr'),
            'health': text_lower.count('health') + text_lower.count('vision') + text_lower.count('doctor')
        }
        
        return themes
    
    def analyze_temporal_patterns(self):
        """Analyze patterns across time in all data sources"""
        
        # Journal temporal patterns (already have years)
        journal_years = defaultdict(int)
        for entry in self.journal_data.get("entries", []):
            try:
                year = entry["date"][:4]  # Extract year from YYYY-MM-DD
                journal_years[year] += 1
            except:
                pass
        
        # Email temporal patterns
        email_years = defaultdict(int)
        for email in self.email_vectors:
            year_from_metadata = email['metadata'].get('year')
            if year_from_metadata:
                email_years[str(year_from_metadata)] += 1
        
        # Conversation is single point in time (2024)
        conversation_year = "2024"  # Maya conversation
        
        return {
            'journal_years': dict(journal_years),
            'email_years': dict(email_years),
            'conversation_year': conversation_year
        }
    
    def find_narrative_peaks(self, cross_correlations, temporal_patterns):
        """Identify peak narrative periods"""
        
        peaks = []
        
        # Find years with multiple data sources active
        all_years = set()
        all_years.update(temporal_patterns['journal_years'].keys())
        all_years.update(temporal_patterns['email_years'].keys())
        
        for year in sorted(all_years):
            year_data = {
                'year': year,
                'journal_entries': temporal_patterns['journal_years'].get(year, 0),
                'email_activity': temporal_patterns['email_years'].get(year, 0),
                'total_activity': temporal_patterns['journal_years'].get(year, 0) + temporal_patterns['email_years'].get(year, 0)
            }
            
            # Consider significant if multiple sources or high activity
            if year_data['total_activity'] > 5:
                peaks.append(year_data)
        
        return sorted(peaks, key=lambda x: x['total_activity'], reverse=True)
    
    def generate_unified_insights(self):
        """Generate comprehensive insights across all data"""
        
        cross_correlations, email_themes = self.analyze_cross_modal_themes()
        temporal_patterns = self.analyze_temporal_patterns()
        narrative_peaks = self.find_narrative_peaks(cross_correlations, temporal_patterns)
        
        # Calculate overall narrative coherence
        coherence_score = self.calculate_narrative_coherence(cross_correlations)
        
        insights = {
            'analysis_date': datetime.now().isoformat(),
            'data_sources': {
                'conversation_words': len(self.conversation_data.get('words', [])),
                'journal_entries': self.journal_data['metadata']['total_entries'],
                'email_vectors': len(self.email_vectors)
            },
            'cross_modal_themes': cross_correlations,
            'email_classification_breakdown': dict(email_themes),
            'temporal_patterns': temporal_patterns,
            'narrative_peaks': narrative_peaks[:5],  # Top 5 peak periods
            'narrative_coherence_score': coherence_score,
            'unified_assessment': self.create_unified_assessment(cross_correlations, narrative_peaks, coherence_score)
        }
        
        return insights
    
    def calculate_narrative_coherence(self, cross_correlations):
        """Calculate how coherent the narrative is across modalities"""
        
        coherence_scores = []
        
        for theme, scores in cross_correlations.items():
            # Calculate variance across modalities (lower variance = higher coherence)
            values = list(scores.values())
            if len(values) > 1 and max(values) > 0:
                # Normalize values
                max_val = max(values)
                normalized = [v / max_val for v in values]
                
                # Calculate coherence (inverse of variance)
                mean_val = sum(normalized) / len(normalized)
                variance = sum((v - mean_val) ** 2 for v in normalized) / len(normalized)
                coherence = 1.0 - variance  # Higher coherence = lower variance
                
                coherence_scores.append(coherence)
        
        return sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0.0
    
    def create_unified_assessment(self, cross_correlations, narrative_peaks, coherence_score):
        """Create overall assessment of personal narrative"""
        
        # Identify dominant themes
        theme_strengths = {}
        for theme, scores in cross_correlations.items():
            total_strength = sum(scores.values())
            theme_strengths[theme] = total_strength
        
        dominant_theme = max(theme_strengths, key=theme_strengths.get) if theme_strengths else "unknown"
        
        # Assess temporal span
        peak_years = [p['year'] for p in narrative_peaks]
        temporal_span = f"{min(peak_years)} to {max(peak_years)}" if peak_years else "Limited"
        
        # Overall assessment
        if coherence_score > 0.7:
            coherence_level = "High - consistent themes across all data sources"
        elif coherence_score > 0.4:
            coherence_level = "Moderate - some thematic consistency"
        else:
            coherence_level = "Low - varied themes across different communication modes"
        
        return {
            'dominant_life_theme': dominant_theme,
            'temporal_span': temporal_span,
            'narrative_coherence': coherence_level,
            'data_richness': 'High' if len(narrative_peaks) > 3 else 'Moderate',
            'cross_modal_correlation_strength': coherence_score
        }

def main():
    """Run unified nexus correlation analysis"""
    
    correlator = UnifiedNexusCorrelator()
    
    # Load all data sources
    if not correlator.load_all_data():
        print("❌ Failed to load data")
        return
    
    # Generate unified insights
    insights = correlator.generate_unified_insights()
    
    # Save comprehensive analysis
    output_file = "/home/jonclaude/Agents/Claude on Studio/VectorVault/projects/email_analysis/unified_nexus_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(insights, f, indent=2)
    
    print(f"\n💾 Unified analysis saved to: {output_file}")
    
    # Print comprehensive summary
    print(f"\n" + "=" * 80)
    print(f"🧠 UNIFIED PERSONAL NARRATIVE NEXUS - Complete Analysis")
    print(f"=" * 80)
    
    print(f"\n📊 DATA INTEGRATION:")
    ds = insights['data_sources']
    print(f"   Conversation: {ds['conversation_words']} words (Maya - 40-year friendship)")
    print(f"   Journal: {ds['journal_entries']} entries (2024-2025 personal thoughts)")
    print(f"   Email: {ds['email_vectors']} vectors (2020-2021 correspondence)")
    
    print(f"\n🎯 DOMINANT THEMES (Cross-Modal Analysis):")
    for theme, scores in insights['cross_modal_themes'].items():
        print(f"   {theme.title()}:")
        for source, score in scores.items():
            print(f"     {source}: {score}")
    
    print(f"\n📈 NARRATIVE PEAKS:")
    for peak in insights['narrative_peaks'][:3]:
        print(f"   {peak['year']}: {peak['total_activity']} activities (journal: {peak['journal_entries']}, email: {peak['email_activity']})")
    
    ua = insights['unified_assessment']
    print(f"\n🎪 UNIFIED ASSESSMENT:")
    print(f"   Dominant Theme: {ua['dominant_life_theme']}")
    print(f"   Temporal Span: {ua['temporal_span']}")
    print(f"   Narrative Coherence: {ua['narrative_coherence']}")
    print(f"   Data Richness: {ua['data_richness']}")
    print(f"   Correlation Strength: {ua['cross_modal_correlation_strength']:.3f}")
    
    print(f"\n✨ PERSONAL NARRATIVE ARCHAEOLOGY COMPLETE")
    print(f"   Your complete digital story spans multiple years and communication modes")
    print(f"   Ready for pattern discovery, story extraction, and creative synthesis!")

if __name__ == "__main__":
    main()