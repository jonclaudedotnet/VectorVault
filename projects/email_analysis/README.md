# Email Analysis Project
**VectorVault PST Email Narrative Archaeology**

## Overview
Process years of email archives to extract personal narratives, relationship evolution, and life story threads for integration with the VectorVault nexus.

## Data Sources
```
Personal Email Archives:
├── archive.pst (2.1GB)     # Recent/current email history
└── backup2005.pst (613MB)  # Historical archive (20+ years old)

Total: 2.7GB raw email data
Expected: ~100-500MB narrative-worthy content
```

## Extraction Pipeline

### Step 1: PST to mbox Conversion
```bash
# Extract PST files to searchable mbox format
readpst -M -o /path/to/output archive.pst
```

### Step 2: Email Parsing & Importance Scoring
**High Value (Keep):**
- Personal correspondence (family, friends)
- Creative project collaborations  
- Life transitions (job changes, moves, health)
- Long conversation threads (3+ exchanges)
- Relationship evolution patterns

**Low Value (Discard):**
- Automated messages/receipts
- Newsletters/marketing
- Spam/promotional content
- Short transactional emails

**Scoring Algorithm:**
```python
score = 0
score += 10 for personal_indicators (family, friends, personal)
score += 8  for creative_indicators (projects, video, creative)
score += 12 for life_events (moving, health, career)
score -= 5  for spam_indicators (unsubscribe, promotion)
score += 5  for thread_length > 3 emails
score += 3  for content_length > 500 chars
```

### Step 3: Thread Analysis
- **Conversation Threading:** Group related emails by subject/participants
- **Relationship Mapping:** Track correspondence frequency over time
- **Life Transition Detection:** Identify major life changes in email content
- **Creative Project Tracking:** Follow project collaborations across time

### Step 4: Vector Integration
- **Temporal Alignment:** Match email dates with journal entries
- **Theme Correlation:** Cross-reference email themes with journal/conversation
- **Narrative Synthesis:** Create searchable vector representations

## Processing Workflow

### Phase 1: Raw Extraction
```bash
cd /path/to/VectorVault
python3 extractors/pst_extractor.py
```

### Phase 2: Analysis & Filtering
- Parse extracted mbox files
- Apply importance scoring
- Extract conversation threads
- Identify narrative patterns

### Phase 3: VectorVault Integration
- Create semantic vectors from important emails
- Cross-correlate with existing journal/conversation data
- Generate unified personal narrative database

## Expected Outputs

### Quantitative Results
- **Email Count:** ~thousands of emails → ~hundreds of important emails
- **Thread Analysis:** Significant conversation chains
- **Relationship Metrics:** Correspondence frequency analysis
- **Temporal Patterns:** Life event timeline reconstruction

### Narrative Discoveries
- **Life Transitions:** Job changes, moves, relationship evolution
- **Creative Projects:** Collaboration histories and project evolution  
- **Relationship Arcs:** How friendships/partnerships developed over time
- **Historical Context:** Pre-smartphone communication patterns (2005 data)

### Cross-Modal Correlations
- **Email ↔ Journal:** Private thoughts vs. external communication
- **Email ↔ Conversation:** Written vs. spoken relationship dynamics
- **Temporal Evolution:** Theme progression across all data sources

## Technical Implementation

### File Structure
```
projects/email_analysis/
├── raw/                    # Extracted mbox files
├── processed/              # Filtered important emails
├── threads/                # Conversation thread analysis
├── vectors/                # Email vector representations
├── reports/                # Analysis summaries
└── correlations/           # Cross-modal pattern discovery
```

### Integration Points
- **SQLite Database:** All email vectors added to main VectorVault DB
- **Nexus Correlator:** Email data added to cross-modal analysis
- **Timeline Alignment:** Email dates correlated with journal entries

## Privacy & Ethics
- **Personal Data Only:** Processing user's own email archives
- **Narrative Focus:** Extracting life stories, not sensitive information
- **Selective Retention:** Keeping story-worthy content, discarding digital noise
- **Local Processing:** All analysis happens on local machine

---
*Email Narrative Archaeology - Discovering stories hidden in digital correspondence*

**Status:** In Progress
**Next Phase:** PST extraction and importance scoring