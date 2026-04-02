#!/bin/bash

# Navigate to the project directory (adjust if needed)
cd /Users/kenny/Desktop/productChatBot

# Initialize Git repository if not already done
if [ ! -d ".git" ]; then
    git init
    echo "Git repository initialized."
else
    echo "Git repository already exists."
fi

# Add all files to Git
git add .

# Commit the changes
git commit -m "Initial commit: Secure AI Customer Support Chatbot"

# Add GitHub remote (replace <your-github-username> and <your-repo-name> with actual values)
# Example: git remote add origin https://github.com/yourusername/productChatBot.git
git remote add origin https://github.com/<your-github-username>/<your-repo-name>.git

# Push to GitHub (use -u to set upstream)
git push -u origin main

echo "Project deployed to GitHub repository."
