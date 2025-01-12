#!/bin/bash

# Set strict mode for better error handling
set -euo pipefail

# Log file for debugging
LOG_FILE="/home/abdulrafay/mlops/course-project-abdul-rafay-1/cron_debug.log"

# Timestamp function for logging
timestamp() {
    date "+%Y-%m-%d %H:%M:%S"
}

# Logging function
log() {
    echo "$(timestamp) - $1" >> "$LOG_FILE"
}

# Start logging
log "Starting data collection script"

# Set environment variables
export HOME="/home/abdulrafay"
export PATH="/home/abdulrafay/.local/bin:/usr/local/bin:$PATH"

# Change to project directory
cd "/home/abdulrafay/mlops/course-project-abdul-rafay-1/src" || {
    log "Failed to change directory"
    exit 1
}

restart_flask() {
    # Find and kill existing Flask processes
    pkill -f "/usr/bin/python3 prediction_service.py"
    
    # Start Flask in the background
    /usr/bin/python3 prediction_service.py &

    
    # Check if Flask started successfully
    if [ $? -eq 0 ]; then
        log "Flask application restarted successfully"
    else
        log "Failed to restart Flask application"
        exit 1
    fi
}

#!/bin/bash

if /usr/bin/python3 data_collection.py; then
    log "Data collection script completed successfully"
    
    if /usr/bin/python3 model_training.py; then
        log "Model training script completed successfully"
        
        restart_flask
        exit 0
    else
        log "Model training script failed"
        exit 1
    fi
else
    log "Data collection script failed"
    exit 1
fi
log "Data collection script failed after $max_tries attempts"
exit 1
