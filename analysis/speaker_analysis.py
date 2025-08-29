#!/usr/bin/env python3
"""
Analyze conversation for speaker changes and participant identification
"""

import json
from pathlib import Path

def analyze_speakers():
    """Analyze the transcription for speaker patterns and changes"""
    
    # Load the complete transcription
    transcription_file = "/home/jonclaude/Agents/Claude on Studio/VectorVault/projects/google_meet_analysis/whisper_transcription.json"
    
    with open(transcription_file, 'r') as f:
        transcription = json.load(f)
    
    # Get all text
    full_text = transcription.get("text", "")
    words = transcription.get("words", [])
    
    print("🔍 Analyzing conversation for speaker patterns...\n")
    
    # Look for name mentions
    name_mentions = {
        "maya": [],
        "paul": [],
        "catherine": [],
        "china": [],  # Topic that might indicate different conversation
        "dog": [],    # Early conversation topic
        "ai": [],     # Technology discussion
        "child": [],  # Parenting topic
    }
    
    # Search for names and key topics
    for i, word_data in enumerate(words):
        word_lower = word_data["word"].lower().strip()
        timestamp = word_data["start"]
        
        for name in name_mentions:
            if name in word_lower:
                name_mentions[name].append({
                    "time": timestamp,
                    "word": word_data["word"],
                    "context": get_context(words, i, 5)  # Get 5 words before and after
                })
    
    # Analyze conversation segments
    print("📊 Name/Topic Mentions Found:")
    for name, mentions in name_mentions.items():
        if mentions:
            print(f"\n'{name.upper()}': {len(mentions)} mentions")
            for i, mention in enumerate(mentions[:3]):  # Show first 3
                time_min = mention["time"] / 60
                print(f"  - {time_min:.1f} min: \"{mention['context']}\"")
    
    # Look for conversation transitions
    print("\n🔄 Potential Conversation Transitions:")
    
    # Check for long silences that might indicate person change
    silence_gaps = []
    for i in range(1, len(words)):
        gap = words[i]["start"] - words[i-1]["end"]
        if gap > 5.0:  # More than 5 seconds silence
            silence_gaps.append({
                "time": words[i]["start"],
                "gap_duration": gap,
                "before": words[i-1]["word"],
                "after": words[i]["word"]
            })
    
    # Show significant gaps
    if silence_gaps:
        print(f"\nFound {len(silence_gaps)} significant pauses (>5 seconds):")
        for gap in silence_gaps[:5]:  # Show first 5
            time_min = gap["time"] / 60
            print(f"  - {time_min:.1f} min: {gap['gap_duration']:.1f}s pause")
            print(f"    Before: '{gap['before']}' → After: '{gap['after']}'")
    
    # Analyze conversation topics over time
    print("\n📈 Conversation Topic Evolution:")
    
    # Divide conversation into thirds
    duration = transcription["metadata"]["duration"]
    third = duration / 3
    
    segments = {
        "First Third (0-34 min)": {"start": 0, "end": third},
        "Middle Third (34-68 min)": {"start": third, "end": 2*third},
        "Final Third (68-103 min)": {"start": 2*third, "end": duration}
    }
    
    for segment_name, times in segments.items():
        segment_words = [w for w in words 
                        if w["start"] >= times["start"] and w["start"] < times["end"]]
        
        if segment_words:
            # Get sample text from segment
            sample_start = len(segment_words) // 2
            sample_words = segment_words[sample_start:sample_start+20]
            sample_text = " ".join([w["word"] for w in sample_words])
            
            print(f"\n{segment_name}:")
            print(f"  Sample: \"{sample_text[:100]}...\"")
    
    return name_mentions, silence_gaps

def get_context(words, index, window=5):
    """Get surrounding words for context"""
    start = max(0, index - window)
    end = min(len(words), index + window + 1)
    
    context_words = [words[i]["word"] for i in range(start, end)]
    return " ".join(context_words)

if __name__ == "__main__":
    analyze_speakers()