# Employee Helpdesk Backend

This folder contains the FastAPI backend for the AI-Powered Employee Helpdesk. It exposes REST endpoints for creating and managing IT support tickets, assigning tickets to support staff, recording ticket activity, calculating dashboard counts, and generating and reviewing AI ticket suggestions.

This guide is written for someone new to the project. It describes the application structure, local setup, API, database expectations, and the path a request takes through the code.

## Contents

- [What the backend does](#what-the-backend-does)
- [Technology](#technology)
- [Project layout](#project-layout)
- [How a request is processed](#how-a-request-is-processed)
- [Database requirements](#database-requirements)
- [Setup and run](#setup-and-run)
- [API reference](#api-reference)
- [Business rules and validation](#business-rules-and-validation)
- [AI analysis details](#ai-analysis-details)
- [Errors and troubleshooting](#errors-and-troubleshooting)
- [Tests and smoke checks](#tests-and-smoke-checks)
- [Current limitations](#current-limitations)

## What the backend does

The backend is the interface between a frontend (or another HTTP client), PostgreSQL, and a local Hugging Face language model.

The main capabilities are:

1. **Ticket management** — create, list, view, edit, and track tickets.
2. **Ticket workflow** — record status and priority changes, comments, and history.
3. **Assignments** — assign tickets to support staff, transfer assignments, and view assignment history.
4. **Dashboard** — count tickets by status, priority, and category.
5. **AI assistance** — analyze a ticket using Qwen, save a validated suggestion, retrieve previous suggestions, and submit support-staff feedback.
6. **Operational checks** — return a basic health response and test PostgreSQL connectivity.

The backend does not include a frontend, user registration flow, login, or database migration scripts.

## Technology

- **Python** — uses modern type annotation syntax (`list[...]` and `X | None`).
- **FastAPI** — HTTP routing, dependency injection, request parsing, and OpenAPI documentation.
- **Pydantic 2** — request and response validation.
- **PostgreSQL** — persistent application data.
- **Psycopg 3** and **psycopg_pool** — PostgreSQL driver and connection pool.
- **Hugging Face Transformers** — local model and text-generation pipeline.
- **LangChain** and **langchain-huggingface** — prompt construction and a LangChain wrapper around the Transformers pipeline.
- **Qwen2.5-3B-Instruct** — local model used for ticket analysis.

Dependencies are listed in [`tests/requirements.txt`](./tests/requirements.txt). Despite the directory name, this file includes both runtime packages and test/smoke-check packages.

## Project layout

```text
backend/
├── app/
│   ├── main.py                    # FastAPI app, lifecycle, and router registration
│   ├── config.py                  # Loads DATABASE_URL from backend/.env or environment
│   ├── database.py                # PostgreSQL connection pool and request dependency
│   ├── ai/
│   │   ├── huggingface_client.py  # Cached local model and generation pipeline
│   │   └── prompts.py             # System and ticket-analysis prompt templates
│   ├── routers/                   # HTTP endpoint definitions
│   ├── schemas/                   # Pydantic request/response models
│   ├── services/                  # Business rules and error translation
│   └── repositories/              # SQL queries and persistence operations
├── models/
│   └── qwen2.5-3b-instruct/       # Downloaded local model snapshot
├── tests/
│   ├── conftest.py                # Isolated FastAPI test application
│   ├── test_api.py                # Automated route and feedback tests
│   └── requirements.txt           # Backend and test/smoke-check dependencies
├── download_model.py              # Downloads the configured Qwen model snapshot
├── test_ai_schema.py              # Manual Pydantic schema check
└── test_huggingface_client.py     # Manual local-model smoke check
```

### Responsibilities by layer

- **Router** (`app/routers`) declares the URL, HTTP method, request body, dependency, and response model. It delegates work to a service.
- **Schema** (`app/schemas`) validates incoming values and specifies the shape of outgoing API responses.
- **Service** (`app/services`) coordinates operations, enforces application rules, and converts repository outcomes into HTTP errors.
- **Repository** (`app/repositories`) runs parameterized SQL statements and returns database rows.
- **AI support** (`app/ai`) constructs the model prompt and initializes the local model pipeline.

PostgreSQL connections use `dict_row`, so repository rows are accessed by column name (for example, `ticket["ticket_id"]`). SQL values are passed using Psycopg `%s` placeholders.

## How a request is processed

For a typical database-backed endpoint:

1. FastAPI matches the URL to a function in a router.
2. FastAPI validates the URL parameters and, when present, the JSON request body using Pydantic.
3. `Depends(get_db)` checks out a connection from the shared pool.
4. The router calls the corresponding service.
5. The service applies business rules and calls one or more repositories.
6. The repository executes SQL and returns rows as dictionaries.
7. The service returns a result or raises `HTTPException`.
8. FastAPI validates the output against the declared response model, serializes it as JSON, and returns the connection to the pool.

The connection pool is configured in `app/database.py` with a minimum size of 1 and a maximum size of 10. It is opened when the FastAPI application starts and closed during shutdown by the lifespan handler in `app/main.py`.

### Route prefixes

Ticket routes from `app/routers/tickets.py` are mounted directly at `/tickets`. The other routers are mounted under `/api`:

| Router | Effective base URL |
|---|---|
| Tickets | `/tickets` |
| Assignments | `/api/tickets` |
| Dashboard | `/api/dashboard` |
| AI analysis/history | `/api/tickets` |
| AI feedback | `/api/ai-suggestions` |

Consequently, ticket operations are split between `/tickets/...` and `/api/tickets/...`; use the paths shown in the API reference below.

## Database requirements

The application expects a PostgreSQL database and requires a connection string in `DATABASE_URL`. The pool is configured to create connections on application startup.

### Tables, columns, and relationships

This reference lists the columns that the current repositories read or write, together with the role of each table. It is reverse-engineered from the SQL and response models in this repository; it is **not** a substitute for a database DDL script. The exact PostgreSQL types and all existing constraints cannot be confirmed here because the project directory does not currently contain a complete schema or migration.

Recommended types below use PostgreSQL conventions (`BIGINT` identifiers, `TEXT` for free-form text, `VARCHAR`/enum/check constraints for bounded values, `BOOLEAN` flags, and `TIMESTAMPTZ` timestamps). Existing database types may differ, but column names and compatible types must support the queries.

#### `users`

An application user who can be an employee, support worker, or administrator. Employee and support names/emails are joined into API responses.

| Column | Purpose and use |
|---|---|
| `user_id` | Primary key; referenced by tickets, activities, and `support_staff`. Positive integer identifier. |
| `full_name` | User's display name; selected as `requester_name` and `staff_name`. Recommended required text. |
| `email` | User contact email; selected as `requester_email` and `staff_email`. Recommended required and unique. |
| `role` | Role checked by the API: `EMPLOYEE`, `SUPPORT`, or `ADMIN`. |
| `is_active` | Boolean used to reject inactive requesters, actors, and support staff. |

#### `support_staff`

Maps a support staff identifier to the corresponding user account.

| Column | Purpose and use |
|---|---|
| `staff_id` | Primary key used in assignment requests and ticket assignments. |
| `user_id` | Foreign key to `users.user_id`; used to verify role/active state and obtain staff details. |

#### `tickets`

The current state of each support request. The API returns all columns from the ticket row plus requester display details.

| Column | Purpose and use |
|---|---|
| `ticket_id` | Primary key; used in routes and references from related records. |
| `requester_id` | Foreign key to `users.user_id`; must identify an active `EMPLOYEE` when a ticket is created. |
| `title` | Required short issue summary; API limits it to 200 characters. |
| `description` | Required issue description. |
| `category` | One of `HARDWARE`, `SOFTWARE`, `NETWORK`, `ACCESS`, or `OTHER`; defaults to `OTHER` at the API boundary. |
| `priority` | One of `LOW`, `MEDIUM`, or `HIGH`; repository expects a database default for new tickets. |
| `status` | One of `OPEN`, `IN_PROGRESS`, `RESOLVED`, or `CLOSED`; repository expects a database default for new tickets. |
| `created_at` | Creation timestamp used for list ordering and recent-ticket context. |
| `updated_at` | Updated when editable details, status, or priority change. |

Requester name and email are not copied into the ticket: create/list/detail queries join `tickets.requester_id` to `users.user_id`. The ticket response exposes those joined values as `requester_name` and `requester_email`.

#### `ticket_activity`

Append-only history for ticket changes and comments. The history endpoint reads these rows chronologically.

| Column | Purpose and use |
|---|---|
| `activity_id` | Primary key and tie-breaker for ordering history. |
| `ticket_id` | Foreign key to `tickets.ticket_id`. |
| `performed_by` | Optional actor ID, normally referencing `users.user_id`; some detail-edit events currently omit it. |
| `activity_type` | Event kind, for example `TICKET_CREATED`, `TICKET_UPDATED`, `STATUS_CHANGE`, `PRIORITY_CHANGE`, `COMMENT`, assignment events, or `AI_FEEDBACK_REVIEWED`. |
| `comment` | Human-readable note or event description; also stores support comments. |
| `old_status`, `new_status` | Previous and resulting status for status transitions; nullable for other activity kinds. |
| `old_priority`, `new_priority` | Previous and resulting priority for priority changes. AI feedback review currently records the old and final priority here. |
| `created_at` | Event timestamp; used to order a ticket's history. |

The current repository's category-change activity does not store old/new category values. Keep the event type/comment to describe that category change, or extend the table and repository if a full category before/after audit is required.

#### `user_activity`

Activity log associated with a user and, where applicable, a ticket.

| Column | Purpose and use |
|---|---|
| `user_id` | User associated with the action; omitted for some ticket-edit log rows. |
| `activity_type` | Event kind such as ticket creation, status/priority update, assignment, comment, or AI feedback submission. |
| `description` | Human-readable summary, such as a ticket number or reviewed suggestion ID. |
| `ticket_id` | Related ticket ID when the event concerns a ticket. |

The repository does not select a user-activity primary key or timestamp. The database may define them, but the code currently only requires the columns above and any defaults/nullable behavior needed for omitted values.

#### `ticket_assignments`

Assignment history. Reassignment marks the former row `TRANSFERRED` and creates a new active row rather than overwriting assignment history.

| Column | Purpose and use |
|---|---|
| `assignment_id` | Primary key. |
| `ticket_id` | Foreign key to `tickets.ticket_id`. |
| `staff_id` | Foreign key to `support_staff.staff_id`. |
| `assigned_by` | User ID of the support/admin actor who assigned or reassigned the ticket; nullable in response models. |
| `assigned_at` | Assignment timestamp and history ordering field. |
| `unassigned_at` | Set when an assignment is transferred; null for an active assignment. |
| `assignment_status` | At minimum supports `ACTIVE` and `TRANSFERRED`; used to locate the current assignment. |

The application expects no more than one active assignment per ticket. Enforce that invariant in the database as well as in application logic (for example, with a partial unique index on active assignments).

#### `ai_suggestions`

Immutable proposal generated by the local model. It is stored separately from the human-confirmed ticket values.

| Column | Purpose and use |
|---|---|
| `suggestion_id` | Primary key. |
| `ticket_id` | Foreign key to `tickets.ticket_id`. |
| `suggested_category` | AI category from the allowed ticket categories. |
| `suggested_priority` | AI priority from `LOW`, `MEDIUM`, or `HIGH`. |
| `troubleshooting_steps` | Generated initial troubleshooting guidance. |
| `explanation` | Generated explanation for the recommendations. |
| `model_name` | Model identifier saved with the suggestion, currently `Qwen/Qwen2.5-3B-Instruct`. |
| `created_at` | Suggestion timestamp; suggestions are listed newest first. |

#### `ai_feedback`

Human review of an AI suggestion. This table must support the current feedback implementation, which inserts and returns the columns below.

| Column | Purpose and use |
|---|---|
| `feedback_id` | Primary key; feedback history ordering field. |
| `suggestion_id` | Foreign key to `ai_suggestions.suggestion_id`. |
| `reviewed_by` | Support staff ID, referencing `support_staff.staff_id`. |
| `is_useful` | Whether the reviewer considered the recommendation useful. |
| `decision` | `ACCEPTED`, `CORRECTED`, or `REJECTED`; records the review outcome. |
| `corrected_category` | Optional human correction to the AI category. |
| `corrected_priority` | Optional human correction to the AI priority. |
| `final_category` | Human-confirmed category after accepting/correcting. Null for rejection. |
| `final_priority` | Human-confirmed priority after accepting/correcting. Null for rejection. |
| `comments` | Optional reviewer note. |

On `ACCEPTED`, final values are copied from the AI suggestion. On `CORRECTED`, corrected values override the AI values and any uncorrected field retains its AI value. Those final values are applied to the ticket; the original suggestion remains unchanged. On `REJECTED`, ticket values are not changed and final fields are null.

### Foreign-key overview

The relationships expected by repository joins and operations are:

```text
support_staff.user_id          -> users.user_id
tickets.requester_id            -> users.user_id
ticket_activity.ticket_id       -> tickets.ticket_id
ticket_activity.performed_by    -> users.user_id (nullable)
user_activity.user_id           -> users.user_id (nullable)
user_activity.ticket_id         -> tickets.ticket_id (nullable)
ticket_assignments.ticket_id    -> tickets.ticket_id
ticket_assignments.staff_id     -> support_staff.staff_id
ticket_assignments.assigned_by  -> users.user_id (nullable)
ai_suggestions.ticket_id        -> tickets.ticket_id
ai_feedback.suggestion_id       -> ai_suggestions.suggestion_id
ai_feedback.reviewed_by         -> support_staff.staff_id
```

Use database constraints for primary/foreign keys, required fields, role/category/priority/status values, and one-active-assignment-per-ticket where possible. Timestamp defaults should be provided for fields the repository does not explicitly insert.

**Schema and migration status:** the current backend directory does not contain a complete initial schema, seed data, or any `.sql` migration file. In particular, `ai_feedback` must already have the `decision`, `final_category`, and `final_priority` columns described above for the current feedback endpoint to work. No migration file is available here to add them automatically. Provision or update the database schema separately before using those endpoints. Active user and support-staff records are also required for the corresponding operations.

## Setup and run

### Prerequisites

1. Python with support for the type syntax used by the code (Python 3.10 or later).
2. PostgreSQL with the required schema described above.
3. A Hugging Face model snapshot under `backend/models/qwen2.5-3b-instruct` if you intend to use AI analysis.
4. Enough RAM/compute to load Qwen2.5-3B-Instruct. The Transformers model loader uses `device_map="auto"` and `torch_dtype="auto"`; whether CPU or GPU execution is suitable depends on the machine and installed PyTorch build.

### Create the database configuration

Create `backend/.env` with a PostgreSQL connection string:

```dotenv
DATABASE_URL=postgresql://USERNAME:PASSWORD@HOST:5432/DATABASE_NAME
```

Replace the example values with the credentials and database details for your environment. Do not commit real credentials. `app/config.py` loads this file relative to the backend directory; an environment variable named `DATABASE_URL` can also provide the setting.

### Install Python packages

Run these commands from the `backend` directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r .\tests\requirements.txt
```

If PowerShell prevents activation, use the Python executable inside `.venv` directly, or follow your organization's virtual-environment policy.

### Download the local AI model (optional)

The model files are large. The repository currently includes a model snapshot in `models/qwen2.5-3b-instruct`. If that directory is absent or incomplete, run from `backend`:

```powershell
python .\download_model.py
```

The script downloads `Qwen/Qwen2.5-3B-Instruct` using `huggingface_hub.snapshot_download` into `./models/qwen2.5-3b-instruct`. A Hugging Face account or token may be needed if download access or rate limits require it.

AI model loading is lazy: the model is initialized only when the first analysis request is made. The initialized client is cached for the process, so subsequent analysis requests reuse it.

### Start the server

From the `backend` directory:

```powershell
python -m uvicorn app.main:app --reload
```

By default, Uvicorn listens on `http://127.0.0.1:8000`. Interactive OpenAPI documentation is available at `http://127.0.0.1:8000/docs`; the generated schema is at `http://127.0.0.1:8000/openapi.json`.

Starting from the backend directory matters for the model: `MODEL_PATH` is relative (`models/qwen2.5-3b-instruct`). The `.env` path itself is resolved relative to the `app` package.

### Check the service

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/db-check
```

- `/health` confirms that the HTTP application responds. It does not check the database.
- `/db-check` runs `SELECT version()` and confirms PostgreSQL connectivity.

## API reference

All request and response bodies use JSON unless noted otherwise. OpenAPI/Swagger at `/docs` is the authoritative generated reference for response schemas.

### Health and database

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/` | Returns a short service-running message. |
| `GET` | `/health` | Returns `{"status":"healthy"}` when the HTTP application responds. |
| `GET` | `/db-check` | Runs a PostgreSQL version query and returns database connectivity information. |

### Tickets

#### `POST /tickets/` — create a ticket

Example request:

```json
{
  "requester_id": 12,
  "title": "Laptop will not connect to Wi-Fi",
  "description": "The laptop can see the office network but cannot connect.",
  "category": "NETWORK"
}
```

`requester_id` is the positive ID of an existing active employee in `users`. It is the ticket's requester reference; the API does not create user accounts or accept duplicate requester contact details. The create, list, and detail responses include `requester_name` and `requester_email`, read from that linked user record. `title` is required and has a maximum length of 200 characters. `description` is required. Both are trimmed and rejected if blank. `category` can be `HARDWARE`, `SOFTWARE`, `NETWORK`, `ACCESS`, or `OTHER`; if omitted it defaults to `OTHER`.

The requester must be an active user with role `EMPLOYEE`. On success, the ticket is created, a `TICKET_CREATED` ticket-activity record is inserted, and a `TICKET_CREATED` user-activity record is inserted. Returns `201 Created` with a ticket response.

#### `GET /tickets/` — list tickets

Optional query parameters:

| Parameter | Meaning |
|---|---|
| `status` | Match a ticket status. |
| `category` | Match a category. |
| `priority` | Match a priority. |
| `requester_id` | Match a requester. |
| `limit` | Page size, default `100`, minimum `1`. |
| `offset` | Number of rows to skip, default `0`, minimum `0`. |

Filters are combined with `AND`. Results are sorted by creation time, newest first. The query parameters for status/category/priority are plain strings; unlike request-body fields, they are not constrained by an enum in the route schema.

Example: `GET /tickets/?status=OPEN&category=NETWORK&limit=25&offset=0`

#### `GET /tickets/{ticket_id}` — get a ticket

Returns the ticket or `404` if no ticket has that ID.

#### `PATCH /tickets/{ticket_id}` — edit ticket details

Example request:

```json
{
  "title": "Laptop cannot join office Wi-Fi",
  "category": "NETWORK"
}
```

Any subset of `title`, `description`, and `category` can be supplied. Supplied title/description values are trimmed, cannot be blank, and have the same limits as ticket creation. Explicit `null` values are rejected by the service. An empty update is rejected. Returns the updated ticket, or `404` when the ticket does not exist.

Changes update `updated_at` and create ticket/user activity records. The API does not currently accept an actor ID for this edit, so the corresponding activity actor is not identified by the request.

#### `GET /tickets/{ticket_id}/history` — ticket activity

Returns ticket activity ordered oldest first. Each history item includes the activity ID, ticket ID, actor if recorded, activity type, comment, optional old/new status and priority, and creation time. A missing ticket returns `404`.

#### `PATCH /tickets/{ticket_id}/status` — change status

Example request:

```json
{
  "status": "IN_PROGRESS",
  "updated_by": 27
}
```

Allowed values are `OPEN`, `IN_PROGRESS`, `RESOLVED`, and `CLOSED`. The allowed transitions are strictly sequential:

```text
OPEN -> IN_PROGRESS -> RESOLVED -> CLOSED
```

Only an active `SUPPORT` or `ADMIN` user may change status. A support user must have an active assignment to the ticket; an admin does not. Each successful change updates the ticket and writes ticket/user activity. Invalid transitions return `409`; missing tickets return `404`; invalid actors or non-assigned support staff return `403`.

#### `PATCH /tickets/{ticket_id}/priority` — change priority

Example request:

```json
{
  "priority": "HIGH",
  "updated_by": 27
}
```

Allowed values are `LOW`, `MEDIUM`, and `HIGH`. Only active support staff or an admin may change priority. Support staff must be assigned to the ticket. Setting the existing priority returns `409` and does not create redundant activity. Successful changes are recorded in ticket and user activity.

#### `POST /tickets/{ticket_id}/comments` — add a comment

Example request:

```json
{
  "comment": "I can reproduce the issue on the office network.",
  "added_by": 27
}
```

The comment must contain 1–2000 characters after trimming; `added_by` must be positive. The actor must be active. Employees may comment on their own tickets, support staff may comment on tickets assigned to them, and admins may comment on any ticket. The comment is stored as a `COMMENT` ticket-activity record, and a user-activity record is also written. The created activity is returned with `201 Created`.

### Assignments

#### `POST /api/tickets/{ticket_id}/assign` — assign a ticket

```json
{
  "staff_id": 8,
  "assigned_by": 27
}
```

Both IDs must be positive. The ticket must exist, the target must be an active support-staff member, and the assigner must be an active `SUPPORT` or `ADMIN` user. A ticket can have only one active assignment. A successful assignment creates an assignment-history row and ticket/user activity, returning `201 Created`. Existing active assignments return `409`.

#### `PATCH /api/tickets/{ticket_id}/reassign` — transfer a ticket

```json
{
  "new_staff_id": 9,
  "reassigned_by": 27
}
```

The new staff member must be active support staff. The actor must be active support staff or an admin. A support actor can reassign only a ticket currently assigned to them; an admin can reassign any ticket. The existing active assignment is marked `TRANSFERRED` with an unassignment time, then a new active assignment is created. The transfer is recorded in ticket/user activity.

Missing tickets or staff members return `404`; authorization failures return `403`; missing assignments or attempts to reassign to the same staff member return `409`.

#### `GET /api/tickets/{ticket_id}/assignments` — assignment history

Returns assignment records oldest first, including assignment status/timestamps and the support staff member's name and email. A missing ticket returns `404`.

### Dashboard

#### `GET /api/dashboard/summary`

Returns an aggregate of all rows in `tickets`:

```json
{
  "total_tickets": 42,
  "by_status": {
    "OPEN": 10,
    "IN_PROGRESS": 12,
    "RESOLVED": 15,
    "CLOSED": 5
  },
  "by_priority": {
    "LOW": 20,
    "MEDIUM": 16,
    "HIGH": 6
  },
  "by_category": {
    "HARDWARE": 9,
    "SOFTWARE": 12,
    "NETWORK": 8,
    "ACCESS": 6,
    "OTHER": 7
  }
}
```

Counts are computed by PostgreSQL using filtered aggregate counts.

### AI analysis and feedback

#### `POST /api/tickets/{ticket_id}/analyze` — create an AI suggestion

No request body is required. The service:

1. Checks that the ticket exists (`404` otherwise).
2. Retrieves up to 20 newest tickets other than the ticket being analyzed.
3. Serializes those records as JSON for prompt context.
4. Formats the system and user prompt with ticket data and history.
5. Loads/reuses the local model and generates text.
6. Extracts the first complete JSON object from the output.
7. Validates its fields against `AIAnalysisResponse`.
8. Saves a valid suggestion and returns its ID, ticket ID, creation time, and analysis.

The analysis fields are `suggested_category`, `suggested_priority`, `troubleshooting_steps`, and `explanation`. Categories and priorities must use the allowed values documented above; the two text fields must be non-empty.

Invalid model output returns `502`. Model-loading, invocation, or other analysis failures return `503`. Analysis is an advisory suggestion: it does not automatically change ticket category, priority, status, or assignment.

#### `GET /api/tickets/{ticket_id}/ai-suggestions` — list saved suggestions

Returns all suggestions for the ticket, newest first. Each suggestion includes its generated fields, model name, timestamp, and a `feedback` array (empty when no feedback has been submitted). A missing ticket returns `404`.

#### `POST /api/ai-suggestions/{suggestion_id}/feedback` — submit feedback

Example request:

```json
{
  "reviewed_by": 27,
  "is_useful": true,
  "decision": "CORRECTED",
  "corrected_category": "NETWORK",
  "corrected_priority": "MEDIUM",
  "comments": "The suggested steps were useful."
}
```

`reviewed_by` must be positive and identify an active support-staff member. `is_useful` is required. `decision` is `ACCEPTED`, `CORRECTED`, or `REJECTED`; it is inferred for older clients when omitted: corrections imply `CORRECTED`, otherwise a useful response implies `ACCEPTED`, and a not-useful response implies `REJECTED`. A `CORRECTED` decision requires at least one corrected field. `corrected_category` and `corrected_priority` use the same allowed values as ticket categories and priorities. `comments` is optional, limited to 1000 characters, trimmed, and converted to null when blank.

Accepting a suggestion stores its suggested category and priority as the final human-confirmed values and updates the ticket. Correcting a suggestion stores the corrected fields, uses the AI value for any field not corrected, and updates the ticket with both final values. Rejecting a suggestion stores the review but leaves ticket values unchanged. All decisions are stored separately from the original AI proposal and written to ticket activity. Responses and later suggestion-history results include `decision`, `corrected_category`, `corrected_priority`, `final_category`, and `final_priority`. A missing suggestion returns `404`; an invalid/inactive support staff member returns `403`. Successful feedback returns `201 Created`.

### Example request flow

The following sequence illustrates a typical ticket lifecycle. Replace IDs with valid values from the configured database:

1. Employee creates a ticket: `POST /tickets/`.
2. Support staff or an admin assigns it: `POST /api/tickets/{ticket_id}/assign`.
3. Support staff analyzes the issue: `POST /api/tickets/{ticket_id}/analyze`.
4. A support staff member reviews the AI response: `POST /api/ai-suggestions/{suggestion_id}/feedback`.
5. The assigned support staff member starts work: `PATCH /tickets/{ticket_id}/status` with `IN_PROGRESS`.
6. The assigned support staff member adds a comment: `POST /tickets/{ticket_id}/comments`.
7. Support staff resolves the issue, then closes it: status transitions through `RESOLVED` and `CLOSED`.
8. The client can retrieve ticket activity, assignment history, AI suggestions, or the dashboard summary at any time using their corresponding GET endpoints.

## Business rules and validation

### Categories and priorities

Ticket and AI categories:

```text
HARDWARE, SOFTWARE, NETWORK, ACCESS, OTHER
```

Priorities:

```text
LOW, MEDIUM, HIGH
```

The AI prompt guides the model to assign priority according to business impact, but the backend only validates that the resulting priority is one of the allowed values.

### User roles and authorization checks

Repository SQL checks active users and their roles for protected operations:

- `EMPLOYEE` — may create a ticket for themselves (the request supplies `requester_id`) and comment on their own ticket.
- `SUPPORT` — may perform certain changes only when assigned to the ticket; active support users can be assignment targets and can submit AI feedback.
- `ADMIN` — may assign/reassign tickets, update status/priority, and comment without the support assignment requirement.

These are database-backed business checks, not a complete authentication system. See [Current limitations](#current-limitations).

### Activity records

Successful operations record history in `ticket_activity`, `user_activity`, or both:

- Ticket creation writes both.
- Ticket detail edits write both; the actor is currently not supplied for these edits.
- Status/priority updates write both with old/new values and the actor.
- Assignment/reassignment writes both.
- Comments write a ticket activity entry and a user activity entry.

Ticket history is returned oldest-first. Assignment history is also returned oldest-first. AI suggestions are returned newest-first; feedback for a suggestion is ordered newest-first.

## AI analysis details

### Prompt

`app/ai/prompts.py` creates a LangChain `ChatPromptTemplate` with:

- A system message containing the helpdesk role, allowed categories and priorities, priority guidance, and response constraints.
- A JSON example showing the required output shape.
- A human message containing the ticket ID, title, description, current category and priority, plus recent ticket history.

The literal braces around the JSON example are escaped for LangChain's template formatter. The history is supporting context only; the prompt explicitly instructs the model not to assume a historical ticket has the same root cause.

### Model initialization

`app/ai/huggingface_client.py` loads the tokenizer and causal language model from `models/qwen2.5-3b-instruct`, then builds a Transformers `text-generation` pipeline. Generation is deterministic (`do_sample=False`), allows up to 512 new tokens, and returns generated text rather than the full prompt. `@lru_cache(maxsize=1)` caches the resulting LangChain `HuggingFacePipeline` in the process.

### Output parsing and persistence

Model output is not assumed to be JSON-only. The service scans for an opening `{` and uses Python's JSON decoder to parse the first complete JSON object it finds. Pydantic then validates required fields, literal category/priority values, and non-empty strings. Only validated suggestions are written to `ai_suggestions`.

If the model returns malformed output or an object that does not match the schema, the endpoint responds with `502`. If the model cannot load or an error occurs during analysis/persistence, the service currently responds with `503`.

## Errors and troubleshooting

FastAPI/Pydantic returns `422 Unprocessable Entity` when request bodies or query constraints fail validation. Service errors use standard JSON error bodies, generally shaped as `{"detail":"..."}`.

| Symptom | Likely cause / next step |
|---|---|
| Server fails at startup with a missing `DATABASE_URL` | Create `backend/.env` or set the environment variable before launching. |
| `/health` works but database endpoints fail | `/health` does not use PostgreSQL. Check `DATABASE_URL`, PostgreSQL availability, credentials, and required schema; use `/db-check`. |
| `/db-check` returns a connection error | Confirm the database host, port, name, credentials, network access, and PostgreSQL service. |
| `404` for a ticket or suggestion | Verify the ID exists in the configured database. |
| `403` for assignment, status, priority, comments, or feedback | Check that the supplied actor is active, has the required role, and (for support actions) has an active assignment. |
| `409` during status update | Only the next transition in `OPEN → IN_PROGRESS → RESOLVED → CLOSED` is accepted. |
| AI endpoint returns `503` and model-path errors | Run the server from `backend` and verify `models/qwen2.5-3b-instruct` exists and is complete. |
| AI endpoint returns `503` with memory/device errors | The local 3B model could not initialize with available CPU/GPU resources or the installed PyTorch build. |
| AI endpoint returns `502` with `Invalid AI response` | The generated output was not a valid JSON object matching the required schema. Check the error detail and server output. |
| `GET /openapi.json` returns a schema error | Check all Pydantic schema modules for unresolved type annotations/imports. The OpenAPI generator evaluates all route response models. |
| Model download fails | Check network access, Hugging Face availability/rate limits, and available disk space. |

When diagnosing a failed request, capture both the HTTP response body and the backend traceback. A Uvicorn access-log line by itself reports the status code but not the underlying exception.

## Tests and smoke checks

Run the automated API tests from the project root:

```powershell
python -m pytest backend\tests -q
```

The automated tests use FastAPI's test client and mocked repository/model dependencies; they do not require a live PostgreSQL server or download/load the model. They cover ticket creation, required-field validation, status updates, AI-model-unavailable responses, and persisted correction/final-value handling at the service boundary.

Two optional smoke scripts are also available. Run these from the `backend` directory:

```powershell
python .\test_ai_schema.py
python .\test_huggingface_client.py
```

The model check is slower and requires model files and sufficient compute. It exercises local model loading but does not test the HTTP endpoint or PostgreSQL persistence. There is not yet a live-database integration test suite.

## Current limitations

- **Authentication is not implemented.** Endpoints that need an actor accept IDs such as `updated_by`, `assigned_by`, `reassigned_by`, `added_by`, or `reviewed_by` in request bodies. The database verifies the referenced user's role and active status, but the API does not establish that the HTTP caller is actually that user. Do not expose this service as an authenticated production API without adding and consistently enforcing an authentication/authorization layer.
- **Initial schema, migrations, and seed data are not included.** The application assumes externally provisioned PostgreSQL core tables and defaults. The current feedback endpoint requires the additional review/final-value columns documented above; this directory does not currently include a script to add them.
- **AI inference is local and synchronous.** The first analysis request may take a long time while the model loads. CPU/GPU memory and latency depend on the host machine.
- **Model output can be invalid.** Schema validation prevents invalid suggestions from being saved, but the request fails rather than repairing or retrying malformed output.
- **Automated tests mock the repositories.** Database SQL and transaction behavior still need integration testing against a provisioned PostgreSQL instance.
- **Ticket edit actor is not recorded.** The ticket edit endpoint does not accept a user identity, and its activity log cannot attribute that edit to an actor.
- **Request filters are lightly validated.** List filters for status, category, and priority are strings; clients should send known enum values.
