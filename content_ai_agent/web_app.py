"""
Streamlit веб-интерфейс для Content AI Agent
"""
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json
import io
import os

from content_ai_agent.main import ContentAIAgent
from content_ai_agent.modules.content_agent import ContentStatus, ContentFormat
from content_ai_agent.modules.analytics import AnalyticsReport
from content_ai_agent.config import Config
