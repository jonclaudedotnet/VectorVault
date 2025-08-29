#!/usr/bin/env python3
"""
Create semantic vectors from complete Whisper transcription
"""

import json
from pathlib import Path

def create_semantic_vectors_from_transcription():
    """Create semantic vectors from the completed transcription"""
    
    transcription_file = "/home/jonclaude/Agents/Claude on Studio/VectorVault/projects/google_meet_analysis/whisper_transcription.json"
    
    with open(transcription_file, 'r') as f:
        transcription = json.load(f)
    
    words = transcription.get("words", [])
    print(f"📝 Processing {len(words)} words from transcription...")
    
    # Create semantic vectors with 10-second windows
    vectors = []
    window_size = 10.0  # seconds
    duration = transcription['metadata']['duration']
    
    current_time = 0
    while current_time < duration:
        window_end = current_time + window_size
        
        # Get words in this time window
        window_words = [w for w in words 
                       if w["start"] >= current_time and w["start"] < window_end]
        
        if window_words:
            # Calculate semantic features
            word_count = len(window_words)
            avg_confidence = sum([w["confidence"] for w in window_words]) / word_count
            avg_word_length = sum([len(w["word"]) for w in window_words]) / word_count
            
            # Vocabulary diversity
            unique_words = len(set([w["word"].lower().strip() for w in window_words]))
            vocab_diversity = unique_words / word_count if word_count > 0 else 0
            
            # Speaking rate (words per second)
            time_span = window_end - current_time
            speaking_rate = word_count / time_span if time_span > 0 else 0
            
            # Text content
            text_snippet = " ".join([w["word"] for w in window_words])
            
            vector = {
                "timestamp": current_time,
                "features": {
                    "word_count": word_count,
                    "avg_confidence": avg_confidence,
                    "avg_word_length": avg_word_length,
                    "vocab_diversity": vocab_diversity,
                    "speaking_rate": speaking_rate
                },
                "words": [w["word"] for w in window_words],
                "text_snippet": text_snippet,
                "metadata": {
                    "window_start": current_time,
                    "window_end": window_end,
                    "actual_words": len(window_words)
                }
            }
            
            # Create dense vector (5-dimensional like audio)
            vector["dense_vector"] = [
                min(word_count / 50.0, 1.0),     # Normalized word count (cap at 50)
                avg_confidence,                  # Confidence score
                min(avg_word_length / 15.0, 1.0), # Normalized word length (cap at 15)
                vocab_diversity,                 # Vocabulary diversity
                min(speaking_rate / 5.0, 1.0)   # Normalized speaking rate (cap at 5 wps)
            ]
            
            vectors.append(vector)
        
        current_time += window_size
    
    # Save semantic vectors
    semantic_data = {
        "metadata": {
            "source": "whisper_transcription",
            "total_words": len(words),
            "duration": duration,
            "vector_count": len(vectors),
            "window_size": window_size
        },
        "vectors": vectors
    }
    
    output_file = "/home/jonclaude/Agents/Claude on Studio/VectorVault/projects/google_meet_analysis/semantic_vectors_complete.json"
    with open(output_file, 'w') as f:
        json.dump(semantic_data, f, indent=2)
    
    print(f"✅ Created {len(vectors)} semantic vectors")
    print(f"📄 Saved to: {output_file}")
    
    # Show sample
    if vectors:
        sample = vectors[len(vectors)//2]  # Middle of conversation
        print(f"\n🔍 Sample vector at {sample['timestamp']:.1f}s:")
        print(f"  Text: \"{sample['text_snippet'][:60]}...\"")
        print(f"  Word count: {sample['features']['word_count']}")
        print(f"  Confidence: {sample['features']['avg_confidence']:.3f}")
        print(f"  Speaking rate: {sample['features']['speaking_rate']:.2f} words/sec")
    
    return semantic_data

if __name__ == "__main__":
    create_semantic_vectors_from_transcription()