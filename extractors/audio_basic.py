#!/usr/bin/env python3
"""
VectorVault Basic Audio Extractor
Basic audio feature extraction using built-in Python libraries
"""

import wave
import math
import json
import struct
from pathlib import Path
from typing import Dict, List, Tuple

class BasicAudioExtractor:
    def __init__(self, window_size: float = 0.1):
        """
        Initialize basic audio extractor
        
        Args:
            window_size: Analysis window size in seconds (default 0.1s = 10Hz)
        """
        self.window_size = window_size
        
    def extract_from_wav(self, wav_file: str) -> Dict:
        """Extract basic features from WAV file"""
        print(f"Loading WAV file: {wav_file}")
        
        with wave.open(wav_file, 'rb') as wav:
            # Get WAV properties
            sample_rate = wav.getframerate()
            channels = wav.getnchannels()
            frames = wav.getnframes()
            duration = frames / sample_rate
            
            # Read audio data
            raw_audio = wav.readframes(frames)
            if channels == 2:
                # Convert stereo to mono by taking every other sample
                audio_data = []
                for i in range(0, len(raw_audio), 4):  # 4 bytes = 2 samples of 16-bit
                    if i + 3 < len(raw_audio):
                        sample = struct.unpack('<h', raw_audio[i:i+2])[0]  # Left channel
                        audio_data.append(sample)
            else:
                # Mono audio
                audio_data = list(struct.unpack('<' + 'h' * (len(raw_audio) // 2), raw_audio))
        
        print(f"Loaded {duration:.1f}s, {sample_rate}Hz, {channels} channels")
        
        return self.extract_features(audio_data, sample_rate)
    
    def extract_features(self, audio_data: List[int], sample_rate: int) -> Dict:
        """Extract basic audio features"""
        
        window_samples = int(sample_rate * self.window_size)
        num_windows = len(audio_data) // window_samples
        
        features = {
            'metadata': {
                'duration': len(audio_data) / sample_rate,
                'sample_rate': sample_rate,
                'window_size': self.window_size,
                'num_frames': num_windows,
                'total_samples': len(audio_data)
            },
            'timestamps': [],
            'features': {
                'rms_energy': [],
                'peak_amplitude': [],
                'zero_crossing_rate': [],
                'spectral_centroid_approx': [],
                'energy_ratio': []
            }
        }
        
        print(f"Extracting features from {num_windows} windows...")
        
        for i in range(num_windows):
            start_idx = i * window_samples
            end_idx = min(start_idx + window_samples, len(audio_data))
            window = audio_data[start_idx:end_idx]
            timestamp = i * self.window_size
            
            features['timestamps'].append(timestamp)
            
            # 1. RMS Energy
            rms = math.sqrt(sum(x*x for x in window) / len(window)) if window else 0
            features['features']['rms_energy'].append(rms)
            
            # 2. Peak Amplitude  
            peak = max(abs(x) for x in window) if window else 0
            features['features']['peak_amplitude'].append(peak)
            
            # 3. Zero Crossing Rate
            zero_crossings = 0
            for j in range(1, len(window)):
                if (window[j-1] >= 0) != (window[j] >= 0):
                    zero_crossings += 1
            zcr = zero_crossings / len(window) if window else 0
            features['features']['zero_crossing_rate'].append(zcr)
            
            # 4. Simple spectral centroid approximation
            # High-frequency vs low-frequency energy ratio
            mid_point = len(window) // 2
            low_energy = sum(abs(x) for x in window[:mid_point])
            high_energy = sum(abs(x) for x in window[mid_point:])
            centroid_approx = high_energy / (low_energy + high_energy + 1) if window else 0
            features['features']['spectral_centroid_approx'].append(centroid_approx)
            
            # 5. Energy ratio compared to previous window
            if i > 0:
                prev_rms = features['features']['rms_energy'][i-1]
                energy_ratio = rms / (prev_rms + 1) if prev_rms > 0 else 1
            else:
                energy_ratio = 1
            features['features']['energy_ratio'].append(energy_ratio)
        
        return features
    
    def create_vectors(self, features: Dict) -> List[Dict]:
        """Create dense vectors for each time frame"""
        
        vectors = []
        num_frames = features['metadata']['num_frames']
        
        for i in range(num_frames):
            vector = {
                'timestamp': features['timestamps'][i],
                'features': {
                    'rms_energy': features['features']['rms_energy'][i],
                    'peak_amplitude': features['features']['peak_amplitude'][i], 
                    'zero_crossing_rate': features['features']['zero_crossing_rate'][i],
                    'spectral_centroid_approx': features['features']['spectral_centroid_approx'][i],
                    'energy_ratio': features['features']['energy_ratio'][i]
                }
            }
            
            # Create dense vector
            dense_vector = [
                vector['features']['rms_energy'],
                vector['features']['peak_amplitude'],
                vector['features']['zero_crossing_rate'],
                vector['features']['spectral_centroid_approx'],
                vector['features']['energy_ratio']
            ]
            
            vector['dense_vector'] = dense_vector
            vectors.append(vector)
            
        return vectors
    
    def save_to_file(self, features: Dict, output_file: str):
        """Save features to JSON"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(features, f, indent=2)
            
        print(f"Features saved: {output_file}")

def main():
    """Extract features from the conversation audio"""
    extractor = BasicAudioExtractor(window_size=0.1)  # 10Hz sampling
    
    # Path to our conversation audio
    audio_file = "/home/jonclaude/Agents/Claude on Studio/Woodside-Animation/conversation_audio.wav"
    
    if Path(audio_file).exists():
        print("🎵 Starting VectorVault Audio Extraction...")
        
        # Extract features
        features = extractor.extract_from_wav(audio_file)
        vectors = extractor.create_vectors(features)
        
        print(f"\n📊 Extraction Results:")
        print(f"Duration: {features['metadata']['duration']:.1f} seconds")
        print(f"Feature vectors: {len(vectors)}")
        print(f"Vector dimensions: {len(vectors[0]['dense_vector'])}")
        print(f"Sampling rate: 10Hz (every 0.1 seconds)")
        
        # Save results
        output_file = "/home/jonclaude/Agents/Claude on Studio/VectorVault/projects/google_meet_analysis/audio_vectors.json"
        extractor.save_to_file({'features': features, 'vectors': vectors}, output_file)
        
        # Show sample data
        print(f"\n🔍 Sample vector at {vectors[0]['timestamp']:.1f}s:")
        for key, value in vectors[0]['features'].items():
            print(f"  {key}: {value:.4f}")
            
    else:
        print(f"❌ Audio file not found: {audio_file}")
        
if __name__ == "__main__":
    main()