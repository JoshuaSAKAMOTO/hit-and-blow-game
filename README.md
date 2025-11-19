# Hit & Blow Game

A classic number guessing game built with Flask.

## Game Rules

Try to guess a 3-digit number with unique digits chosen by the computer.

- **Hit**: The digit and position are correct
- **Blow**: The digit is correct but in the wrong position

Try to guess the number in 10 attempts or less!

## Local Development

### Requirements

- Python 3.10+

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Flask development server:
```bash
python app.py
```

3. Open your browser and visit:
```
http://localhost:8000
```

### Legacy CGI Version

The `ht01.py`, `ht02.py`, and `server.py` files are from the original CGI-based implementation. You can run the legacy version with:

```bash
python server.py
```

## Deployment

This application is configured for deployment on Render.com.

### Deploy to Render

1. Push this repository to GitHub
2. Create a new Web Service on Render.com
3. Connect your GitHub repository
4. Render will automatically detect the `render.yaml` configuration

The app will be deployed with:
- Automatic HTTPS
- Auto-deploy on git push
- Environment variables for security

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3
- **Deployment**: Render.com (WSGI with Gunicorn)

## License

MIT
