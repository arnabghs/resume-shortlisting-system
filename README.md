## About

This application is a job application management system built using FastAPI and PostgreSQL. It allows users to post job listings, apply for jobs with resumes, and shortlist candidates based on their skills and experience.

### Features

- Post job listings with title, description, and required skills.
- Apply for jobs by uploading resumes.
- Shortlist candidates based on their resumes and job requirements.
- Store job listings and applications in a PostgreSQL database.

### Technologies Used
- FastAPI: A modern, fast (high-performance), web framework for building APIs
- PostgreSQL: A powerful, open source object-relational database system.
- Docker: To run the PostgreSQL database in a containerized environment.
- nltk: Natural Language Toolkit for processing resumes.
- pdfplumber: To extract text from PDF resumes.

---

## Development Environment Setup for Unix

Run the PostgresSQL database with Docker
```
docker run --name my-postgres \
  -e POSTGRES_USER=myuser \
  -e POSTGRES_PASSWORD=mypassword \
  -e POSTGRES_DB=resume_db \
  -p 5432:5432 \
  -d postgres:15
7d4ac160b8e0af230dae66216ed9fcd76f8cf6d05fb499764de8516d528640f3
```

Run the Schema migrations to create the necessary tables in the database:
```
docker exec -i my-postgres psql -U myuser -d resume_db < schema.sql
```

Activate the virtual environment and
```
source venv/bin/activate

```

Install the required packages:
```
pip install -r requirements.txt
```

Run the FastAPI application:
```
uvicorn main:app --reload
```

-------


Sample curl to post a new job :

```
curl --location 'http://localhost:8000/api/jobs' \
--form 'title="Python Developer"' \
--form 'description="Python developer with 2+ years experience in SQL and web development"' \
--form 'required_skills="Python, SQL, FastAPI"'
```

Sample curl to apply for jobs :
```
curl --location 'http://localhost:8000/api/apply' \
--form 'job_id="1"' \
--form 'resume=@"/Users/arnab.ghosh1/Documents/Tom.pdf"'
```

Sample curl to shortlist candidates for a job:
```
 curl --location 'http://localhost:8000/api/shortlist?job_id=1&limit=10'
```



Sample Resumes:

``` 
Jane Smith
Email: jane.smith@example.com
Skills: JavaScript, React,
Experience: Frontend Developer at ABC Inc (2023–2024) with 1 year
experience

---

John Doe
Email: john.doe@example.com
Skills: Python, Java, SQL,
Experience: Software Developer at XYZ Corp (2022–2024) with 2 years
experience

---

Tom Field
Email: tom.field@example.com
Skills: Angular, SQL, Typescript
Experience: Tech Lead at XYZ Corp (2020–2024) with 4 years
experience
```
