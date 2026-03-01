from app import create_app
from app.core.config import ENVIRONMENT, PORT

app = create_app(ENVIRONMENT)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=True)
