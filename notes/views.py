# notes/views.py
from django.shortcuts import render, redirect
from .utils import generate_notes_gemini, generate_pdf, generate_word, generate_ppt

from django.shortcuts import render
import logging
from .utils import generate_notes_gemini

# Set up logging
logger = logging.getLogger(__name__)

def search_notes(request):
    topic = request.GET.get('topic', '').strip()
    notes_content = []
    notes_text = ""

    if topic:
        try:
            # Structured notes (list of dicts) from Gemini
            notes_content = generate_notes_gemini(topic)

            if not notes_content:
                notes_content = [{"type": "note", "text": "No notes generated."}]

            # Store structured notes in session for downloads
            request.session['topic'] = topic
            request.session['notes'] = notes_content

            # Convert structured notes to plain text for fallback downloads / sharing
            lines = []
            for item in notes_content:
                t = item.get('text', '').strip()
                if not t:
                    continue
                if item.get('type') == 'note':
                    lines.append(f"NOTE: {t}")
                elif item.get('type') == 'list':
                    level = item.get('level', 0)
                    indent = "  " * level
                    lines.append(f"{indent}• {t}")
                else:
                    lines.append(t)
            notes_text = "\n".join(lines)
            request.session['notes_text'] = notes_text

        except Exception as e:
            # Log the error and show fallback message
            logger.error(f"Gemini API error for topic '{topic}': {e}")
            notes_content = [{"type": "note", "text": "Unable to generate notes right now. Please try again later."}]
            notes_text = "Unable to generate notes at this time."

    return render(request, 'notes_template.html', {
        'topic': topic,
        'notes': notes_content,
        'notes_text': notes_text
    })


def download_pdf(request):
    topic = request.session.get('topic', 'Notes')
    notes_struct = request.session.get('notes', None)

    if notes_struct:
        return generate_pdf(topic, notes_struct)

    notes_text = request.session.get('notes_text', '')
    if not notes_text:
        return redirect('search_notes')
    return generate_pdf(topic, notes_text)



def download_word(request):
    topic = request.session.get('topic', 'Notes')
    # prefer structured if you want, but our Word accepts plain text
    notes_text = request.session.get('notes_text', '')
    if not notes_text:
        return redirect('search_notes')
    return generate_word(topic, notes_text)


def download_ppt(request):
    topic = request.session.get('topic', 'Notes')
    # Prefer structured notes (list) if available; fallback to plain text otherwise
    notes_struct = request.session.get('notes', None)
    if notes_struct:
        return generate_ppt(topic, notes_struct)
    notes_text = request.session.get('notes_text', '')
    if not notes_text:
        return redirect('search_notes')
    return generate_ppt(topic, notes_text)
