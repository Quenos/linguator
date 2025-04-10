from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_babel import Babel, BabelConfigs, BabelMiddleware
from contextlib import asynccontextmanager
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

app.include_router(word_pairs.router)

@app.get("/")
def read_root(request: Request):
    # gettext should work via the middleware-managed babel instance on the request
    return {"message": request.state.babel.gettext("Hello World")}
