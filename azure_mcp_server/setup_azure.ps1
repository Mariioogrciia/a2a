# Setup Azure Function App configuration
# Step 1: Set Linux FX Version to Python 3.11
az functionapp config set --name function-futbol-mcp --resource-group GarciaRomeroMario --linux-fx-version "Python|3.11"

# Step 2: Set required app settings
az functionapp config appsettings set --name function-futbol-mcp --resource-group GarciaRomeroMario --settings FUNCTIONS_WORKER_RUNTIME=python
