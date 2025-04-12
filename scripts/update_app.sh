#!/bin/bash
# scripts/update_app.sh

# Navigate to project directory
cd /home/ubuntu/stormslide

# Activate virtual environment
source venv/bin/activate

# Pull latest changes
git pull origin main

# Check if pull was successful (no conflicts)
if [ $? -eq 0 ]; then
    # Restart Flask app
    sudo supervisorctl reread
    sudo supervisorctl update
    sudo supervisorctl restart flask_app
    echo "$(date): Successfully updated and restarted Flask app" >> logs/update.log
else
    echo "$(date): Git pull failed, check for conflicts" >> logs/update.log
fi