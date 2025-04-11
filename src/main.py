from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_babel import Babel, BabelConfigs, BabelMiddleware
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os
# Use relative import since database.py is in the same directory
from .database import connect_to_mongo, close_mongo_connection
# Import the new router
from .routers import word_pairs

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

app = FastAPI(lifespan=lifespan)

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
app.include_router(word_pairs.router, prefix="/word-pairs")

# --- UI Routes ---

@app.get("/ui/word-pairs", response_class=HTMLResponse)
async def word_pairs_page(request: Request):
    """Serves the main Word Pairs UI page."""
    return templates.TemplateResponse("word_pair_list.html", {"request": request})

@app.get("/ui/practice", response_class=HTMLResponse)
async def practice_mode_page(request: Request):
    """Serves the Practice Mode UI shell page."""
    # This just serves the initial HTML shell.
    # The actual practice content is loaded via HTMX calls.
    return templates.TemplateResponse("practice_mode.html", {"request": request})

# --- End UI Routes ---

@app.get("/")
def read_root(request: Request):
    # gettext should work via the middleware-managed babel instance on the request
    return {"message": request.state.babel.gettext("Hello World")}
