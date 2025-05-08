from fasthtml.common import *
from web_ui.routes import rt # Import the router instance

# Initialize the FastHTML application
# The `rt` object is typically created by `fast_app()` and then routes are defined on it.
# However, if routes are in a separate file, we need to ensure the app instance uses that router.
# A common pattern if routes are split:
# In routes.py:
#   from fasthtml.routing import APIRouter
#   rt = APIRouter()
#   @rt.get("/") ...
# In main_app.py:
#   from fasthtml.common import fast_app
#   from web_ui.routes import rt as web_routes_router # rt is already an APIRouter instance
#   app, _ = fast_app() # _ can be a throwaway router if web_routes_router handles all
#   app.include_router(web_routes_router)

# Simpler approach for now, if routes.py defines functions on an imported app or router:
# Let routes.py define and attach routes to `app` directly.
# This file will just initialize and serve.

# Option 1: app and rt are created here and passed or imported into routes.py
# app, rt = fast_app(debug=True) # debug=True for development
# import web_ui.routes # This would make routes.py define routes on the imported app/rt

# Option 2: (Preferred for cleaner separation) app created here, router imported
from web_ui.routes import init_routes # A function that takes the app and adds routes

app, _ = fast_app(debug=True) # Create app, we might not use the returned router directly if web_ui.routes has its own
init_routes(app) # Pass the app instance to initialize routes

# Placeholder for where the uploaded file will be temporarily stored
# In a real app, this needs to be more robust, secure, and cleaned up.
UPLOAD_DIR = Path("./temp_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

if __name__ == "__main__":
    serve() # FastHTML's way to run Uvicorn
