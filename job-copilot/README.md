# Job Application Copilot

An intelligent job application automation system that helps users find, evaluate, and apply for jobs that match their profile.

## Features

- Automatic job discovery across multiple ATS platforms (Greenhouse, Lever, Ashby, Workday)
- AI-powered job matching and scoring
- Automated cover letter generation
- Smart form field auto-completion
- Company management and discovery
- Preference-based filtering
- Application status tracking

## AI Provider Configuration

This application supports multiple AI providers through an abstraction layer. You can configure which AI provider to use by setting environment variables.

### Supported AI Providers

#### Google Gemini (Default)
- Environment Variable: `AI_PROVIDER=gemini`
- Requires: `GEMINI_API_KEY`
- Default Model: `gemini-3.1-flash-lite-preview`

#### Alibaba Cloud Qwen
- Environment Variable: `AI_PROVIDER=qwen`
- Requires: `QWEN_API_KEY`
- Default Model: `qwen-max`

### Configuration

Create a `.env` file in the root directory with your settings:

```env
# AI Provider Configuration
AI_PROVIDER=gemini              # Options: gemini, qwen
GEMINI_API_KEY=your_gemini_key  # Required if using Gemini
QWEN_API_KEY=your_qwen_key      # Required if using Qwen
DEFAULT_MODEL_ID=gemini-3.1-flash-lite-preview  # Default model ID

# Database Configuration
DATABASE_URL=sqlite:///./job_automator.db
```

## Prompts Management

All AI prompts are centralized in the `prompts.py` file for easy maintenance and customization. The following prompts are defined:

- `ANALYZE_JOB_FIT_PROMPT`: Used to analyze how well a candidate matches a job description
- `GENERATE_COVER_LETTER_PROMPT`: Used to generate personalized cover letters
- `SEMANTIC_MATCH_FIELDS_PROMPT`: Used to match form fields semantically

You can customize these prompts to better suit your needs without modifying the core application logic.

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up your environment variables in a `.env` file
4. Run the application: `python main.py`

## Usage

The application provides a FastAPI web interface with the following endpoints:

- `GET /api/health` - Health check
- `POST /api/save-field` - Save field mappings for auto-fill
- `GET /api/get-fill-values` - Get saved field values
- `POST /api/match-fields` - Match form fields semantically
- `GET /api/preferences` - Get user preferences
- `PUT /api/preferences` - Save user preferences
- `GET /api/companies` - List companies
- `POST /api/companies` - Add a company
- `PUT /api/companies/{id}` - Update a company
- `DELETE /api/companies/{id}` - Delete a company
- `POST /api/companies/discover` - Discover companies
- `GET /api/jobs/discover` - Discover and score jobs
- `GET /api/jobs` - List jobs
- `PUT /api/jobs/{id}/status` - Update job status

## Architecture

- **Frontend**: API-based (designed for web interface)
- **Backend**: Python with FastAPI framework
- **Database**: SQLite with SQLAlchemy ORM
- **AI Engine**: Configurable AI provider (Google Gemini, Qwen, etc.)
- **Scrapers**: Individual modules for each ATS platform
- **Filter Engine**: Programmatic filtering logic