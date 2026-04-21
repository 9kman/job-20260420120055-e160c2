import anthropic
from app.config import Config
from datetime import datetime


class ClaudeService:
    def __init__(self, api_key=None):
        self.api_key = api_key or Config.ANTHROPIC_API_KEY
        self.client = anthropic.Anthropic(api_key=self.api_key) if self.api_key else None
        self.model = Config.CLAUDE_MODEL

    def compose_email(self, context, recipient_name=None, tone='professional'):
        if not self.client:
            return {'error': 'Claude API not configured'}

        prompt = f"""Compose a professional email with the following context:
- Recipient: {recipient_name or 'Recipient'}
- Context/Talking Points: {context}
- Tone: {tone}

Write a clear, concise, and professional email."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{'role': 'user', 'content': prompt}]
        )

        return {
            'content': response.content[0].text,
            'model': self.model,
            'tokens_used': response.usage.input_tokens + response.usage.output_tokens
        }

    def summarize_email_thread(self, emails):
        if not self.client:
            return {'error': 'Claude API not configured'}

        email_content = "\n\n".join([
            f"From: {e.get('sender', 'Unknown')}\nDate: {e.get('date', 'Unknown')}\nSubject: {e.get('subject', 'No Subject')}\n\n{e.get('body', '')}"
            for e in emails
        ])

        prompt = f"""Summarize the following email thread in a concise format:

{email_content}

Provide:
1. A brief summary (2-3 sentences)
2. Key points discussed
3. Any action items or deadlines mentioned"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{'role': 'user', 'content': prompt}]
        )

        return {
            'summary': response.content[0].text,
            'model': self.model,
            'tokens_used': response.usage.input_tokens + response.usage.output_tokens
        }

    def generate_response(self, incoming_email, tone='professional'):
        if not self.client:
            return {'error': 'Claude API not configured'}

        prompt = f"""Generate a {tone} response to the following email:

From: {incoming_email.get('sender', 'Unknown')}
Subject: {incoming_email.get('subject', 'No Subject')}

{incoming_email.get('body', '')}

Write a {tone} reply that appropriately addresses the email."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{'role': 'user', 'content': prompt}]
        )

        return {
            'content': response.content[0].text,
            'model': self.model,
            'tokens_used': response.usage.input_tokens + response.usage.output_tokens
        }


claude_service = ClaudeService()