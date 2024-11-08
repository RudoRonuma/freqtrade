#!/bin/bash

# Default values
INSTALL_REQUIREMENTS=true
REQUIREMENTS_FILE="requirements.txt"
CONFIG_FILE="user_data/config.json"
STRATEGY_NAME="Strategy005"
NO_RESTART=false

# Parse command line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --no-install) INSTALL_REQUIREMENTS=false ;;
        --requirements) REQUIREMENTS_FILE="$2"; shift ;;
        --config) CONFIG_FILE="$2"; shift ;;
        --strategy) STRATEGY_NAME="$2"; shift ;;
        --no-restart) NO_RESTART=true ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

# Function to install requirements
install_requirements() {
    if [ "$INSTALL_REQUIREMENTS" = true ]; then
        echo "Installing requirements from $REQUIREMENTS_FILE..."
        pip install -r "$REQUIREMENTS_FILE" --quiet
    else
        echo "Skipping requirements installation."
    fi
}

# Function to run the trading bot
run_bot() {
    echo "Running trading bot with strategy $STRATEGY_NAME..."
    python3 -m freqtrade trade --config "$CONFIG_FILE" --strategy "$STRATEGY_NAME"
}

# Main loop to handle unexpected exits
while true; do
    install_requirements
    run_bot

    if [ "$NO_RESTART" = true ]; then
        echo "Exiting..."
        break
    fi
    echo "Bot exited unexpectedly. Restarting..."
    sleep 1
done