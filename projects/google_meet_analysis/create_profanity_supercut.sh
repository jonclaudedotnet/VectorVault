#!/bin/bash
# Create profanity supercut from conversation

echo "🎬 Creating Profanity Supercut from 40-year friendship conversation"
echo "================================================================"

# Create clips directory
CLIPS_DIR="/home/jonclaude/Agents/Claude on Studio/VectorVault/projects/google_meet_analysis/profanity_clips"
mkdir -p "$CLIPS_DIR"

AUDIO="/home/jonclaude/Agents/Claude on Studio/Woodside-Animation/conversation_audio.wav"

# Extract the best profanity moments (with 3-second context each)
echo "Extracting clips..."

# The funniest ones based on context
ffmpeg -i "$AUDIO" -ss 57.56 -t 3.26 "$CLIPS_DIR/01_jesus_head_explode.wav" -y 2>/dev/null
ffmpeg -i "$AUDIO" -ss 221.70 -t 3.50 "$CLIPS_DIR/02_crazy_bad_vision.wav" -y 2>/dev/null
ffmpeg -i "$AUDIO" -ss 615.94 -t 3.12 "$CLIPS_DIR/03_god_meeting_tools.wav" -y 2>/dev/null
ffmpeg -i "$AUDIO" -ss 619.70 -t 3.10 "$CLIPS_DIR/04_shit_dont_hear.wav" -y 2>/dev/null
ffmpeg -i "$AUDIO" -ss 752.98 -t 3.18 "$CLIPS_DIR/05_fuck_china_number_one.wav" -y 2>/dev/null
ffmpeg -i "$AUDIO" -ss 1687.10 -t 3.38 "$CLIPS_DIR/06_stupid_sorry.wav" -y 2>/dev/null
ffmpeg -i "$AUDIO" -ss 1697.42 -t 3.32 "$CLIPS_DIR/07_stupid_were_all.wav" -y 2>/dev/null
ffmpeg -i "$AUDIO" -ss 2518.62 -t 3.60 "$CLIPS_DIR/08_shit_happening.wav" -y 2>/dev/null
ffmpeg -i "$AUDIO" -ss 3141.06 -t 3.30 "$CLIPS_DIR/09_shit_thats_good.wav" -y 2>/dev/null
ffmpeg -i "$AUDIO" -ss 3293.14 -t 3.26 "$CLIPS_DIR/10_god_something.wav" -y 2>/dev/null
ffmpeg -i "$AUDIO" -ss 3781.82 -t 3.46 "$CLIPS_DIR/11_fucking_og_push.wav" -y 2>/dev/null
ffmpeg -i "$AUDIO" -ss 3925.10 -t 3.70 "$CLIPS_DIR/12_fucking_crazy_maya.wav" -y 2>/dev/null

echo "Creating concatenation list..."

# Create concat file
cat > "$CLIPS_DIR/concat_list.txt" << EOF
file '01_jesus_head_explode.wav'
file '02_crazy_bad_vision.wav'
file '03_god_meeting_tools.wav'
file '04_shit_dont_hear.wav'
file '05_fuck_china_number_one.wav'
file '06_stupid_sorry.wav'
file '07_stupid_were_all.wav'
file '08_shit_happening.wav'
file '09_shit_thats_good.wav'
file '10_god_something.wav'
file '11_fucking_og_push.wav'
file '12_fucking_crazy_maya.wav'
EOF

echo "Creating supercut..."

# Create the supercut
cd "$CLIPS_DIR"
ffmpeg -f concat -safe 0 -i concat_list.txt -c copy ../profanity_supercut.wav -y 2>/dev/null

echo "✅ Supercut created: profanity_supercut.wav"
echo ""
echo "📊 Supercut contains:"
echo "  - 12 choice profanity moments"
echo "  - ~40 seconds of concentrated friendship energy"
echo "  - Context: Jesus, China #1, OG Push, and philosophical stupidity"
echo ""
echo "😂 Perfect for understanding the emotional texture of 40-year friendships!"