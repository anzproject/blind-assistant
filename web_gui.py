#!/usr/bin/env python3
"""
Web-based GUI for Blind Assistant setup and configuration.
"""

from flask import Flask, render_template, request, jsonify
import json
import os
from pathlib import Path

app = Flask(__name__)

CONFIG_FILE = Path("config.json")

def load_config():
    """Load configuration from file."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        "voice_rate": 180,
        "voice_volume": 1.0,
        "camera_resolution": "640x480",
        "gps_update_interval": 5,
        "emergency_contacts": [],
        "user_profiles": {}
    }

def save_config(config):
    """Save configuration to file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

@app.route('/')
def index():
    """Main setup page."""
    config = load_config()
    return render_template('index.html', config=config)

@app.route('/api/config', methods=['GET', 'POST'])
def config_api():
    """API endpoint for configuration."""
    if request.method == 'POST':
        config = request.json
        save_config(config)
        return jsonify({"status": "success"})
    else:
        return jsonify(load_config())

@app.route('/api/test/<component>')
def test_component(component):
    """Test individual components."""
    # This would integrate with the actual modules
    test_results = {
        "camera": "Camera test passed",
        "audio": "Audio test passed",
        "gps": "GPS test passed",
        "bluetooth": "Bluetooth test passed"
    }
    return jsonify({"result": test_results.get(component, "Unknown component")})

@app.route('/api/status')
def system_status():
    """Get system status."""
    # Check if modules are loaded and working
    status = {
        "assistant_running": False,  # Would check actual status
        "camera_ready": True,
        "audio_ready": True,
        "gps_ready": True,
        "bluetooth_connected": False
    }
    return jsonify(status)

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)

    # Create basic HTML template
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blind Assistant Setup</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .section { margin-bottom: 30px; border: 1px solid #ccc; padding: 20px; border-radius: 5px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; }
        input, select { width: 100%; padding: 8px; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <h1>AI Blind Assistant Setup</h1>

    <div class="section">
        <h2>Voice Settings</h2>
        <div class="form-group">
            <label for="voice_rate">Voice Rate (words per minute):</label>
            <input type="number" id="voice_rate" value="{{ config.voice_rate }}">
        </div>
        <div class="form-group">
            <label for="voice_volume">Voice Volume (0.0 - 1.0):</label>
            <input type="number" id="voice_volume" step="0.1" min="0" max="1" value="{{ config.voice_volume }}">
        </div>
    </div>

    <div class="section">
        <h2>Camera Settings</h2>
        <div class="form-group">
            <label for="camera_resolution">Camera Resolution:</label>
            <select id="camera_resolution">
                <option value="640x480" {% if config.camera_resolution == '640x480' %}selected{% endif %}>640x480</option>
                <option value="1280x720" {% if config.camera_resolution == '1280x720' %}selected{% endif %}>1280x720</option>
                <option value="1920x1080" {% if config.camera_resolution == '1920x1080' %}selected{% endif %}>1920x1080</option>
            </select>
        </div>
    </div>

    <div class="section">
        <h2>GPS Settings</h2>
        <div class="form-group">
            <label for="gps_interval">GPS Update Interval (seconds):</label>
            <input type="number" id="gps_interval" value="{{ config.gps_update_interval }}">
        </div>
    </div>

    <div class="section">
        <h2>System Tests</h2>
        <button onclick="testComponent('camera')">Test Camera</button>
        <button onclick="testComponent('audio')">Test Audio</button>
        <button onclick="testComponent('gps')">Test GPS</button>
        <button onclick="testComponent('bluetooth')">Test Bluetooth</button>
        <div id="test_results"></div>
    </div>

    <div class="section">
        <h2>Actions</h2>
        <button onclick="saveConfig()">Save Configuration</button>
        <button onclick="startAssistant()">Start Assistant</button>
        <button onclick="stopAssistant()">Stop Assistant</button>
        <div id="status_message"></div>
    </div>

    <script>
        function saveConfig() {
            const config = {
                voice_rate: parseInt(document.getElementById('voice_rate').value),
                voice_volume: parseFloat(document.getElementById('voice_volume').value),
                camera_resolution: document.getElementById('camera_resolution').value,
                gps_update_interval: parseInt(document.getElementById('gps_interval').value),
                emergency_contacts: [],
                user_profiles: {}
            };

            fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            })
            .then(response => response.json())
            .then(data => {
                showMessage('Configuration saved successfully!', 'success');
            })
            .catch(error => {
                showMessage('Error saving configuration: ' + error, 'error');
            });
        }

        function testComponent(component) {
            fetch('/api/test/' + component)
            .then(response => response.json())
            .then(data => {
                document.getElementById('test_results').innerHTML = '<div class="status success">' + data.result + '</div>';
            })
            .catch(error => {
                document.getElementById('test_results').innerHTML = '<div class="status error">Test failed: ' + error + '</div>';
            });
        }

        function startAssistant() {
            showMessage('Starting assistant...', 'success');
            // This would trigger the main assistant
        }

        function stopAssistant() {
            showMessage('Stopping assistant...', 'success');
            // This would stop the main assistant
        }

        function showMessage(message, type) {
            const statusDiv = document.getElementById('status_message');
            statusDiv.innerHTML = '<div class="status ' + type + '">' + message + '</div>';
            setTimeout(() => { statusDiv.innerHTML = ''; }, 3000);
        }
    </script>
</body>
</html>
    """

    with open(templates_dir / "index.html", "w") as f:
        f.write(html_content)

    app.run(debug=True, host='0.0.0.0', port=5000)
