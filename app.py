# app.py

import os
import openai # <-- USES OPENAI
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import PyPDF2
from pptx import Presentation

# Load environment variables from .env file
load_dotenv()

# Configure the OpenAI API key
try:
    openai.api_key = os.environ["OPENAI_API_KEY"]
except KeyError:
    print("ERROR: OpenAI API Key not found.")

# ... (the rest of your OpenAI code) ...