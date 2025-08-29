#!/usr/bin/env python3
"""
Extract stories and narratives from the conversation
"""

import json
from pathlib import Path

def extract_stories():
    """Extract coherent story segments from the conversation"""
    
    # Load transcription
    with open("/home/jonclaude/Agents/Claude on Studio/VectorVault/projects/google_meet_analysis/whisper_transcription.json", 'r') as f:
        transcription = json.load(f)
    
    words = transcription.get("words", [])
    
    # Look for story indicators and longer narrative segments
    story_segments = []
    
    # Process in chunks to find sustained narrative sections
    chunk_size = 100  # words
    for i in range(0, len(words) - chunk_size, 50):  # Sliding window
        chunk = words[i:i+chunk_size]
        text = " ".join([w["word"] for w in chunk])
        
        # Look for narrative indicators
        story_indicators = [
            "when I", "I was", "I remember", "there was", "we were",
            "this guy", "this woman", "she told", "he said", "they had",
            "happened", "story", "told me", "went to", "came to",
            "years ago", "back when", "used to", "one time"
        ]
        
        # Count narrative elements
        narrative_score = sum(1 for indicator in story_indicators if indicator in text.lower())
        
        if narrative_score >= 3:  # Strong narrative segment
            story_segments.append({
                "start_time": chunk[0]["start"],
                "end_time": chunk[-1]["end"],
                "text": text,
                "score": narrative_score
            })
    
    # Merge overlapping segments
    merged_stories = []
    for segment in story_segments:
        if merged_stories and segment["start_time"] < merged_stories[-1]["end_time"] + 10:
            # Extend previous story
            merged_stories[-1]["end_time"] = segment["end_time"]
            merged_stories[-1]["text"] += " " + segment["text"]
        else:
            merged_stories.append(segment)
    
    # Find the most substantial stories
    print("📚 STORIES FOUND IN THE CONVERSATION:\n")
    
    for i, story in enumerate(merged_stories[:5], 1):  # Top 5 stories
        duration = story["end_time"] - story["start_time"]
        if duration > 30:  # Substantial stories over 30 seconds
            time_min = story["start_time"] / 60
            
            print(f"Story {i} (at {time_min:.1f} minutes, {duration:.0f} seconds long):")
            print("-" * 60)
            
            # Clean up the text for readability
            text = story["text"].replace("  ", " ")
            
            # Show first 300 chars of the story
            if len(text) > 300:
                print(f"{text[:300]}...")
            else:
                print(text)
            print("\n")
    
    # Look for specific story patterns
    print("\n🔍 SPECIFIC STORY THEMES:\n")
    
    # Search for China story
    china_story = find_story_about(words, "China", context_words=200)
    if china_story:
        print("China Story:")
        print("-" * 60)
        print(china_story[:500] + "...\n")
    
    # Search for camp/work stories
    camp_story = find_story_about(words, "camp", context_words=150)
    if camp_story:
        print("Camp/Work Story:")
        print("-" * 60)
        print(camp_story[:500] + "...\n")
    
    # Search for technology/AI stories
    ai_story = find_story_about(words, "DeepSeek", context_words=150)
    if ai_story:
        print("AI/Technology Story:")
        print("-" * 60)
        print(ai_story[:500] + "...\n")
    
    return merged_stories

def find_story_about(words, topic, context_words=100):
    """Find story segments about a specific topic"""
    
    for i, word in enumerate(words):
        if topic.lower() in word["word"].lower():
            # Get surrounding context
            start = max(0, i - context_words//2)
            end = min(len(words), i + context_words//2)
            
            context = " ".join([w["word"] for w in words[start:end]])
            return context
    
    return None

if __name__ == "__main__":
    extract_stories()