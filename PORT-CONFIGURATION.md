# Port Configuration Guide

This document explains how to configure custom ports for the CareerCraft AI application.

## Backend Port Configuration

The backend supports several ways to configure the port:

### 1. Command Line Arguments

```bash
# Start backend on port 8080
python backend/main.py --port 8080

# Start backend on different host and port
python backend/main.py --host 0.0.0.0 --port 9000

# Other options
python backend/main.py --help
```

### 2. Environment Variable

```bash
# Set PORT environment variable
export PORT=8080
python backend/main.py

# Or inline
PORT=8080 python backend/main.py
```

### 3. Default Port

If no port is specified, the backend defaults to port 8000.

## Frontend Port Configuration

The frontend uses React Scripts and supports these options:

### 1. Environment Variable

```bash
# Start frontend on port 3001
PORT=3001 npm start

# Or export first
export PORT=3001
npm start
```

### 2. Package.json Scripts

We've added convenience scripts:

```bash
# Start on custom port (uses PORT env var, defaults to 3000)
npm run start:port

# Start on specific ports
npm run start:3001
npm run start:3002
```

### 3. Default Port

The frontend defaults to port 3000 if no PORT environment variable is set.

## Development Script

Use the included `start-dev.sh` script to start both backend and frontend with custom ports:

```bash
# Start with default ports (backend: 8000, frontend: 3000)
./start-dev.sh

# Start with custom backend port
./start-dev.sh 8080

# Start with custom backend and frontend ports
./start-dev.sh 8080 3001
```

### What the script does:

1. Starts the backend on the specified port
2. Updates the frontend's `.env.local` to point to the correct backend port
3. Starts the frontend on the specified port
4. Handles graceful shutdown of both servers with Ctrl+C

## Environment Configuration

The development script automatically updates the frontend's API configuration:

- Updates `REACT_APP_API_BASE_URL` in `.env.local`
- Ensures frontend connects to the correct backend port
- Preserves other environment variables

## Production Deployment

For production deployment:

### Backend
```bash
# Using environment variable
PORT=80 python backend/main.py --host 0.0.0.0 --no-reload

# Using command line
python backend/main.py --host 0.0.0.0 --port 80 --no-reload --log-level info
```

### Frontend
```bash
# Build for production
npm run build

# Serve with custom port (using serve package)
npx serve -s build -l 3000
```

## Docker Configuration

When using Docker, map ports in your docker-compose.yml or docker run commands:

```yaml
# docker-compose.yml
services:
  backend:
    build: ./backend
    ports:
      - "8080:8000"  # Map host:container
    environment:
      - PORT=8000
  
  frontend:
    build: ./frontend
    ports:
      - "3001:3000"
    environment:
      - PORT=3000
      - REACT_APP_API_BASE_URL=http://localhost:8080
```

## Troubleshooting

### Port Already in Use

If you get a "port already in use" error:

```bash
# Find what's using the port
lsof -i :8000

# Kill the process (replace PID with actual process ID)
kill -9 <PID>
```

### Frontend Can't Connect to Backend

1. Check that backend is running on the expected port
2. Verify `.env.local` has the correct `REACT_APP_API_BASE_URL`
3. Check browser network tab for failed requests
4. Ensure CORS is configured for the frontend's port

### Development Script Issues

1. Make sure the script is executable: `chmod +x start-dev.sh`
2. Check that both `python` and `npm` are available in PATH
3. Ensure you're running from the project root directory