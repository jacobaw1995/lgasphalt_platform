from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'lg-asphalt-secret-key'  # Temporary for testing; will use .env later

@app.route('/')
def home():
    return 'Welcome to LG Asphalt Project Management Platform!'

if __name__ == '__main__':
    app.run(debug=True)