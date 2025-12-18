import io
import json
import wave
import streamlit as st
from agents import groq_chat, ollama_chat
from frontend.provider import _get_client


def generate_followup_question(resume_text: str, last_question: str, transcript: str, api_key: str) -> str:
    provider = st.session_state.get('provider', 'openai')
    if provider == 'openai':
        client = _get_client(api_key)
        sys = (
            "You are a concise technical interviewer. Generate ONE short follow-up question (max 25 words) "
            "to probe deeper based on the prior question and the candidate's answer. If no follow-up is needed, respond with NONE."
        )
        user = (
            f"Resume context (for tailoring):\n{resume_text[:1500]}\n\n"
            f"Previous question: {last_question}\n"
            f"Candidate answer transcript: {transcript}"
        )
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": sys}, {"role": "user", "content": user}],
            temperature=0.2,
        )
        content = resp.choices[0].message.content.strip()
        return None if content.upper().startswith("NONE") else content
    else:
        sys = (
            "You are a concise technical interviewer. Generate ONE short follow-up question (max 25 words) "
            "to probe deeper based on the prior question and the candidate's answer. If no follow-up is needed, respond with NONE."
        )
        user = (
            f"Resume context (for tailoring):\n{resume_text[:1500]}\n\n"
            f"Previous question: {last_question}\n"
            f"Candidate answer transcript: {transcript}"
        )
        try:
            if st.session_state.get('provider') == 'groq':
                content = groq_chat(st.session_state.api_key, messages=[{"role": "system", "content": sys}, {"role": "user", "content": user}])
            elif st.session_state.get('provider') == 'ollama':
                content = ollama_chat(messages=[{"role": "system", "content": sys}, {"role": "user", "content": user}], model=st.session_state.get('ollama_model'), base_url=st.session_state.get('ollama_base_url'))
            else:
                return None
            content = content.strip()
            return None if content.upper().startswith("NONE") else content
        except Exception:
            return None


def synthesize_speech(text: str, api_key: str) -> bytes:
    if st.session_state.get('provider', 'openai') != 'openai':
        raise RuntimeError("TTS is only available with the OpenAI provider in this app.")
    client = _get_client(api_key)
    resp = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text,
        response_format="mp3",
    )
    if hasattr(resp, "content") and isinstance(resp.content, (bytes, bytearray)):
        return resp.content
    try:
        return bytes(resp)
    except Exception:
        pass
    try:
        return resp.read()
    except Exception:
        pass
    raise RuntimeError("TTS response not in expected binary format")


def transcribe_audio(audio_file, api_key: str) -> str:
    if st.session_state.get('provider', 'openai') != 'openai':
        raise RuntimeError("Audio transcription is only available with the OpenAI provider in this app.")
    client = _get_client(api_key)
    data = audio_file.read()
    audio_file.seek(0)
    fname = getattr(audio_file, 'name', 'answer.wav')
    mime = getattr(audio_file, 'type', 'audio/wav')
    file_tuple = (fname, io.BytesIO(data), mime)
    tr = client.audio.transcriptions.create(
        model="whisper-1",
        file=file_tuple,
        response_format="json",
    )
    text = getattr(tr, 'text', None)
    if text is None:
        try:
            text = tr["text"]
        except Exception:
            text = ""
    return text or ""


def _wav_bytes_from_pcm16(pcm_bytes: bytes, sample_rate: int = 48000, channels: int = 1) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_bytes)
    buf.seek(0)
    return buf.read()


def transcribe_pcm_bytes(pcm_bytes: bytes, sample_rate: int, api_key: str) -> str:
    wav_bytes = _wav_bytes_from_pcm16(pcm_bytes, sample_rate=sample_rate, channels=1)
    if st.session_state.get('provider', 'openai') != 'openai':
        raise RuntimeError("Audio transcription is only available with the OpenAI provider in this app.")
    client = _get_client(api_key)
    fname = 'answer.wav'
    mime = 'audio/wav'
    file_tuple = (fname, io.BytesIO(wav_bytes), mime)
    tr = client.audio.transcriptions.create(
        model="whisper-1",
        file=file_tuple,
        response_format="json",
    )
    text = getattr(tr, 'text', None)
    if text:
        return text
    try:
        return tr.get('text', '')
    except Exception:
        return ""


def score_answer(question: str, transcript: str, api_key: str) -> dict:
    provider = st.session_state.get('provider', 'openai')
    if provider == 'openai':
        _ = _get_client(api_key)  # presence check
    if provider == 'groq':
        sys = (
            "You are an expert technical interviewer. Score the candidate's single answer strictly. "
            "Return ONLY compact JSON with keys: communication (0-10), technical_knowledge (0-10), "
            "problem_solving (0-10), overall (0-100), strengths (array of short phrases), "
            "weaknesses (array of short phrases), feedback (<=60 words)."
        )
        user = f"Question: {question}\n\nCandidate answer (transcript): {transcript}"
        try:
            content = groq_chat(st.session_state.api_key, messages=[{"role": "system", "content": sys}, {"role": "user", "content": user}])
            try:
                return json.loads(content)
            except Exception:
                return {
                    "communication": 5,
                    "technical_knowledge": 5,
                    "problem_solving": 5,
                    "overall": 50,
                    "strengths": [],
                    "weaknesses": [],
                    "feedback": "",
                }
        except Exception as e:
            return {
                "communication": 5,
                "technical_knowledge": 5,
                "problem_solving": 5,
                "overall": 50,
                "strengths": [],
                "weaknesses": [],
                "feedback": f"Error scoring with Groq: {e}",
            }
    elif provider == 'ollama':
        sys = (
            "You are an expert technical interviewer. Score the candidate's single answer strictly. "
            "Return ONLY compact JSON with keys: communication (0-10), technical_knowledge (0-10), "
            "problem_solving (0-10), overall (0-100), strengths (array of short phrases), "
            "weaknesses (array of short phrases), feedback (<=60 words)."
        )
        user = f"Question: {question}\n\nCandidate answer (transcript): {transcript}"
        try:
            content = ollama_chat(messages=[{"role": "system", "content": sys}, {"role": "user", "content": user}], model=st.session_state.get('ollama_model'), base_url=st.session_state.get('ollama_base_url'))
            try:
                return json.loads(content)
            except Exception:
                return {
                    "communication": 5,
                    "technical_knowledge": 5,
                    "problem_solving": 5,
                    "overall": 50,
                    "strengths": [],
                    "weaknesses": [],
                    "feedback": "",
                }
        except Exception as e:
            return {
                "communication": 5,
                "technical_knowledge": 5,
                "problem_solving": 5,
                "overall": 50,
                "strengths": [],
                "weaknesses": [],
                "feedback": f"Error scoring with Ollama: {e}",
            }
