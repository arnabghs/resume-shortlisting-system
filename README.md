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
