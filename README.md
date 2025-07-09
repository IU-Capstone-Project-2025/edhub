[![Contributors][contributors-shield]][contributors-url]
[![Stargazers][stars-shield]][stars-url]
[![Forks][forks-shield]][forks-url]
[![Unlicense License][license-shield]][license-url]
[![Issues][prod-shield]][prod-url]
[![Issues][issues-shield]][issues-url]

You can use the public version of EdHub available at [www.edhub.space](https://edhub.space).

## What is EdHub?

EdHub is a Learning Management System for interaction between teachers, students, and parents. It aims to improve the quality of an educational process, simplify the interaction between stakeholders, and improve student engagement in learning.

Any user can create a course becoming a **Teacher**, invite students and their parents, upload materials, create assignments, see student submissions, grade them based on criteria, and calculate course grade. You can also join the course as a **Student** to see the study materials and submit your homework or as a **Parent** to track the academic performance of your child.

Most existing LMSs either have limited functionality or have awkward website design and cause difficulties in everyday use. EdHub combines a self-contained and clear design, supporting all the necessary features but not bogging the user down with complex customizations.

### Built With

* [![FastAPI][FastAPI]][FastAPI-url]
* [![React][React]][React-url]
* [![PostgreSQL][PostgreSQL]][PostgreSQL-url]
* [![NginX][NginX]][NginX-url]
* [![Docker][Docker]][Docker-url]

## Local Startup

These instructions will help you to download a copy of the project and run it on your local machine. All of your organization's data will be stored on your computer and will be inaccessible to external users.

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) (v20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2.0+)

### Quick Start
```bash
# Clone repository
git clone https://github.com/IU-Capstone-Project-2025/edhub.git
cd edhub

# Build and start containers
docker compose up --build

# To run in detached mode:
# docker compose up --build -d
```
Now you can go to http://localhost/ to access the application.

### Services Overview
| Service       | Port  | Notes                  |
|---------------|-------|------------------------|
| **Frontend**  | 3000  | React application      |
| **Backend**   | 8000  | FastAPI application    |
| **Database**  | 5432  | PostgreSQL container   |
| **Nginx**     | 80    | Nginx reverse proxy    |

### API Endpoints

You can access the web version of API documentation at http://localhost/api/docs/.

### Maintenance Commands
```bash
# Stop all services
docker compose down

# Stop and remove volumes
docker compose down -v

# View logs
docker compose logs -f

# Rebuild from scratch
docker compose down -v && docker compose up --build
```
[contributors-shield]: https://img.shields.io/github/contributors/IU-Capstone-Project-2025/edhub.svg?style=for-the-badge
[contributors-url]: https://github.com/IU-Capstone-Project-2025/edhub/graphs/contributors
[stars-shield]: https://img.shields.io/github/stars/IU-Capstone-Project-2025/edhub.svg?style=for-the-badge
[stars-url]: https://github.com/IU-Capstone-Project-2025/edhub/stargazers
[forks-shield]: https://img.shields.io/github/forks/IU-Capstone-Project-2025/edhub.svg?style=for-the-badge
[forks-url]: https://github.com/IU-Capstone-Project-2025/edhub/network/members
[issues-shield]: https://img.shields.io/github/issues/IU-Capstone-Project-2025/edhub.svg?style=for-the-badge
[issues-url]: https://github.com/IU-Capstone-Project-2025/edhub/issues
[license-shield]: https://img.shields.io/github/license/IU-Capstone-Project-2025/edhub.svg?style=for-the-badge
[license-url]: https://github.com/IU-Capstone-Project-2025/edhub/blob/main/LICENSE
[prod-shield]: https://img.shields.io/github/actions/workflow/status/IU-Capstone-Project-2025/edhub/deploy-prod.yml?style=for-the-badge
[prod-url]: https://github.com/IU-Capstone-Project-2025/edhub/actions

[FastAPI]: https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi
[FastAPI-url]: https://fastapi.tiangolo.com/
[React]: https://img.shields.io/badge/-ReactJs-61DAFB?logo=react&logoColor=white&style=for-the-badge
[React-url]: https://react.dev/
[PostgreSQL]: https://img.shields.io/badge/postgresql-4169e1?style=for-the-badge&logo=postgresql&logoColor=white
[PostgreSQL-url]: https://www.postgresql.org/
[NginX]: https://img.shields.io/badge/Nginx-009639?logo=nginx&logoColor=white&style=for-the-badge
[NginX-url]: https://nginx.org/
[Docker]: https://img.shields.io/badge/docker-257bd6?style=for-the-badge&logo=docker&logoColor=white
[Docker-url]: https://www.docker.com/