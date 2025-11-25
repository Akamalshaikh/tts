from flask import Flask, request, Response, jsonify
import requests
import json

app = Flask(__name__)

def generate_voice_audio(input_text, voice="alloy", vibe="null"):
    """
    Sends a request to the openai.fm API to generate audio.
    Returns the audio bytes if successful, None otherwise.
    """
    url = "https://www.openai.fm/api/generate"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
        "Origin": "https://www.openai.fm",
        "Referer": "https://www.openai.fm/",
    }

    system_prompt = """Voice Affect: Energetic and animated; dynamic with variations in pitch and tone.

Tone: Excited and enthusiastic, conveying an upbeat and thrilling atmosphere.

Pacing: Rapid delivery when describing the game or the key moments (e.g., "an overtime thriller," "pull off an unbelievable win") to convey the intensity and build excitement.

Slightly slower during dramatic pauses to let key points sink in.

Emotion: Intensely focused, and excited. Giving off positive energy.

Personality: Relatable and engaging.

Pauses: Short, purposeful pauses after key moments in the game."""

    payload = {
        "input": input_text,
        "prompt": system_prompt,
        "voice": voice,
        "vibe": vibe
    }

    try:
        response = requests.post(url, headers=headers, data=payload, timeout=30)
        
        if response.status_code == 200:
            return response.content
        else:
            print(f"Error: Received status code {response.status_code}")
            return None
            
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


@app.route('/')
def home():
    """Home page with API documentation"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Voice Generation API</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            h1 { color: #333; }
            code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }
            .example { background: #e8f5e9; padding: 15px; border-radius: 5px; margin: 10px 0; }
            a { color: #2196F3; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>🎙️ Voice Generation API</h1>
        <h2>Endpoint:</h2>
        <p><strong>GET /api/generate</strong></p>
        
        <h3>Parameters:</h3>
        <ul>
            <li><code>prompt</code> (required) - Text to convert to speech</li>
            <li><code>voice</code> (optional) - Voice type (default: alloy)</li>
            <li><code>vibe</code> (optional) - Vibe setting (default: null)</li>
        </ul>
        
        <h3>Example Usage:</h3>
        <div class="example">
            <p><a href="/api/generate?prompt=hi solox" target="_blank">/api/generate?prompt=hi solox</a></p>
            <p><a href="/api/generate?prompt=Hello world, this is amazing!" target="_blank">/api/generate?prompt=Hello world, this is amazing!</a></p>
        </div>
        
        <h3>How to use:</h3>
        <p>Simply add your text after <code>?prompt=</code> and the audio will download automatically!</p>
    </body>
    </html>
    """
    return html


@app.route('/api/generate', methods=['GET'])
def generate():
    """
    Generate voice audio from text prompt
    Usage: /api/generate?prompt=your+text+here&voice=alloy&vibe=null
    """
    # Get parameters from query string
    prompt = request.args.get('prompt')
    voice = request.args.get('voice', 'alloy')
    vibe = request.args.get('vibe', 'null')
    
    # Validate prompt
    if not prompt:
        return jsonify({
            "error": "Missing 'prompt' parameter",
            "usage": "/api/generate?prompt=your+text+here"
        }), 400
    
    # Generate audio
    print(f"Generating audio for: '{prompt}'")
    audio_bytes = generate_voice_audio(prompt, voice, vibe)
    
    if audio_bytes:
        # Return the audio file directly
        return Response(
            audio_bytes,
            mimetype='audio/wav',
            headers={
                'Content-Disposition': f'attachment; filename="voice_audio.wav"',
                'Content-Type': 'audio/wav'
            }
        )
    else:
        return jsonify({
            "error": "Failed to generate audio"
        }), 500


# For Vercel serverless function
def handler(request):
    with app.request_context(request.environ):
        try:
            return app.full_dispatch_request()
        except Exception as e:
            return jsonify({"error": str(e)}), 500