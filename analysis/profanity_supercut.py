#!/usr/bin/env python3
"""
Extract profanity moments with context for comedy supercut
"""

import json
import subprocess
from pathlib import Path

def create_profanity_supercut():
    """Extract audio clips around profanity for comedy montage"""
    
    # Load transcription
    with open("/home/jonclaude/Agents/Claude on Studio/VectorVault/projects/google_meet_analysis/whisper_transcription.json", 'r') as f:
        data = json.load(f)
    
    words = data.get("words", [])
    
    # Define profanity to extract
    profanity_list = ["fuck", "shit", "damn", "hell", "jesus", "god", "crazy", "stupid", "dumb", "fucking"]
    
    # Find all profanity moments with timestamps
    profanity_moments = []
    
    for i, word_data in enumerate(words):
        word_lower = word_data["word"].lower().strip()
        
        for profane in profanity_list:
            if profane in word_lower:
                # Get 3 seconds context (1.5 before, 1.5 after)
                start_time = max(0, word_data["start"] - 1.5)
                end_time = word_data["end"] + 1.5
                
                # Get text context
                context_start = max(0, i - 5)
                context_end = min(len(words), i + 5)
                context_text = " ".join([words[j]["word"] for j in range(context_start, context_end)])
                
                profanity_moments.append({
                    "word": word_data["word"],
                    "category": profane,
                    "start_time": start_time,
                    "end_time": end_time,
                    "exact_time": word_data["start"],
                    "context": context_text,
                    "index": i
                })
                break
    
    # Sort by time
    profanity_moments.sort(key=lambda x: x["exact_time"])
    
    print("🎬 PROFANITY SUPERCUT GENERATOR")
    print("=" * 60)
    print(f"Found {len(profanity_moments)} profanity moments\n")
    
    # Group by category for comedy effect
    categories = {}
    for moment in profanity_moments:
        cat = moment["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(moment)
    
    print("📊 PROFANITY BREAKDOWN:")
    for cat, moments in sorted(categories.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {cat}: {len(moments)} instances")
    
    # Create extraction commands
    print("\n🎞️ AUDIO EXTRACTION COMMANDS:\n")
    
    audio_file = "/home/jonclaude/Agents/Claude on Studio/Woodside-Animation/conversation_audio.wav"
    output_dir = "/home/jonclaude/Agents/Claude on Studio/VectorVault/projects/google_meet_analysis/profanity_clips"
    
    # Create output directory command
    print(f"mkdir -p {output_dir}\n")
    
    # Generate ffmpeg commands for best moments
    print("# Extract individual clips (best 20 moments):")
    for i, moment in enumerate(profanity_moments[:20]):
        output_file = f"{output_dir}/clip_{i:03d}_{moment['category']}_{moment['exact_time']:.1f}.wav"
        
        # Calculate duration
        duration = moment["end_time"] - moment["start_time"]
        
        cmd = f"ffmpeg -i \"{audio_file}\" -ss {moment['start_time']:.2f} -t {duration:.2f} \"{output_file}\" -y"
        print(f"# {moment['context'][:50]}...")
        print(cmd)
        print()
    
    # Create concat file for montage
    print("\n# Create concat file for montage:")
    print("cat > concat_list.txt << EOF")
    for i in range(min(20, len(profanity_moments))):
        moment = profanity_moments[i]
        print(f"file 'profanity_clips/clip_{i:03d}_{moment['category']}_{moment['exact_time']:.1f}.wav'")
    print("EOF")
    
    print("\n# Create the supercut montage:")
    print("ffmpeg -f concat -safe 0 -i concat_list.txt profanity_supercut.wav")
    
    # Show some funny examples
    print("\n😂 COMEDY GOLD EXAMPLES:\n")
    
    # Find the funniest ones
    funny_ones = [m for m in profanity_moments if any(
        word in m["context"].lower() for word in 
        ["china", "ear bones", "blind", "sexy", "capitalism", "og push"]
    )]
    
    for moment in funny_ones[:5]:
        time_min = moment["exact_time"] / 60
        print(f"{time_min:.1f} min - \"{moment['word']}\" in context:")
        print(f"  \"{moment['context']}\"")
        print()
    
    # Save moment data
    output_json = "/home/jonclaude/Agents/Claude on Studio/VectorVault/projects/google_meet_analysis/profanity_moments.json"
    with open(output_json, 'w') as f:
        json.dump({
            "moments": profanity_moments,
            "categories": {k: len(v) for k, v in categories.items()},
            "total": len(profanity_moments)
        }, f, indent=2)
    
    print(f"💾 Saved moment data to: {output_json}")
    
    return profanity_moments

if __name__ == "__main__":
    create_profanity_supercut()