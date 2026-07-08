from datetime import timedelta

# JWT Configuration

SECRET_KEY = "scientific_collaboration_network_analyzer_infosys_springboard_2026"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60

ACCESS_TOKEN_EXPIRE_DELTA = timedelta(
    minutes=ACCESS_TOKEN_EXPIRE_MINUTES
)