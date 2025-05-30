Sample curl to post a new job :

```
curl --location 'http://localhost:8000/api/jobs' \
--form 'title="Python Developer"' \
--form 'description="Python developer with 2+ years experience in SQL and web development"' \
--form 'required_skills="Python, SQL, FastAPI"'
```

Sample curl to get resume scores :
```
curl --location 'http://localhost:8000/api/shortlist' \
--form 'job_id="1"' \
--form 'resume=@"Tom.pdf"'
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
```
