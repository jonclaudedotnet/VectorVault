# VectorVault
**Multimodal Analysis Framework for Personal Narrative Archaeology**

> *"Extract the mathematical DNA of human conversations"*

## 🎯 Purpose
VectorVault transforms personal life data into discoverable stories through AI-powered analysis. Built for creators who want to extract narratives from lived experience without traditional writing.

## 📊 Current Analysis Scope
- **Conversation Audio:** 1.7-hour Google Meet conversation (13,461 words)
- **Personal Journal:** 82 Apple Journal entries (6,707 words, 2024-2025)
- **Total Vectors:** 127,221 searchable data points
- **Cross-Modal Correlations:** Technology, creativity, relationships, work themes

## 🏗️ Architecture

```
VectorVault/
├── extractors/          # Modular feature extraction
│   ├── audio_basic.py      # RMS energy, spectral analysis
│   ├── visual_basic.py     # Frame complexity scoring
│   ├── whisper_direct.py   # Speech-to-text with timestamps
│   └── journal_extractor.py # Apple Journal HTML/theme parsing
├── storage/            # Vector database management  
│   └── simple_vector_db.py # SQLite-based similarity search
├── analysis/           # Pattern discovery tools
│   ├── profanity_supercut.py # Humor extraction & audio clips
│   └── journal_insights_report.md # AI-enabled creative concepts
├── projects/           # Specific use cases
│   └── google_meet_analysis/ # Maya conversation archaeology
└── nexus_correlator.py # Cross-modal pattern discovery
```

## 🧠 Core Innovations

### Conversation Archaeology
- **Word-level timestamps** for precise temporal mapping
- **Audio-visual correlation** at 10Hz sampling rate
- **Humor analysis** with context-aware audio extraction
- **Mathematical representation** of friendship dynamics

### Journal Integration
- **Theme extraction** from Apple Journal HTML exports
- **Voice-to-text pattern recognition** in personal entries
- **Temporal narrative evolution** tracking
- **Cross-modal correlation** between private thoughts and conversations

### AI-Enabled Creative Concepts Discovery
Analysis revealed multiple breakthrough ideas:
- **VR Museum Documentation** with "shoot now, AI-enhance later" approach
- **"Mr. AI" Broadcast Co-host** with wake phrase integration
- **Historical Preservation** using AI narrative extraction
- **Real-time Translation Systems** for global communication

## 📈 Key Metrics

### Personal Narrative Database
- **20,168 total words** analyzed across modalities
- **6.05 correlation score** for technology themes
- **20.7% reflection ratio** in journal entries
- **40-year friendship** conversation pattern analysis

### Technical Capabilities
- **127,221 vectors** in searchable database
- **0.1-second precision** audio analysis
- **0.5fps visual sampling** with complexity scoring
- **Cross-temporal correlation** discovery

## 🎪 Sample Outputs

### Humor Supercut
```bash
# 40-second profanity supercut from 40-year friendship
ffmpeg -f concat -safe 0 -i concat_list.txt profanity_supercut.wav
# Contains: Jesus, China #1, OG Push, philosophical stupidity
```

### Theme Correlations
```json
{
  "technology": {"correlation_score": 6.05, "journal_entries": 34},
  "creativity": {"correlation_score": 2.89, "journal_entries": 13},
  "work": {"correlation_score": 2.67, "journal_entries": 16}
}
```

## 🚀 Usage

### Basic Analysis Pipeline
```python
# Extract conversation features
extractor = AudioBasicExtractor()
audio_vectors = extractor.process_conversation(audio_file)

# Parse personal journals
journal_extractor = JournalExtractor(journal_path)
journal_vectors = journal_extractor.create_semantic_vectors()

# Discover cross-modal patterns
correlator = NexusCorrelator()
insights = correlator.generate_narrative_insights()
```

### Query Examples
```python
# Find moments of high emotional intensity
db.similarity_search("emotional breakthrough", modality="audio")

# Discover recurring themes
db.find_patterns("technology obsession", temporal_range="2024-2025")

# Extract story fragments
db.correlate_themes(["creativity", "relationships", "technology"])
```

## 🎬 Real-World Applications

### Content Creation
- **Podcast highlight extraction** from long-form conversations
- **Story discovery** in personal archives
- **Theme tracking** across time periods
- **Humor identification** for comedy content

### Personal Intelligence
- **Conversation pattern analysis** for relationship insights
- **Creative idea mining** from journals and notes
- **Temporal theme evolution** tracking
- **Cross-modal correlation** discovery

### Professional Use Cases
- **Interview analysis** for documentary production
- **Customer conversation** pattern recognition
- **Creative brief extraction** from brainstorm sessions
- **Meeting archaeology** for project retrospectives

## 🔬 Technical Details

### Audio Processing
- **Sample rate:** 16kHz with 0.1s window analysis
- **Features:** RMS energy, peak amplitude, zero-crossing rate
- **No dependencies:** Pure Python math implementation
- **GPU acceleration:** Optional Whisper fp16 mode

### Visual Analysis
- **Sampling rate:** 0.5fps (every 2 seconds)
- **Metrics:** Frame complexity via file size analysis
- **Format support:** MP4, AVI, MOV extraction
- **Lightweight:** No computer vision dependencies

### Vector Storage
- **Database:** SQLite with JSON vector columns
- **Similarity:** Cosine similarity with magnitude normalization
- **Scalability:** Handles 100k+ vectors efficiently
- **Query types:** Temporal, thematic, cross-modal searches

## 🎪 Philosophy

VectorVault embodies a **Wim Wenders approach** to personal data - teaching computers to see the emotional texture of human experience. Rather than replacing human creativity, it amplifies pattern recognition to discover stories hidden in the data streams of daily life.

**Core Principle:** Every conversation, journal entry, and moment contains mathematical signatures of human experience that can be extracted, correlated, and transformed into discoverable narratives.

## 📝 Status

**Current:** Fully operational multimodal analysis system
**Next:** Pattern discovery UI and narrative synthesis tools
**Vision:** Complete personal archaeology platform for story extraction

---
*"I'm trying to extract my stories from the life I'm currently living. Because I'm not a writer, I'm finding interesting ways to try to tell my stories and have a legacy that way."*

**Generated by VectorVault Personal Narrative Archaeology System**