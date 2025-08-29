#!/usr/bin/env python3
"""
VectorVault Basic Visual Extractor
Extract visual features from video frames using basic image processing
"""

import subprocess
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple
import tempfile
import os

class BasicVisualExtractor:
    def __init__(self, 
                 sample_rate: float = 1.0,  # 1 frame per second
                 frame_width: int = 320,    # Downscale for processing
                 frame_height: int = 240):
        """
        Initialize visual extractor
        
        Args:
            sample_rate: Frames to extract per second
            frame_width: Width to scale frames for processing  
            frame_height: Height to scale frames for processing
        """
        self.sample_rate = sample_rate
        self.frame_width = frame_width
        self.frame_height = frame_height
        
    def extract_frames_from_mp4(self, mp4_file: str, temp_dir: str) -> List[str]:
        """Extract frames from MP4 using ffmpeg"""
        
        print(f"Extracting frames from: {mp4_file}")
        print(f"Sample rate: {self.sample_rate} fps")
        
        # Create frame extraction command
        output_pattern = os.path.join(temp_dir, "frame_%06d.png")
        
        cmd = [
            'ffmpeg',
            '-i', mp4_file,
            '-vf', f'fps={self.sample_rate},scale={self.frame_width}:{self.frame_height}',
            '-y',  # Overwrite output files
            output_pattern
        ]
        
        # Run extraction
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"ffmpeg failed: {result.stderr}")
        except FileNotFoundError:
            raise Exception("ffmpeg not found. Please install ffmpeg.")
            
        # Get list of extracted frames
        frame_files = sorted([
            os.path.join(temp_dir, f) for f in os.listdir(temp_dir) 
            if f.startswith('frame_') and f.endswith('.png')
        ])
        
        print(f"Extracted {len(frame_files)} frames")
        return frame_files
    
    def analyze_frame_basic(self, frame_file: str) -> Dict:
        """Basic frame analysis using image statistics"""
        
        # For now, we'll use ffprobe to get basic frame statistics
        # This avoids needing PIL/OpenCV dependencies
        
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_frames',
            '-select_streams', 'v:0',
            frame_file
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                # Fallback to basic file analysis
                return self.analyze_frame_fallback(frame_file)
                
            frame_data = json.loads(result.stdout)
            if 'frames' in frame_data and len(frame_data['frames']) > 0:
                frame_info = frame_data['frames'][0]
                
                return {
                    'file_size': os.path.getsize(frame_file),
                    'width': int(frame_info.get('width', self.frame_width)),
                    'height': int(frame_info.get('height', self.frame_height)),
                    'pict_type': frame_info.get('pict_type', 'I'),
                    'complexity_estimate': os.path.getsize(frame_file) / 1000.0  # KB as complexity proxy
                }
            else:
                return self.analyze_frame_fallback(frame_file)
                
        except Exception:
            return self.analyze_frame_fallback(frame_file)
    
    def analyze_frame_fallback(self, frame_file: str) -> Dict:
        """Fallback frame analysis using just file properties"""
        return {
            'file_size': os.path.getsize(frame_file),
            'width': self.frame_width,
            'height': self.frame_height, 
            'pict_type': 'unknown',
            'complexity_estimate': os.path.getsize(frame_file) / 1000.0
        }
    
    def extract_visual_features(self, mp4_file: str) -> Dict:
        """Extract visual features from entire video"""
        
        # Create temporary directory for frames
        with tempfile.TemporaryDirectory() as temp_dir:
            
            # Extract frames
            frame_files = self.extract_frames_from_mp4(mp4_file, temp_dir)
            
            if not frame_files:
                raise Exception("No frames extracted from video")
            
            # Get video duration
            duration = self.get_video_duration(mp4_file)
            
            # Analyze each frame
            visual_features = {
                'metadata': {
                    'source_file': mp4_file,
                    'duration': duration,
                    'sample_rate': self.sample_rate,
                    'num_frames': len(frame_files),
                    'frame_width': self.frame_width,
                    'frame_height': self.frame_height
                },
                'frames': [],
                'timestamps': []
            }
            
            print(f"Analyzing {len(frame_files)} frames...")
            
            for i, frame_file in enumerate(frame_files):
                timestamp = i / self.sample_rate
                
                # Basic frame analysis
                frame_analysis = self.analyze_frame_basic(frame_file)
                
                # Calculate relative metrics
                frame_features = {
                    'timestamp': timestamp,
                    'complexity': frame_analysis['complexity_estimate'],
                    'file_size': frame_analysis['file_size'],
                    'width': frame_analysis['width'],
                    'height': frame_analysis['height']
                }
                
                visual_features['frames'].append(frame_features)
                visual_features['timestamps'].append(timestamp)
                
                if i % 100 == 0:
                    print(f"Processed {i+1}/{len(frame_files)} frames...")
            
            return visual_features
    
    def get_video_duration(self, mp4_file: str) -> float:
        """Get video duration using ffprobe"""
        cmd = [
            'ffprobe',
            '-v', 'quiet', 
            '-print_format', 'json',
            '-show_format',
            mp4_file
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            data = json.loads(result.stdout)
            return float(data['format']['duration'])
        except:
            return 0.0
    
    def create_visual_vectors(self, features: Dict) -> List[Dict]:
        """Create dense vectors from visual features"""
        
        vectors = []
        
        for frame in features['frames']:
            # Create simple visual vector
            dense_vector = [
                frame['complexity'],           # Visual complexity
                frame['file_size'] / 10000.0, # Normalized file size
                frame['timestamp']             # Temporal position
            ]
            
            vector = {
                'timestamp': frame['timestamp'],
                'features': {
                    'complexity': frame['complexity'],
                    'file_size': frame['file_size'],
                    'temporal_position': frame['timestamp']
                },
                'dense_vector': dense_vector
            }
            
            vectors.append(vector)
            
        return vectors
    
    def save_to_file(self, features: Dict, output_file: str):
        """Save visual features to file"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(features, f, indent=2)
            
        print(f"Visual features saved: {output_file}")

def main():
    """Extract visual features from the Google Meet MP4"""
    
    extractor = BasicVisualExtractor(sample_rate=0.5)  # 1 frame every 2 seconds
    
    # Path to original MP4
    mp4_file = "/home/jonclaude/Downloads/fbu-zwns-okp (2025-07-24 20_00 GMT-4).mp4"
    
    if Path(mp4_file).exists():
        print("🎬 Starting VectorVault Visual Extraction...")
        
        try:
            # Extract visual features  
            features = extractor.extract_visual_features(mp4_file)
            vectors = extractor.create_visual_vectors(features)
            
            print(f"\n📊 Visual Extraction Results:")
            print(f"Video duration: {features['metadata']['duration']:.1f} seconds")
            print(f"Visual vectors: {len(vectors)}")
            print(f"Vector dimensions: {len(vectors[0]['dense_vector'])}")
            print(f"Sample rate: {features['metadata']['sample_rate']} fps")
            
            # Save results
            output_file = "/home/jonclaude/Agents/Claude on Studio/VectorVault/projects/google_meet_analysis/visual_vectors.json"
            extractor.save_to_file({'features': features, 'vectors': vectors}, output_file)
            
            # Show sample
            if vectors:
                print(f"\n🔍 Sample vector at {vectors[0]['timestamp']:.1f}s:")
                for key, value in vectors[0]['features'].items():
                    print(f"  {key}: {value:.4f}")
                    
        except Exception as e:
            print(f"❌ Visual extraction failed: {e}")
            
    else:
        print(f"❌ MP4 file not found: {mp4_file}")

if __name__ == "__main__":
    main()