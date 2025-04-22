# Kurobara - Docker Setup

This repository contains Docker configuration for running the Kurobara manga management application.

## Prerequisites

- Docker
- Docker Compose

## Setup

1. Clone this repository
2. Copy your backend code to the `backend` directory
3. Run the setup script:

\`\`\`bash
chmod +x setup.sh
./setup.sh
\`\`\`

4. Update the `.env` file with your actual configuration values
5. Access the application at http://localhost:3000

## Environment Variables

- `NEXT_PUBLIC_API_URL`: URL for the frontend to connect to the backend API
- `DATABASE_URL`: Connection string for the database
- `JWT_SECRET`: Secret key for JWT token generation

## Directory Structure

\`\`\`
kurobara/
├── backend/           # Backend application code
├── frontend/          # Frontend application code
├── docker-compose.yml # Docker Compose configuration
├── .env               # Environment variables
└── README.md          # This file
\`\`\`

## Development

To run the application in development mode:

\`\`\`bash
docker-compose -f docker-compose.dev.yml up
\`\`\`

## Production

To run the application in production mode:

\`\`\`bash
docker-compose up -d
\`\`\`

## Troubleshooting

If you encounter any issues:

1. Check the logs: `docker-compose logs -f`
2. Ensure all environment variables are correctly set
3. Verify network connectivity between containers
\`\`\`

Let's also create a development version of the docker-compose file for development purposes:
