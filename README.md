## What is EdHub?

EdHub is a Learning Management System for interaction between teachers, students, and parents. It aims to improve the quality of an educational process, simplify the interaction between stakeholders, and improve student engagement in learning.

Any user can create a course becoming a **Teacher**, invite students and their parents, upload materials, create assignments, see student submissions, grade them based on criteria, and calculate course grade. You can also join the course as a **Student** to see the study materials and submit your homework or as a **Parent** to track the academic performance of your child.

Most existing LMSs either have limited functionality or have awkward website design and cause difficulties in everyday use. EdHub combines a self-contained and clear design, supporting all the necessary features but not bogging the user down with complex customizations.

## 🚀 How to Launch

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) (v20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2.0+)

### Quick Start
```bash
# Clone repository
git clone https://github.com/IU-Capstone-Project-2025/edhub.git
cd edhub

# Build and start containers
docker-compose up --build

# To run in detached mode:
# docker-compose up --build -d
```

### Services Overview
| Service       | Access URL                     | Port  | Notes                     |
|---------------|--------------------------------|-------|---------------------------|
| **Frontend**  | http://localhost:5173         | 5173  | React application      |
| **Backend**   | http://localhost:8000         | 8000  | FastAPI application       |
| **Database**  | postgresql://db:5432/edhub    | 5432  | PostgreSQL container      |

### API Endpoints

You can access the web version of API documentation at http://localhost:8000/docs/.

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