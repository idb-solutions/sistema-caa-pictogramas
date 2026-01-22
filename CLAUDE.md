# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Sistema de Comunicação Alternativa com Pictogramas** (Alternative Communication System with Pictograms) for children with Autism Spectrum Disorder (TEA). It's a Flask-based web application that allows therapists to manage patients and enables children to communicate using visual pictograms with Brazilian Portuguese voice synthesis.

**Key Purpose:** Facilitate communication for children with ASD through a visual interface with 16 pictograms organized in 4 categories (Comida, Emoções, Necessidades, Ações), with integrated voice synthesis and session tracking.

## Development Commands

### Environment Setup
```bash
# Create and activate Anaconda environment
conda create -n caa_project python=3.11 -y
conda activate caa_project

# Install dependencies
pip install -r requirements.txt
```

### Database Initialization
```bash
# Initialize database with default data (categories, pictogramas, admin user)
python init_db.py

# Creates admin user: login='admin', senha='1234'
# Creates 4 categories with 16 pictograms
```

### Running the Application
```bash
# Start development server
python run.py

# Access at: http://localhost:5000
# Debug mode is enabled by default (see run.py:23)
```

### Testing API Endpoints
```bash
# Health check
curl http://localhost:5000/api/health

# List categories
curl http://localhost:5000/api/categorias

# List pictograms
curl http://localhost:5000/api/pictogramas

# Login (obtain session)
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"login": "admin", "senha": "1234"}'
```

## Architecture

### Application Factory Pattern
The app uses Flask's application factory pattern in `app/__init__.py:13-21`:
- `create_app(config_name)` creates and configures the Flask app
- `db` (SQLAlchemy instance) is initialized via `db.init_app(app)`
- Blueprint `main` is registered from `app/routes.py`

### Database Models (app/models.py)
7 tables with SQLAlchemy ORM:

1. **Usuario** - Therapists/professionals with simple numeric password authentication
2. **Paciente** - Children with ASD, linked to Usuario (1:N)
3. **Categoria** - 4 categories (Comida, Emoções, Necessidades, Ações) with color/icon
4. **Pictograma** - 16 pictograms, linked to Categoria (N:1)
5. **Sessao** - Therapy sessions with mandatory evaluation field
6. **HistoricoSelecao** - Log of each pictogram click during sessions
7. **Configuracao** - System configuration key-value store

**Critical Relationships:**
- `Usuario.pacientes` → Paciente (backref: `profissional`)
- `Sessao.paciente` → Paciente (backref: `sessoes`, cascade delete)
- `Sessao.profissional` → Usuario (backref: `sessoes`)
- `Sessao.historico` → HistoricoSelecao (cascade delete)
- `Pictograma.categoria` → Categoria (backref: `pictogramas`)

### Authentication Flow
Session-based authentication (not JWT):
- Login: `POST /api/login` → sets `session['usuario_id']`, `session['usuario_nome']`, `session['usuario_login']`
- `@login_required` decorator (routes.py:19-28) protects authenticated routes
- Sessions expire after 2 hours (`config.py:17`)

### API Structure (app/routes.py)

**Views (HTML):**
- `/` - Login page (redirects to `/selecionar-paciente` if logged in)
- `/cadastro` - Professional registration
- `/selecionar-paciente` - Patient selection (requires login)
- `/comunicacao/<int:paciente_id>` - Main pictogram interface (requires login)
- `/historico`, `/gerenciar` - Session history and management (require login)

**API Endpoints:**
- Authentication: `/api/login`, `/api/cadastro`, `/api/logout`, `/api/usuario/atual`
- Patients: `/api/pacientes` (GET, POST), `/api/pacientes/<id>` (GET, PUT, DELETE)
- Categories: `/api/categorias` (GET, POST), `/api/categorias/<id>` (PUT, DELETE)
- Pictograms: `/api/pictogramas` (GET, POST), `/api/pictogramas/<id>` (PUT, DELETE)
- Sessions: `/api/sessoes` (GET, POST), `/api/sessoes/<id>/selecao` (POST), `/api/sessoes/<id>/finalizar` (POST), `/api/sessoes/<id>/historico` (GET)
- Upload: `/api/upload` (POST - image upload for pictograms)

Refer to `documents/ENDPOINTS_API.md` for detailed API documentation.

### Configuration (config.py)
Three config classes: `Config` (base), `DevelopmentConfig`, `ProductionConfig`

**Key settings:**
- Database: SQLite at `database/comunicacao.db`
- Session lifetime: 2 hours
- Max upload size: 5MB
- Allowed image extensions: png, jpg, jpeg, gif
- Upload folder: `app/static/uploads`

### Frontend
Vanilla JavaScript with Web Speech API for voice synthesis:
- Templates in `app/templates/` (Jinja2)
- Static assets in `app/static/` (CSS, JS, images)
- Pictogram images should be 300x300 PNG in `app/static/images/`
- Voice synthesis uses browser's Web Speech API (Brazilian Portuguese)

### Session Workflow
1. Therapist logs in → selects/creates patient
2. System auto-creates `Sessao` when navigating to `/comunicacao/<paciente_id>`
3. Each pictogram click creates `HistoricoSelecao` entry via `POST /api/sessoes/<id>/selecao`
4. Finalizing session requires mandatory `avaliacao` field via `POST /api/sessoes/<id>/finalizar`
5. System calculates session duration and marks as `finalizada=True`

## Important Notes

### Password Security
Passwords are stored in **plain text** (models.py:14). This is intentional for the educational/therapy context with simple 4-digit numeric passwords. Do not suggest adding password hashing unless explicitly requested.

### Soft Deletes
Patients and Pictograms use soft deletes (`ativo=False`) rather than hard deletes. Categories use hard deletes and cascade delete their pictograms.

### Image Paths
Pictograms reference images at `/static/images/<filename>`. The `init_db.py` script expects images like `agua.png`, `pao.png`, etc. to exist in `app/static/images/`.

### Mandatory Evaluation
When finalizing a session, the `avaliacao` field is **mandatory** (routes.py:525-528). The API will return 400 if not provided.

### Database Location
SQLite database is created at `database/comunicacao.db` relative to project root (config.py:14-15).

### Session Management
- Only one active session per patient at a time (routes.py:476-483)
- If a session is already open for a patient, `POST /api/sessoes` returns the existing session_id
- Sessions track the professional who created them (`profissional_id`)

## Project Context

**Institution:** UNINTER - Atividade Extensionista I
**Course:** CST em Ciência de Dados
**Target Audience:** Clinics and special education schools in Costa Rica-MS, Brazil
**UN SDGs:** ODS 3 (Health and Well-being), ODS 4 (Quality Education), ODS 10 (Reduced Inequalities)
