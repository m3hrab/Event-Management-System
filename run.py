import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables
load_dotenv()

# Create Flask app with environment-specific config
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    # Get configuration from environment
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')  # Render requires 0.0.0.0
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # For production deployment (like Render), debug should be False
    if config_name == 'production':
        debug = False
    
    app.run(debug=debug, host=host, port=port) 