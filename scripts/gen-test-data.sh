#!/bin/bash
# Generate test fixtures for CLI testing
# These files are not committed to git - run this script to create them locally

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIXTURES_DIR="$SCRIPT_DIR/fixtures"

mkdir -p "$FIXTURES_DIR"

echo "Generating test fixtures in $FIXTURES_DIR..."

# Images (512x512 with plasma patterns for realistic image data)
echo "Creating images..."
magick -size 512x512 plasma:red-yellow -depth 8 -quality 85 "$FIXTURES_DIR/dummy_image.jpg"
magick -size 512x512 plasma:green-blue "$FIXTURES_DIR/dummy_image.png"
magick -size 512x512 plasma:blue-purple "$FIXTURES_DIR/dummy_image.webp"

# Videos (10 seconds)
echo "Creating videos..."
ffmpeg -y -f lavfi -i color=c=red:s=320x240:d=10 -c:v libx264 -pix_fmt yuv420p "$FIXTURES_DIR/dummy_video.mp4" 2>/dev/null
ffmpeg -y -f lavfi -i color=c=blue:s=320x240:d=10 -c:v libx264 -pix_fmt yuv420p "$FIXTURES_DIR/dummy_video.mov" 2>/dev/null

# Voice audio (30 seconds, pink noise)
echo "Creating voice audio..."
ffmpeg -y -f lavfi -i "anoisesrc=d=30:c=pink:r=44100:a=0.5" -ac 2 -ar 44100 -b:a 192k "$FIXTURES_DIR/dummy_voice.mp3" 2>/dev/null
ffmpeg -y -f lavfi -i "anoisesrc=d=30:c=pink:r=44100:a=0.5" -ac 2 -ar 44100 "$FIXTURES_DIR/dummy_voice.wav" 2>/dev/null

# Music audio (30 seconds, modulated tone)
echo "Creating music audio..."
ffmpeg -y -f lavfi -i "aevalsrc=sin(440*2*PI*t)*sin(2*PI*t/5):d=30" -ac 2 -ar 44100 -b:a 192k "$FIXTURES_DIR/dummy_music.mp3" 2>/dev/null
ffmpeg -y -f lavfi -i "aevalsrc=sin(440*2*PI*t)*sin(2*PI*t/5):d=30" -ac 2 -ar 44100 "$FIXTURES_DIR/dummy_music.flac" 2>/dev/null

# Text (500+ words)
echo "Creating text file..."
cat > "$FIXTURES_DIR/dummy_text.txt" << 'EOF'
The rapid advancement of artificial intelligence has fundamentally transformed how we interact with technology and process information. Machine learning algorithms now power everything from recommendation systems on streaming platforms to sophisticated medical diagnostic tools. These systems analyze vast amounts of data to identify patterns that would be impossible for humans to detect manually. The implications of this technology extend far beyond simple automation, touching nearly every aspect of modern life.

Natural language processing represents one of the most significant breakthroughs in recent AI development. These systems can now understand context, sentiment, and nuance in human communication with remarkable accuracy. Chatbots and virtual assistants have become increasingly sophisticated, capable of handling complex queries and providing helpful responses. The technology continues to improve as researchers develop new architectures and training methodologies.

Computer vision has similarly advanced at an impressive pace. Image recognition systems can now identify objects, faces, and scenes with superhuman accuracy in many contexts. Self-driving vehicles rely heavily on these capabilities to navigate safely through complex environments. Medical imaging analysis benefits enormously from AI systems that can detect anomalies that might escape human observation.

The ethical considerations surrounding artificial intelligence have become increasingly important as these systems become more powerful and widespread. Questions about bias in training data, algorithmic fairness, and the potential for misuse demand careful attention from developers and policymakers alike. Ensuring that AI systems treat all users equitably requires ongoing vigilance and thoughtful design choices.

Privacy concerns also feature prominently in discussions about AI technology. These systems often require access to large amounts of personal data to function effectively. Balancing the benefits of personalization with the need to protect individual privacy represents a significant challenge. Regulatory frameworks continue to evolve as governments attempt to address these complex issues.

The economic impact of artificial intelligence extends across multiple sectors. Automation has the potential to increase productivity dramatically while also displacing certain types of jobs. Workers may need to develop new skills to remain competitive in an AI-enhanced economy. Educational institutions and employers must adapt to prepare people for this changing landscape.

Research in artificial intelligence continues to push the boundaries of what machines can accomplish. Large language models demonstrate increasingly impressive capabilities in generating coherent text, solving complex problems, and engaging in creative tasks. The pace of progress has surprised even many experts in the field.

The future of AI holds both tremendous promise and significant uncertainty. Continued investment in research and development will likely yield further breakthroughs in capabilities. However, ensuring that these powerful technologies benefit humanity broadly will require careful stewardship and thoughtful governance.

Collaboration between technologists, policymakers, and civil society will be essential for navigating the challenges ahead. Open dialogue about the goals and values that should guide AI development can help build consensus around responsible approaches. The decisions made today will shape the trajectory of this transformative technology for decades to come.

As AI systems become more integrated into daily life, public understanding of these technologies becomes increasingly important. Education initiatives can help people develop the knowledge needed to engage critically with AI-powered tools and services. An informed citizenry is better equipped to participate in discussions about how these technologies should be governed.

The intersection of artificial intelligence with other emerging technologies creates additional opportunities and challenges. Quantum computing may eventually enable AI systems that far exceed current capabilities. Biotechnology applications of AI could revolutionize healthcare and agriculture. These convergences demand attention from researchers and policymakers alike.
EOF

echo "Done! Test fixtures created in $FIXTURES_DIR"
ls -lah "$FIXTURES_DIR"
