Here is a concise, professional English version of the `README.md`.

---

# 🎙️ WhatsApp Audio AI Pipeline

An automated tool designed to transform WhatsApp voice messages into structured text, optimized for Large Language Model (LLM) analysis.

## 🤖 AI Workflow

This script acts as the first stage of a two-step AI data pipeline:

1.  **Speech-to-Text (STT) — [OpenAI Whisper](https://github.com/openai/whisper):** 
    The script recursively scans for WhatsApp audio folders, converts `.opus` files to `.wav` using FFmpeg, and uses Whisper to generate high-accuracy transcriptions.
2.  **Text Analysis — [Qwen LLM](https://github.com/QwenLM/Qwen) (Planned):** 
    The resulting `output.txt` is formatted specifically to be fed into **Qwen**. This allows for automated summarization, intent detection, and key information extraction from your voice notes.

## ✨ Features

*   **Auto-Discovery:** Recursively finds all `WhatsApp Audio` directories.
*   **Format Conversion:** seamless `.opus` $\rightarrow$ `.wav` conversion via FFmpeg.
*   **LLM-Ready Output:** Generates a clean, unified text file perfect for LLM context windows.
*   **Configurable:** Choose Whisper model sizes (`tiny` to `large`) and specify languages.

## 🛠️ Setup

### Dependencies
1.  **FFmpeg:** Must be installed and added to your PATH.
2.  **Python Packages:**
    ```bash
    pip install openai-whisper torch
    ```

## 🚀 Usage

Run the script by pointing it to your WhatsApp backup directory:

```bash
# Basic usage (current directory)
python converter.py

# Specify path and use a larger model for better accuracy
python converter.py /path/to/backup --model medium --language ru
```

### Arguments
*   `root`: (Optional) The directory to start searching from.
*   `--model`: Whisper model name (default: `small`).
*   `--language`: ISO language code (e.g., `en`, `ru`). If omitted, auto-detection is used.

## 📁 Output
*   `/output/`: Directory containing converted `.wav` files.
*   `output.txt`: The final transcription file containing all text, ready for **Qwen** analysis.
