#!/usr/bin/env python3
"""
VectorVault Direct Whisper Transcription
Direct Whisper processing without subprocess complexity
"""

import whisper
import json
from pathlib import Path

def transcribe_conversation():
    """Transcribe the full conversation using Whisper"""
    
    audio_file = "/home/jonclaude/Agents/Claude on Studio/Woodside-Animation/conversation_audio.wav"
    
    print("🎤 Loading Whisper model...")
    model = whisper.load_model("base")  # Using base model for speed/accuracy balance
    
    print(f"🎵 Transcribing: {audio_file}")
    print("⚡ Using RTX 2070 SUPER acceleration...")
    
    # Transcribe with word-level timestamps
    result = model.transcribe(
        audio_file,
        word_timestamps=True,
        verbose=True,  # Show progress
        fp16=True,     # Use half-precision for speed on GPU
    )
    
    # Extract word-level data
    words_data = []
    for segment in result.get("segments", []):
        for word in segment.get("words", []):
            words_data.append({
                "word": word.get("word", "").strip(),
                "start": word.get("start", 0),
                "end": word.get("end", 0),
                "confidence": word.get("probability", 0.5)
            })
    
    transcription = {
        "text": result.get("text", ""),
        "language": result.get("language", "en"),
        "words": words_data,
        "segments": result.get("segments", []),
        "metadata": {
            "model": "base",
            "total_words": len(words_data),
            "duration": max([w["end"] for w in words_data]) if words_data else 0
        }
    }
    
    # Save complete transcription
    output_file = "/home/jonclaude/Agents/Claude on Studio/VectorVault/projects/google_meet_analysis/whisper_transcription.json"
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(transcription, f, indent=2)
    
    print(f"\n📊 Transcription Complete:")
    print(f"Total words: {len(words_data)}")
    print(f"Language: {transcription['language']}")
    print(f"Duration: {transcription['metadata']['duration']:.1f} seconds")
    print(f"Saved to: {output_file}")
    
    # Show sample
    if words_data:
        print(f"\n🔍 First 10 words:")
        for i, word in enumerate(words_data[:10]):
            print(f"  {word['start']:.1f}s: '{word['word']}' (confidence: {word['confidence']:.2f})")
    
    return transcription

if __name__ == "__main__":
    transcribe_conversation()