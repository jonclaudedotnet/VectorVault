#!/usr/bin/env python3
"""
Extract funny moments and humor from the conversation
"""

import json
import re

def find_funny_moments():
    """Extract humor, laughter, and funny exchanges"""
    
    with open("/home/jonclaude/Agents/Claude on Studio/VectorVault/projects/google_meet_analysis/whisper_transcription.json", 'r') as f:
        data = json.load(f)
    
    words = data.get("words", [])
    full_text = data.get("text", "")
    
    print("😂 FUNNY MOMENTS & HUMOR IN THE CONVERSATION\n")
    print("=" * 60)
    
    # Search for explicit humor indicators
    humor_segments = []
    
    # Look for swearing/emphasis that might be funny
    swear_words = ["fuck", "shit", "damn", "hell", "jesus", "god", "crazy", "ridiculous", "stupid", "dumb", "wtf"]
    
    # Look for laughter and humor patterns
    funny_patterns = [
        "haha", "lol", "funny", "hilarious", "joke", "kidding", "serious",
        "right in my ear bones", "china number one", "white people"
    ]
    
    # Extract segments with these patterns
    for i, word in enumerate(words):
        word_lower = word["word"].lower()
        
        for pattern in swear_words + funny_patterns:
            if pattern in word_lower:
                # Get context
                start = max(0, i-20)
                end = min(len(words), i+20)
                context = " ".join([w["word"] for w in words[start:end]])
                
                humor_segments.append({
                    "time": word["start"],
                    "trigger": pattern,
                    "context": context
                })
                break
    
    # Find specific funny exchanges
    print("\n🎭 COMEDY GOLD MOMENTS:\n")
    
    # The ear bones moment
    ear_bones = find_text_segment(full_text, "ear bones")
    if ear_bones:
        print("1. THE EAR BONES MOMENT:")
        print("-" * 40)
        print(ear_bones)
        print()
    
    # China number one
    china = find_text_segment(full_text, "China number one")
    if china:
        print("2. CHINA NUMBER ONE:")
        print("-" * 40)
        print(china)
        print()
    
    # The animals count
    animals = find_text_segment(full_text, "dogs will you have")
    if animals:
        print("3. THE PET CENSUS:")
        print("-" * 40)
        print(animals)
        print()
    
    # Technical frustration humor
    print("\n💻 TECHNICAL FRUSTRATION COMEDY:\n")
    
    tech_frustration = find_text_segment(full_text, "sexy. Like this")
    if tech_frustration:
        print("Screen sharing struggles:")
        print("-" * 40)
        print(tech_frustration)
        print()
    
    # Self-deprecating humor
    print("\n🤷 SELF-DEPRECATING MOMENTS:\n")
    
    blind = find_text_segment(full_text, "really blind")
    if blind:
        print("Vision problems:")
        print("-" * 40)
        print(blind)
        print()
    
    # Philosophical humor
    print("\n🧠 PHILOSOPHICAL/ABSURD HUMOR:\n")
    
    capitalism = find_text_segment(full_text, "capitalism is no better")
    if capitalism:
        print("Political philosophy:")
        print("-" * 40)
        print(capitalism)
        print()
    
    # Jon's OG weed story
    weed = find_text_segment(full_text, "fucking OG push")
    if weed:
        print("\n🌿 JON'S CANNABIS NOSTALGIA:")
        print("-" * 40)
        print(weed)
        print()
    
    # Look for question-answer comedy
    print("\n❓ FUNNY Q&A EXCHANGES:\n")
    
    # Do I all right?
    allright = find_text_segment(full_text, "Do I all right")
    if allright:
        print("Existential check-in:")
        print("-" * 40)
        print(allright)
        print()
    
    # Count swear words for comedy intensity
    swear_count = {}
    for word in swear_words:
        count = full_text.lower().count(word)
        if count > 0:
            swear_count[word] = count
    
    print("\n📊 PROFANITY METRICS (for comedy intensity):")
    print("-" * 40)
    for word, count in sorted(swear_count.items(), key=lambda x: x[1], reverse=True):
        print(f"{word}: {count} times")
    
    return humor_segments

def find_text_segment(text, search_phrase, context_chars=200):
    """Find a phrase and return it with context"""
    lower_text = text.lower()
    index = lower_text.find(search_phrase.lower())
    
    if index > -1:
        start = max(0, index - context_chars//2)
        end = min(len(text), index + len(search_phrase) + context_chars//2)
        segment = text[start:end]
        
        # Clean it up
        segment = segment.replace("  ", " ")
        
        # Add ellipsis if truncated
        if start > 0:
            segment = "..." + segment
        if end < len(text):
            segment = segment + "..."
        
        return segment
    
    return None

if __name__ == "__main__":
    find_funny_moments()