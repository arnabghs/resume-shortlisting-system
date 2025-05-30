CREATE TABLE jobs
(
    id              SERIAL PRIMARY KEY,
    title           VARCHAR(255) NOT NULL,
    description     TEXT,
    required_skills TEXT
);

CREATE TABLE candidates
(
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    email       VARCHAR(255) UNIQUE,
    resume_text TEXT,
    job_id      INTEGER REFERENCES jobs (id)
);

CREATE TABLE skills
(
    id           SERIAL PRIMARY KEY,
    candidate_id INTEGER REFERENCES candidates (id),
    skill        VARCHAR(255)
);

CREATE TABLE experience
(
    id           SERIAL PRIMARY KEY,
    candidate_id INTEGER REFERENCES candidates (id),
    description  TEXT
);