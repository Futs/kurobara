#!/bin/bash

# Stop the development environment
docker-compose -f docker-compose.dev.yml down

echo "Development environment stopped!"
