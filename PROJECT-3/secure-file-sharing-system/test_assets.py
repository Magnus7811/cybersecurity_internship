from flask import Flask, send_file
app = Flask(__name__)

@app.route('/test-image')
def test_image():
    return send_file('static/crypto-bg.jpg')

@app.route('/test-svg')
def test_svg():
    return send_file('static/lock-icon.svg'), 200, {'Content-Type': 'image/svg+xml'}

if __name__ == '__main__':
    app.run(port=5001)
