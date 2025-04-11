from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_babel import Babel, BabelConfigs, BabelMiddleware
# Ensure ONLY lazy_gettext is imported as _
from fastapi_babel import lazy_gettext as _
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import os
from jinja2 import Environment, FileSystemLoader # Import Jinja2 Environment components
# Use relative import since database.py is in the same directory
from .database import connect_to_mongo, close_mongo_connection, get_database
# Import the new router
from .routers import word_pairs, practice, progress
import logging

# Define logger for this module
logger = logging.getLogger(__name__)

# Ensure the base directory is the project root for correct path resolution
# This needs to be defined before BabelConfigs
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Babel configuration - might still be needed for context
babel_configs = BabelConfigs(
    ROOT_DIR=BASE_DIR, # Use BASE_DIR here
    BABEL_DEFAULT_LOCALE="en",
    # Use an absolute path for the translation directory
    BABEL_TRANSLATION_DIRECTORY=os.path.join(BASE_DIR, "locales"),
)
babel = Babel(configs=babel_configs)

# Define the lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    await connect_to_mongo()
    print("Database connection established.")
    yield
    # Code to run on shutdown
    await close_mongo_connection()
    print("Database connection closed.")

app = FastAPI(
    title="Linguator API",
    description="API for the Linguator language learning app",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware first
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Add Babel middleware using the standard FastAPI method
app.add_middleware(BabelMiddleware, babel_configs=babel_configs)

# Install Babel middleware instead of init_app - Keep commented
# babel.install_middleware(app)

# --- Static Files & Templates Configuration ---

# Ensure the base directory is the project root for correct path resolution
# BASE_DIR is already defined above, no need to redefine
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Mount static files (like htmx.min.js) - REMOVED as static files are not used for this feature anymore
# app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "src/frontend/static")), name="static")

# Configure templates by creating environment first
# templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "src/frontend/templates"))
# Comment out the i18n extension again
# templates.env.add_extension(\'jinja2.ext.i18n\')
# Use install_jinja again instead of configure_jinja_env
# babel.install_jinja(templates.env)

# Create and configure Jinja environment separately
jinja_env = Environment(loader=FileSystemLoader(os.path.join(BASE_DIR, "src/frontend/templates")))
babel.install_jinja(jinja_env) # Configure the env
# Remove manual additions to globals
# jinja_env.globals['_'] = gettext
# jinja_env.globals['gettext'] = gettext
# jinja_env.globals['ngettext'] = ngettext
templates = Jinja2Templates(env=jinja_env) # Pass the pre-configured env

# --- End Static Files & Templates Configuration ---

# Include the word_pairs router with a prefix for API endpoints
app.include_router(word_pairs.router, prefix="/word-pairs", tags=["Word Pairs"])
app.include_router(practice.router)
app.include_router(progress.router)

# --- UI Routes ---

@app.get("/", response_class=RedirectResponse, status_code=302)
async def read_root(request: Request):
    """Redirects the root path to the word pairs UI page."""
    return RedirectResponse(url="/ui/word-pairs")

@app.get("/ui/word-pairs", response_class=HTMLResponse)
async def word_pairs_page(request: Request):
    """Serves the Word Pairs list UI page."""
    context = {
        "request": request,
        "_": _  # Add back lazy_gettext to context
    }
    return templates.TemplateResponse("word_pair_list.html", context)

@app.get("/ui/practice", response_class=HTMLResponse)
async def practice_mode_page(request: Request):
    """Serves the Practice Mode UI shell page."""
    context = {
        "request": request,
        "_": _  # Add back lazy_gettext to context
    }
    return templates.TemplateResponse("practice_mode.html", context)

@app.get("/ui/progress", response_class=HTMLResponse)
async def progress_tracking_page(request: Request):
    """Serves the Progress Tracking UI page."""
    context = {
        "request": request,
        "_": _  # Add back lazy_gettext to context
    }
    return templates.TemplateResponse("progress_tracking.html", context)

# --- End UI Routes ---

# Add a simple health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    logger.info("Health check requested")
    db_status = "Unknown"
    try:
        db_instance = get_database() # Use the function
        await db_instance.command('ping') # Use the instance
        db_status = "OK"
        logger.info("Database ping successful")
    except RuntimeError as e:
        # Handle case where DB is not initialized
        db_status = "Not Connected"
        logger.warning(f"Database not initialized during health check: {e}")
    except Exception as e:
        logger.error(f"Database ping failed during health check: {e}")
        db_status = "Error"
    return {"status": "OK", "database": db_status}
