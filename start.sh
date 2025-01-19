 #!/bin/bash
 uvicorn app.main:app --host 0.0.0.0 --port $PORT --reload
 export $(grep -v '^#' .env | xargs)