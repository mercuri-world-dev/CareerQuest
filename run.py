import os
from __init__ import create_app

app = create_app()

if os.environ.get('FLASK_ENV') == 'development' and __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)