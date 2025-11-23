A procedural-generative-hybrid game engine for playing the 5th edition ruleset of Dungeons & Dragons.

# Project Setup for Development

The backend of the app runs off of a set of Docker containers. To configure them, a copy of the `server/backend/.env.template` file must be made, renamed to `.env`, and properly populated.

Using VSCode extensions such as *Container Tools* and *Docker DX* can make running the `docker-compose.yml` file simple. However, through the command line, the container can be initialized and launched using the `docker-compose up` command.

Once the containers are running, the app should be accessible. To view the Vue server console logs, run `docker-compose logs -f frontend` in the terminal.

> *Note: If using the PGAdmin4 extension for Docker Desktop on Windows to assist in managing the database for local development, the server address must be set to `host.docker.internal`*