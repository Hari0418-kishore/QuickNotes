# notes/views.py
from django.shortcuts import render, redirect
from .utils import generate_notes_gemini, generate_pdf, generate_word, generate_ppt

def search_notes(request):
    topic = request.GET.get('topic', '').strip()
    notes_content = []
    notes_text = ""

    if topic:
        # structured notes (list of dicts)
        notes_content = generate_notes_gemini(topic)

        # Store structured notes in session for downloads (preferred)
        request.session['topic'] = topic
        request.session['notes'] = notes_content

        # Convert structured notes to plain text string for fallback downloads / sharing
        lines = []
        for item in notes_content:
            t = item.get('text', '').strip()
            if not t:
                continue
            if item.get('type') == 'note':
                lines.append(f"NOTE: {t}")
            elif item.get('type') == 'list':
                # simple bullet marker
                level = item.get('level', 0)
                indent = "  " * level
                lines.append(f"{indent}• {t}")
            else:
                lines.append(t)
        notes_text = "\n".join(lines)
        request.session['notes_text'] = notes_text

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
