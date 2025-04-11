from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_babel import Babel, BabelConfigs, BabelMiddleware
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os
# Use relative import since database.py is in the same directory
from .database import connect_to_mongo, close_mongo_connection, get_database
# Import the new router
from .routers import word_pairs, practice
import logging

# Babel configuration - might still be needed for context
babel_configs = BabelConfigs(
    ROOT_DIR=__file__,
    BABEL_DEFAULT_LOCALE="en",
    BABEL_TRANSLATION_DIRECTORY="locales",
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

# Install Babel middleware instead of init_app
# babel.install_middleware(app)

# Add Babel middleware using the standard FastAPI method
app.add_middleware(BabelMiddleware, babel_configs=babel_configs)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# --- Static Files & Templates Configuration ---

# Ensure the base directory is the project root for correct path resolution
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Mount static files (like htmx.min.js) - REMOVED as static files are not used for this feature anymore
# app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "src/frontend/static")), name="static")

# Configure templates
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "src/frontend/templates"))

# --- End Static Files & Templates Configuration ---

# Include the word_pairs router with a prefix for API endpoints
app.include_router(word_pairs.router, prefix="/word-pairs", tags=["Word Pairs"])
app.include_router(practice.router)

# --- UI Routes ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serves the main page, redirecting or showing a welcome message."""
    db_status = "Unknown"
    ping_status = "N/A"
    try:
        db_instance = get_database() # Use the function to get the DB instance
        db_status = "Connected"
        # Optional: Ping DB to be sure
        await db_instance.command('ping') # Use the obtained instance
        ping_status = "Ping OK"
    except RuntimeError as e:
        # Handle case where DB is not initialized
        db_status = "Not Connected"
        ping_status = f"Check Failed: {e}"
        logger.warning(f"Database not initialized when checking root page: {e}")
    except Exception as e:
        db_status = "Error"
        ping_status = f"Ping Failed: {e}"
        logger.error(f"MongoDB connection error on root page: {e}")

    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "Welcome to Linguator",
        "db_status": db_status,
        "ping_status": ping_status
    })

@app.get("/ui/word-pairs", response_class=HTMLResponse)
async def word_pairs_page(request: Request):
    """Serves the Word Pairs list UI page."""
    return templates.TemplateResponse("word_pair_list.html", {"request": request})

@app.get("/ui/practice", response_class=HTMLResponse)
async def practice_mode_page(request: Request):
    """Serves the Practice Mode UI shell page."""
    # This just serves the initial HTML shell.
    # The actual practice content is loaded via client-side JS now
    return templates.TemplateResponse("practice_mode.html", {"request": request})

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
