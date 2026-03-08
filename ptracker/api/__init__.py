from flask_smorest import Blueprint

api_bp = Blueprint("api", __name__, url_prefix="/api", description="API endpoints")

# noqa: E402 ignores "import not at top of file"
# noqa: F401 ignores "unused import"
from . import auth_routes  # noqa: E402, F401
from . import item_routes  # noqa: E402, F401
