#!/bin/bash
# VectorVault Email Extraction - Install and Process

echo "📧 VECTORVAULT EMAIL EXTRACTION PIPELINE"
echo "========================================="

# Install pst-utils
echo "🔧 Installing pst-utils..."
echo "Please run: sudo apt-get install pst-utils -y"
echo "Press Enter when installation is complete..."
read -p ""

# Verify installation
if command -v readpst &> /dev/null; then
    echo "✅ readpst installed successfully"
    readpst --help | head -5
else
    echo "❌ Installation failed"
    exit 1
fi

# Create directories
echo "📁 Setting up directories..."
mkdir -p "/home/jonclaude/Agents/Claude on Studio/VectorVault/projects/email_analysis/raw/archive"
mkdir -p "/home/jonclaude/Agents/Claude on Studio/VectorVault/projects/email_analysis/raw/backup2005"

# Extract main archive (2.1GB)
echo "📧 Extracting main archive (2.1GB)..."
cd "/home/jonclaude/Agents/Claude on Studio/VectorVault/projects/email_analysis/raw/archive"
readpst -M -o . "/media/nvme-drive1/Users/conta/Documents/Outlook Files/Outlook Data File - archive.pst"

if [ $? -eq 0 ]; then
    echo "✅ Main archive extraction complete"
    echo "📊 Files created:"
    ls -lh .
else
    echo "❌ Main archive extraction failed"
fi

# Extract 2005 backup (613MB)
echo "📧 Extracting 2005 backup (613MB)..."
cd "/home/jonclaude/Agents/Claude on Studio/VectorVault/projects/email_analysis/raw/backup2005"
readpst -M -o . "/media/nvme-drive1/Users/conta/Desktop/backup2005.pst"

if [ $? -eq 0 ]; then
    echo "✅ 2005 backup extraction complete"
    echo "📊 Files created:"
    ls -lh .
else
    echo "❌ 2005 backup extraction failed"
fi

# Run analysis
echo "🧠 Running importance analysis..."
cd "/home/jonclaude/Agents/Claude on Studio/VectorVault"
python3 extractors/pst_extractor.py

echo "✨ Email extraction pipeline complete!"
echo "📁 Check /projects/email_analysis/raw/ for extracted files"