import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request as URLRequest, urlopen

from django.conf import settings


def build_openai_messages(system_prompt, turns):
    return [{'role': 'system', 'content': system_prompt}] + list(turns)


def call_openai_chat(messages, max_tokens=450, temperature=0.7):
    """
    Call OpenAI Chat Completions API and return (reply_text, error_text).
    If successful, error_text is None. If failed, reply_text is None.
    """
    api_key = (getattr(settings, 'OPENAI_API_KEY', '') or os.environ.get('OPENAI_API_KEY', '')).strip()
    model = getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini')
    timeout = int(getattr(settings, 'OPENAI_TIMEOUT', 25))

    if not api_key:
        return None, 'OpenAI API key is missing. Set OPENAI_API_KEY in your environment.'

    payload = json.dumps({
        'model': model,
        'messages': messages,
        'max_tokens': max_tokens,
        'temperature': temperature,
    }).encode('utf-8')

    request = URLRequest(
        'https://api.openai.com/v1/chat/completions',
        data=payload,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        },
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read())
        text = data['choices'][0]['message']['content'].strip()
        return text, None
    except HTTPError as exc:
        return None, f'OpenAI request failed with status {exc.code}.'
    except URLError:
        return None, 'Could not reach OpenAI service. Check your network and API settings.'
    except Exception:
        return None, 'Unexpected error while calling OpenAI.'
