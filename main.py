from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
import psycopg2
from psycopg2.extras import RealDictCursor
import uvicorn

# Download NLTK data
nltk.download('punkt')
nltk.download('punkt_tab')

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
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

# Extract text from PDF
def extract_text(pdf_file):
    try:
        with pdfplumber.open(pdf_file) as pdf:
            text = "".join(page.extract_text() for page in pdf.pages if page.extract_text())
        return text if text else ""
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse PDF: {str(e)}")

# Score resume against job description using TF-IDF
def score_resume(resume_text, job_description):
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
    similarity = (tfidf_matrix * tfidf_matrix.T).toarray()[0, 1]
    return similarity * 100

@app.post("/api/shortlist")
async def shortlist_resume(job_desc: str = Form(...), resume: UploadFile = File(...)):
    # Validate inputs
    if not job_desc.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty")
    if not resume.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Extract resume text
    resume_text = extract_text(resume.file)
    if not resume_text:
        raise HTTPException(status_code=400, detail="Resume is empty or unreadable")


    # Parse basic fields
    name = resume.filename.split('.')[0]
    skills = " ".join(nltk.word_tokenize(resume_text.lower())[:50])  # Basic skill extraction

    # Save to database
    conn = get_db()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "INSERT INTO candidates (name, resume_text) VALUES (%s, %s) RETURNING id",
            (name, resume_text)
        )
        candidate_id = cursor.fetchone()['id']
        cursor.execute(
            "INSERT INTO skills (candidate_id, skill) VALUES (%s, %s)",
            (candidate_id, skills)
        )
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # Fetch all candidates and rank
    try:
        cursor.execute("SELECT id, name, resume_text FROM candidates")
        candidates = cursor.fetchall()
        results = []
        for candidate in candidates:
            score = score_resume(candidate['resume_text'], job_desc)
            results.append({"id": candidate['id'], "name": candidate['name'], "score": score})
        results = sorted(results, key=lambda x: x['score'], reverse=True)
    finally:
        cursor.close()
        conn.close()

    return {"results": results}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)