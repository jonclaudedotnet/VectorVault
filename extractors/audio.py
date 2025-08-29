#!/usr/bin/env python3
"""
VectorVault Audio Extractor
Dense audio feature extraction for conversation analysis
"""

import numpy as np
import librosa
import math
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class AudioExtractor:
    def __init__(self, 
                 sample_rate: int = 16000,
                 hop_length: int = 1600,  # 0.1 second intervals
                 n_mfcc: int = 13,
                 n_chroma: int = 12):
        """
        Initialize audio feature extractor
        
        Args:
            sample_rate: Target sample rate for analysis
            hop_length: Samples between feature frames (1600 = 0.1s at 16kHz)
            n_mfcc: Number of MFCC coefficients
            n_chroma: Number of chroma features
        """
        self.sample_rate = sample_rate
        self.hop_length = hop_length
        self.n_mfcc = n_mfcc
        self.n_chroma = n_chroma
        
    def extract_from_file(self, audio_file: str) -> Dict:
        """Extract all audio features from file"""
        print(f"Loading audio: {audio_file}")
        
        # Load audio
        try:
            audio, sr = librosa.load(audio_file, sr=self.sample_rate)
            duration = len(audio) / self.sample_rate
            print(f"Loaded {duration:.1f} seconds at {sr}Hz")
        except Exception as e:
            raise Exception(f"Failed to load audio: {e}")
            
        return self.extract_features(audio)
    
    def extract_features(self, audio: np.ndarray) -> Dict:
        """Extract comprehensive audio features"""
        
        features = {
            'metadata': {
                'duration': len(audio) / self.sample_rate,
                'sample_rate': self.sample_rate,
                'hop_length': self.hop_length,
                'num_frames': None
            },
            'features': {}
        }
        
        print("Extracting audio features...")
        
        # 1. MFCC - Spectral shape (captures voice characteristics)
        mfcc = librosa.feature.mfcc(
            y=audio, 
            sr=self.sample_rate,
            n_mfcc=self.n_mfcc,
            hop_length=self.hop_length
        )
        features['features']['mfcc'] = mfcc.T.tolist()  # Transpose for time-major
        
        # 2. Spectral Centroid - Brightness/brightness
        spectral_centroid = librosa.feature.spectral_centroid(
            y=audio,
            sr=self.sample_rate, 
            hop_length=self.hop_length
        )[0]
        features['features']['spectral_centroid'] = spectral_centroid.tolist()
        
        # 3. Zero Crossing Rate - Speech texture
        zcr = librosa.feature.zero_crossing_rate(
            audio,
            hop_length=self.hop_length
        )[0]
        features['features']['zero_crossing_rate'] = zcr.tolist()
        
        # 4. RMS Energy - Volume/intensity
        rms = librosa.feature.rms(
            y=audio,
            hop_length=self.hop_length
        )[0]
        features['features']['rms_energy'] = rms.tolist()
        
        # 5. Chroma - Harmonic content
        chroma = librosa.feature.chroma_stft(
            y=audio,
            sr=self.sample_rate,
            n_chroma=self.n_chroma,
            hop_length=self.hop_length
        )
        features['features']['chroma'] = chroma.T.tolist()
        
        # 6. Tempo and beat tracking
        tempo, beats = librosa.beat.beat_track(
            y=audio,
            sr=self.sample_rate,
            hop_length=self.hop_length
        )
        features['features']['tempo'] = float(tempo)
        features['features']['beat_frames'] = beats.tolist()
        
        # 7. Onset detection - Major acoustic events
        onsets = librosa.onset.onset_detect(
            y=audio,
            sr=self.sample_rate,
            hop_length=self.hop_length,
            units='time'
        )
        features['features']['onsets'] = onsets.tolist()
        
        # Generate timestamps for each frame
        num_frames = len(features['features']['rms_energy'])
        timestamps = [i * self.hop_length / self.sample_rate for i in range(num_frames)]
        features['timestamps'] = timestamps
        features['metadata']['num_frames'] = num_frames
        
        print(f"Extracted {num_frames} feature frames at 10Hz")
        return features
    
    def create_dense_vectors(self, features: Dict) -> List[Dict]:
        """Create dense vectors combining all features for each time frame"""
        
        vectors = []
        num_frames = features['metadata']['num_frames']
        
        for i in range(num_frames):
            vector = {
                'timestamp': features['timestamps'][i],
                'features': {
                    'mfcc': features['features']['mfcc'][i],
                    'spectral_centroid': features['features']['spectral_centroid'][i],
                    'zero_crossing_rate': features['features']['zero_crossing_rate'][i], 
                    'rms_energy': features['features']['rms_energy'][i],
                    'chroma': features['features']['chroma'][i]
                }
            }
            
            # Flatten into single dense vector for storage
            dense_vector = []
            dense_vector.extend(vector['features']['mfcc'])  # 13 dims
            dense_vector.append(vector['features']['spectral_centroid'])  # 1 dim
            dense_vector.append(vector['features']['zero_crossing_rate'])  # 1 dim
            dense_vector.append(vector['features']['rms_energy'])  # 1 dim
            dense_vector.extend(vector['features']['chroma'])  # 12 dims
            
            vector['dense_vector'] = dense_vector  # 28-dimensional vector
            vectors.append(vector)
            
        return vectors
    
    def save_features(self, features: Dict, output_file: str):
        """Save features to JSON file"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(features, f, indent=2)
            
        print(f"Features saved to: {output_file}")

def main():
    """Test the audio extractor"""
    extractor = AudioExtractor()
    
    # Use the conversation audio we already extracted
    audio_file = "/home/jonclaude/Agents/Claude on Studio/Woodside-Animation/conversation_audio.wav"
    
    if Path(audio_file).exists():
        features = extractor.extract_from_file(audio_file)
        vectors = extractor.create_dense_vectors(features)
        
        print(f"\nExtraction complete:")
        print(f"- Duration: {features['metadata']['duration']:.1f} seconds")
        print(f"- Feature frames: {len(vectors)}")
        print(f"- Vector dimensions: {len(vectors[0]['dense_vector'])}")
        print(f"- First vector timestamp: {vectors[0]['timestamp']:.1f}s")
        print(f"- Last vector timestamp: {vectors[-1]['timestamp']:.1f}s")
        
        # Save to analysis directory
        output_file = "/home/jonclaude/Agents/Claude on Studio/VectorVault/projects/google_meet_analysis/audio_features.json"
        extractor.save_features(features, output_file)
        
    else:
        print(f"Audio file not found: {audio_file}")
        print("Please extract audio from MP4 first")

if __name__ == "__main__":
    main()