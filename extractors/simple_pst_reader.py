#!/usr/bin/env python3
"""
Simple PST Reader - Pure Python approach
When readpst isn't available, try Python libraries
"""

import os
import json
import struct
from pathlib import Path
from datetime import datetime

class SimplePSTReader:
    def __init__(self, pst_path):
        self.pst_path = Path(pst_path)
        self.file_size = self.pst_path.stat().st_size if self.pst_path.exists() else 0
        
    def analyze_pst_structure(self):
        """Basic PST file analysis without full parsing"""
        
        if not self.pst_path.exists():
            return None
            
        analysis = {
            "file_path": str(self.pst_path),
            "file_size_mb": round(self.file_size / (1024 * 1024), 2),
            "analysis_method": "Header inspection",
            "recommendations": []
        }
        
        # Try to read PST header
        try:
            with open(self.pst_path, 'rb') as f:
                header = f.read(512)  # Read first 512 bytes
                
                # Check PST signature
                if header[:4] == b'!BDN':
                    analysis["format"] = "PST (Personal Storage Table)"
                    analysis["recommendations"].append("Use readpst or libpst for full extraction")
                else:
                    analysis["format"] = "Unknown or corrupted PST"
                    analysis["recommendations"].append("File may be corrupted or not a PST file")
                    
        except Exception as e:
            analysis["error"] = str(e)
            analysis["recommendations"].append("File access error - check permissions")
        
        return analysis
    
    def create_extraction_commands(self, pst_files):
        """Generate extraction commands for when tools become available"""
        
        commands = []
        
        for pst_file in pst_files:
            pst_path = pst_file if isinstance(pst_file, str) else pst_file.get('path', '')
            output_name = Path(pst_path).stem
            
            # readpst commands
            commands.append({
                "tool": "readpst",
                "install": "sudo apt-get install readpst",
                "command": f'readpst -M -o ./raw/{output_name}/ "{pst_path}"',
                "description": "Extract to mbox format for email parsing"
            })
            
            # Alternative: libpst-python
            commands.append({
                "tool": "python-libpst",
                "install": "pip3 install python-libpst",
                "command": f'python3 -c "import pypff; process_pst(\'{pst_path}\')"',
                "description": "Pure Python PST processing"
            })
        
        return commands
    
    def estimate_content_value(self, file_size_mb):
        """Estimate narrative value based on file size"""
        
        if file_size_mb < 50:
            return {
                "estimated_emails": "< 1,000",
                "narrative_value": "Low - likely recent/limited correspondence",
                "processing_priority": 3
            }
        elif file_size_mb < 500:
            return {
                "estimated_emails": "1,000 - 10,000",
                "narrative_value": "Medium - substantial email history", 
                "processing_priority": 2
            }
        else:
            return {
                "estimated_emails": "10,000+",
                "narrative_value": "High - extensive email archive with likely story content",
                "processing_priority": 1
            }

def main():
    """Analyze available PST files and create extraction plan"""
    
    print("📧 SIMPLE PST ANALYSIS - VectorVault Email Archaeology")
    print("=" * 65)
    
    # PST files found on system
    pst_files = [
        "/media/nvme-drive1/Users/conta/Documents/Outlook Files/Outlook Data File - archive.pst",
        "/media/nvme-drive1/Users/conta/Desktop/backup2005.pst"
    ]
    
    reader = SimplePSTReader("")
    analyses = []
    
    print("🔍 ANALYZING PST FILES:\n")
    
    for pst_path in pst_files:
        reader.pst_path = Path(pst_path)
        reader.file_size = reader.pst_path.stat().st_size if reader.pst_path.exists() else 0
        
        analysis = reader.analyze_pst_structure()
        if analysis:
            analyses.append(analysis)
            
            # Add content estimation
            size_mb = analysis["file_size_mb"]
            content_est = reader.estimate_content_value(size_mb)
            analysis.update(content_est)
            
            print(f"📁 {Path(pst_path).name}")
            print(f"   Size: {size_mb} MB")
            print(f"   Estimated emails: {content_est['estimated_emails']}")
            print(f"   Narrative value: {content_est['narrative_value']}")
            print(f"   Priority: {content_est['processing_priority']}")
            print()
    
    # Generate extraction commands
    commands = reader.create_extraction_commands(pst_files)
    
    print("🔧 EXTRACTION METHODS:")
    print("\n1. Install readpst (recommended):")
    print("   sudo apt-get install readpst")
    print("\n2. Extract archives:")
    for i, cmd in enumerate(commands[:2], 1):  # Show first 2 commands
        print(f"   {cmd['command']}")
    
    print("\n3. Process with VectorVault:")
    print("   python3 extractors/pst_extractor.py")
    
    # Save analysis
    output_file = "/home/jonclaude/Agents/Claude on Studio/VectorVault/projects/email_analysis/pst_analysis.json"
    
    analysis_summary = {
        "analysis_date": datetime.now().isoformat(),
        "total_files": len(analyses),
        "total_size_mb": sum(a["file_size_mb"] for a in analyses),
        "extraction_status": "Pending - readpst installation required",
        "files": analyses,
        "extraction_commands": commands,
        "next_steps": [
            "Install readpst: sudo apt-get install readpst",
            "Extract PST files to mbox format",
            "Run importance scoring and thread analysis",
            "Integrate with VectorVault nexus for cross-modal correlation"
        ]
    }
    
    with open(output_file, 'w') as f:
        json.dump(analysis_summary, f, indent=2)
    
    print(f"\n💾 Analysis saved to: {output_file}")
    print(f"\n📊 SUMMARY:")
    print(f"   Total archive size: {analysis_summary['total_size_mb']} MB")
    print(f"   Estimated narrative value: High (2005 backup + recent archive)")
    print(f"   Ready for extraction once readpst is installed")
    
    return analysis_summary

if __name__ == "__main__":
    main()