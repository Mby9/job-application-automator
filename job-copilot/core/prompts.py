"""
Centralized storage for all AI prompts used by the application.
"""

# Job Fit Analysis Prompts
ANALYZE_JOB_FIT_PROMPT = """
Compare the following Resume and Job Description.
Provide:
1. A match score out of 100.
2. Five key skills missing or needing emphasis.
3. A brief summary of why the candidate is or isn't a good fit.

Format the output as valid JSON.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}
"""

ANALYZE_BATCH_JOB_FIT_PROMPT = """
You are an expert technical recruiter evaluating candidates.
Given the candidate's resume and a list of job descriptions (in JSON format), output ONLY a JSON object.
The keys should be the exact job `id` provided, and the value must be an integer from 0 to 100 representing the match score (how well the resume fits the job requirements).
Do NOT include any other text, summaries, or explanations. Just the JSON mapping.

RESUME:
{resume_text}

JOBS TO EVALUATE:
{jobs_json}
"""

# Cover Letter Generation Prompts
GENERATE_COVER_LETTER_PROMPT = """
Write a professional and compelling cover letter for the following job using the candidate's resume.
The tone should be enthusiastic but professional. Focus on specific achievements from the resume that match the job requirements.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}
"""

# Semantic Field Matching Prompts
SEMANTIC_MATCH_FIELDS_PROMPT = """
Match the Following "Current Labels" to the most semantically similar "Saved Labels".
Only match if they represent the same data field (e.g. "First Name" matches "Given Name").
Return a JSON object where keys are "Current Labels" and values are the corresponding "Saved Labels".
Do not include unmatched labels.

Current Labels: {current_labels}
Saved Labels: {saved_labels}
"""

# Company Domain Fetching Prompt
GET_COMPANY_DOMAINS_PROMPT = """
You are extremely accurate at identifying the primary corporate website domains for companies.
Given the following list of company names, return a JSON object where the keys are the exact company names provided, and the values are their primary website domain name (e.g. "openai.com", "google.com").
Exclude "www." and "https://". Just the bare domain.
If you cannot confidently identify a domain for a company, set its value to null.

COMPANY NAMES:
{company_names}
"""

# Resume Compression Prompt
RESUME_COMPRESSION_PROMPT = """
You are an expert resume optimizer. Your task is to take a raw, potentially noisy resume text and compress it by removing irrelevant information, filler words, and formatting noise while preserving all essential professional details.

Follow these rules:
1. EXTRACT and KEEP: Name, contact information, LinkedIn/Portfolio URLs.
2. ORGANIZE and CONDENSE: Work experience (Company, Title, Dates, Key Achievements). Summarize achievements into concise, impactful bullet points.
3. EXTRACT: Technical and soft skills.
4. KEEP: Education and relevant certifications/projects.
5. REMOVE: Generic objective statements, personal hobbies (unless highly relevant to tech), and verbose filler language.
6. OUTPUT: Return the optimized resume in a clean, structured text format that is easy for an AI to parse for job matching.

RAW RESUME TEXT:
{resume_text}
"""