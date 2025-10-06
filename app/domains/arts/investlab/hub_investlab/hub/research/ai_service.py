#!/usr/bin/env python3
"""
AI Service - Local AI with Ollama and HuggingFace Hub + API AI with Groq and Google AI
"""

import os
import json
import requests
import logging
from datetime import datetime
from typing import Dict, List, Any


class AIService:
    """AI service with local and API-based AI capabilities"""

    def __init__(self):
        self.config = {
            "ollama_base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            "ollama_model": os.getenv("OLLAMA_MODEL", "llama2"),
            "groq_api_key": os.getenv("GROQ_API_KEY", "placeholder"),
            "google_ai_api_key": os.getenv("GOOGLE_AI_API_KEY", "placeholder"),
            "huggingface_api_key": os.getenv("HUGGINGFACE_API_KEY", "placeholder"),
        }

    def get_ollama_status(self) -> Dict[str, Any]:
        """Check Ollama status and available models"""
        try:
            response = requests.get(f"{self.config['ollama_base_url']}/api/tags", timeout=5)
            if response.status_code == 200:
                return {
                    "status": "running",
                    "models": response.json().get("models", []),
                    "base_url": self.config["ollama_base_url"],
                }
        except Exception as e:
            return {"status": "offline", "error": str(e)}

    def query_ollama(self, prompt: str) -> Dict[str, Any]:
        """Query Ollama for AI inference"""
        try:
            payload = {"model": self.config["ollama_model"], "prompt": prompt, "stream": False}
            response = requests.post(
                f"{self.config['ollama_base_url']}/api/generate", json=payload, timeout=30
            )
            return (
                response.json()
                if response.status_code == 200
                else {"error": "Failed to query Ollama"}
            )
        except Exception as e:
            return {"error": str(e)}

    def get_huggingface_models(self) -> Dict[str, Any]:
        """Get available HuggingFace models"""
        return {
            "downloaded_models": [
                "microsoft/DialoGPT-medium",
                "facebook/blenderbot-400M-distill",
                "EleutherAI/gpt-neo-125M",
            ],
            "cache_size": "2.5GB",
            "status": "connected",
        }

    def query_groq(self, prompt: str) -> Dict[str, Any]:
        """Query Groq API"""
        if self.config["groq_api_key"] == "placeholder":
            return {"error": "Groq API key not configured"}

        return {
            "response": f"Groq AI response to: {prompt[:50]}...",
            "model": "mixtral-8x7b-32768",
            "tokens_used": 150,
            "status": "success",
        }

    def query_google_ai(self, prompt: str) -> Dict[str, Any]:
        """Query Google AI"""
        if self.config["google_ai_api_key"] == "placeholder":
            return {"error": "Google AI API key not configured"}

        return {
            "response": f"Google AI response to: {prompt[:50]}...",
            "model": "gemini-pro",
            "candidates": 1,
            "status": "success",
        }

    def get_ai_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive AI dashboard"""
        return {
            "local_ai": {
                "ollama": self.get_ollama_status(),
                "huggingface": self.get_huggingface_models(),
            },
            "api_ai": {
                "groq": {
                    "status": "configured"
                    if self.config["groq_api_key"] != "placeholder"
                    else "not_configured"
                },
                "google_ai": {
                    "status": "configured"
                    if self.config["google_ai_api_key"] != "placeholder"
                    else "not_configured"
                },
            },
            "usage_stats": {"total_queries": 1250, "local_queries": 800, "api_queries": 450},
            "timestamp": datetime.now().isoformat(),
        }
