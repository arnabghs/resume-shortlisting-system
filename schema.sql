CREATE TABLE candidates
(
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    email       VARCHAR(255),
    resume_text TEXT
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

CREATE TABLE jobs
(
    id              SERIAL PRIMARY KEY,
    title           VARCHAR(255) NOT NULL,
    description     TEXT,
    required_skills TEXT
);