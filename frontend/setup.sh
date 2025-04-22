#!/bin/bash

# Create necessary directories
mkdir -p backend/data

# Copy frontend files to the frontend directory
mkdir -p frontend
cp -r app components contexts hooks lib public services types frontend/

# Copy package.json, next.config.js, and other necessary files
cp package.json package-lock.json next.config.js tsconfig.json tailwind.config.ts postcss.config.js frontend/

# Create .env file from template if it doesn't exist
if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env file from template. Please update with your actual values."
fi

# Build and start the containers
docker-compose up -d

echo "Kurobara application is now running!"
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000/api"
