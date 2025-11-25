from flask import Flask, request, Response, stream_with_context
import requests

app = Flask(__name__)

# The detailed style prompt (hardcoded as the default style)
SYSTEM_PROMPT_STYLE = """Voice Affect: Energetic and animated; dynamic with variations in pitch and tone.

Tone: Excited and enthusiastic, conveying an upbeat and thrilling atmosphere.

Pacing: Rapid delivery when describing the game or the key moments (e.g., "an overtime thriller," "pull off an unbelievable win") to convey the intensity and build excitement.

Slightly slower during dramatic pauses to let key points sink in.

Emotion: Intensely focused, and excited. Giving off positive energy.

Personality: Relatable and engaging.

Pauses: Short, purposeful pauses after key moments in the game."""

@app.route('/', methods=['GET'])
def index():
    """Health check route."""
    return (
        "<h1>OpenAI FM API Wrapper is Running</h1>"
        "<p>Use the endpoint: <a href='/api/generate?prompt=Test'>/api/generate?prompt=Test</a></p>"
    )

@app.route('/api/generate', methods=['GET'])
def generate_audio_endpoint():
    """
    Endpoint to generate audio.
    Usage: GET /api/generate?prompt=Your%20Text%20Here
    """
    # Get the text input from the URL query parameter 'prompt'
    user_input = request.args.get('prompt')

    if not user_input:
        return "Error: Missing 'prompt' parameter. Usage: /api/generate?prompt=text", 400

    url = "https://www.openai.fm/api/generate"

    # Headers to mimic a real browser request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
        "Origin": "https://www.openai.fm",
        "Referer": "https://www.openai.fm/",
    }

    # Construct the payload
    payload = {
        "input": user_input,
        "prompt": SYSTEM_PROMPT_STYLE,
        "voice": "alloy",
        "vibe": "null"
    }

    print(f"Endpoint received request for text: '{user_input}'")

    try:
        # Make the POST request to the upstream API
        upstream_response = requests.post(url, headers=headers, data=payload, stream=True)
        
        if upstream_response.status_code == 200:
            # Stream the audio back to the browser
            return Response(
                stream_with_context(upstream_response.iter_content(chunk_size=1024)),
                content_type=upstream_response.headers.get('Content-Type', 'audio/wav')
            )
        else:
            return f"Upstream API Error: {upstream_response.status_code} - {upstream_response.text}", 502

    except Exception as e:
        return f"Server Error: {e}", 500

# Vercel requires the app to be exposed, but for local testing:
if __name__ == "__main__":
    app.run(debug=True, port=5000)
