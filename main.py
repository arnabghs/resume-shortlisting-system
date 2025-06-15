from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
import psycopg2
from psycopg2.extras import RealDictCursor
import uvicorn
import re
import logging
from io import BytesIO

# Configure logging
logging.basicConfig(
    filename="errors.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Download NLTK data
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for React frontend (to be added later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Database connection
def get_db():
    try:
        conn = psycopg2.connect(
            dbname="resume_db",
            user="myuser",
            password="mypassword",
            host="localhost",
            port="5432"
        )
        return conn
    except Exception as e:
        logging.error(f"Database connection failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Database connection failed")


# Extract text from PDF
def extract_text(pdf_file, max_size=5 * 1024 * 1024):  # 5MB limit
    try:
        # Check file size
        pdf_file.seek(0, 2)  # Move to end of file
        if pdf_file.tell() > max_size:
            logging.error("File size exceeds 5MB")
            raise HTTPException(status_code=400, detail="File size exceeds 5MB")
        pdf_file.seek(0)  # Reset to start

        with pdfplumber.open(pdf_file) as pdf:
            text = "".join(page.extract_text() for page in pdf.pages if page.extract_text())
        if not text:
            logging.error("Resume is empty or unreadable")
            raise HTTPException(status_code=400, detail="Resume is empty or unreadable")
        return text
    except Exception as e:
        logging.error(f"Failed to parse PDF: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to parse PDF: {str(e)}")


# Extract fields using regex
def extract_email(resume_text):
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    match = re.search(pattern, resume_text)
    return match.group(0) if match else "unknown@example.com"


def extract_skills(resume_text):
    pattern = r"(?:Skills|Technical Skills|Key Skills):?\s*([^\n]+)"
    match = re.search(pattern, resume_text, re.IGNORECASE)
    skills = []
    if match:
        skills = [s.strip() for s in match.group(1).split(",")]
    return skills if skills else ["unknown"]


def extract_experience(resume_text):
    pattern = r"(?:Experience|Work Experience):?\s*([^\n]+(?:\n[^\n]+)*)"
    match = re.search(pattern, resume_text, re.IGNORECASE)
    return match.group(1).strip() if match else ""


# Score resume against job description
def score_resume(experience_text, skills, job_description, skills_weight=0.3):
    try:
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        skills_text = " ".join(skills)
        skills_score = vectorizer.fit_transform([skills_text, job_description]).toarray()[0, 1] * skills_weight
        experience_score = vectorizer.fit_transform([experience_text, job_description]).toarray()[0, 1] * (1 - skills_weight)
        return (skills_score + experience_score) * 100
    except Exception as e:
        logging.error(f"TF-IDF scoring failed: {str(e)}")
        return 0.0


@app.post("/api/jobs")
async def create_job(title: str = Form(...), description: str = Form(...), required_skills: str = Form(...)):
    if not title.strip() or not description.strip():
        raise HTTPException(status_code=400, detail="Title and description cannot be empty")

    conn = get_db()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "INSERT INTO jobs (title, description, required_skills) VALUES (%s, %s, %s) RETURNING id",
            (title, description, required_skills)
        )
        job_id = cursor.fetchone()['id']
        conn.commit()
        return {"id": job_id, "title": title, "message": "Job created successfully"}
    except Exception as e:
        logging.error(f"Failed to create job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create job: {str(e)}")
    finally:
        cursor.close()
        conn.close()


@app.post("/api/apply")
async def apply_for_job(job_id: int = Form(...), resume: UploadFile = File(...)):
    # Validate inputs
    if not resume.filename.endswith('.pdf'):
        logging.error("Invalid file type uploaded")
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Check if job exists
    conn = get_db()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT id FROM jobs WHERE id = %s", (job_id,))
        if not cursor.fetchone():
            logging.error(f"Job ID {job_id} not found")
            raise HTTPException(status_code=404, detail="Job not found")
    except Exception as e:
        logging.error(f"Failed to verify job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to verify job: {str(e)}")
    finally:
        cursor.close()
        conn.close()

    # Extract resume text
    resume_text = extract_text(BytesIO(await resume.read()))

    # Parse fields
    name = resume.filename.split('.')[0]  # Simplified name extraction
    email = extract_email(resume_text)
    if not email:
        logging.error("No valid email found in resume")
        raise HTTPException(status_code=400, detail="No valid email found in resume")
    skills = extract_skills(resume_text)
    experience = extract_experience(resume_text)

    # Upsert candidate
    conn = get_db()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # Check if candidate exists
        cursor.execute("SELECT id FROM candidates WHERE email = %s", (email,))
        existing_candidate = cursor.fetchone()

        if existing_candidate:
            candidate_id = existing_candidate['id']
            # Update candidate
            cursor.execute(
                """
                UPDATE candidates
                SET name        = %s,
                    resume_text = %s,
                    job_id      = %s
                WHERE email = %s
                """,
                (name, resume_text, job_id, email)
            )
            # Delete existing skills and experience
            cursor.execute("DELETE FROM skills WHERE candidate_id = %s", (candidate_id,))
            cursor.execute("DELETE FROM experience WHERE candidate_id = %s", (candidate_id,))
        else:
            # Insert new candidate
            cursor.execute(
                """
                INSERT INTO candidates (name, email, resume_text, job_id)
                VALUES (%s, %s, %s, %s) RETURNING id
                """,
                (name, email, resume_text, job_id)
            )
            candidate_id = cursor.fetchone()['id']

        # Insert skills and experience
        for skill in skills:
            cursor.execute(
                "INSERT INTO skills (candidate_id, skill) VALUES (%s, %s)",
                (candidate_id, skill)
            )
        cursor.execute(
            "INSERT INTO experience (candidate_id, description) VALUES (%s, %s)",
            (candidate_id, experience)
        )
        conn.commit()
    except Exception as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

    return {
        "message": f"CV {'updated' if existing_candidate else 'uploaded'} successfully for job ID {job_id}",
        "candidate_id": candidate_id
    }


@app.get("/api/shortlist")
async def shortlist_candidates(job_id: int, limit: int = 0):
    # Intended for admin use only (authentication can be added later)

    # Validate job_id
    conn = get_db()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT description FROM jobs WHERE id = %s", (job_id,))
        job = cursor.fetchone()
        if not job:
            logging.error(f"Job ID {job_id} not found")
            raise HTTPException(status_code=404, detail="Job not found")
        job_description = job['description']
    except Exception as e:
        logging.error(f"Failed to fetch job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch job: {str(e)}")

    # Fetch candidates for the job
    try:
        cursor.execute("""
                       SELECT c.id               AS candidate_id,
                              c.name,
                              c.email,
                              e.description      AS experience,
                              ARRAY_AGG(s.skill) AS skills
                       FROM candidates c
                                LEFT JOIN skills s ON c.id = s.candidate_id
                                LEFT JOIN experience e ON c.id = e.candidate_id
                       WHERE c.job_id = %s
                       GROUP BY c.id, e.description
                       """, (job_id,))
        candidates = cursor.fetchall()
        if not candidates:
            return {"results": []}

        results = []
        for candidate in candidates:
            skills = candidate['skills'] if candidate['skills'] else ['unknown']
            experience = candidate['experience'] if candidate['experience'] else ''
            score = score_resume(experience, skills, job_description)
            results.append({
                "id": candidate['candidate_id'],
                "name": candidate['name'],
                "email": candidate['email'],
                "score": score
            })
        results = sorted(results, key=lambda x: x['score'], reverse=True)

        # Apply limit if specified
        if limit > 0:
            results = results[:limit]
    except Exception as e:
        logging.error(f"Ranking failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ranking failed: {str(e)}")
    finally:
        cursor.close()
        conn.close()

    return {"results": results}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
