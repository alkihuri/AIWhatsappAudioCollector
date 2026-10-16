#!/usr/bin/env python3

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def find_whatsapp_audio_dirs(root: Path) -> list[Path]:
	return [p for p in root.rglob("*") if p.is_dir() and p.name == "WhatsApp Audio"]


def collect_opus_files(audio_dirs: list[Path]) -> list[Path]:
	files: list[Path] = []
	for audio_dir in audio_dirs:
		files.extend(p for p in audio_dir.rglob("*.opus") if p.is_file())
	return sorted(files)


def unique_wav_path(output_dir: Path, stem: str) -> Path:
	candidate = output_dir / f"{stem}.wav"
	n = 1
	while candidate.exists():
		candidate = output_dir / f"{stem}_{n}.wav"
		n += 1
	return candidate


def append_transcription(txt_file: Path, name: str, text: str) -> None:
	with txt_file.open("a", encoding="utf-8") as f:
		f.write(f"{name}\nСОДЕРЖАНИЕ:\n{text.strip()}\n\n")


def convert_opus_to_wav(opus_file: Path, wav_file: Path) -> tuple[bool, str]:
	wav_file.parent.mkdir(parents=True, exist_ok=True)

	cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(opus_file), str(wav_file)]

	result = subprocess.run(cmd, capture_output=True, text=True)
	if result.returncode == 0:
		return True, f"OK: {opus_file} -> {wav_file}"

	error_text = (result.stderr or result.stdout or "Unknown ffmpeg error").strip()
	return False, f"FAIL: {opus_file}\n  {error_text}"


def main() -> int:
	parser = argparse.ArgumentParser(
		description=(
			"Search recursively for folders named 'WhatsApp Audio', find all .opus files, "
			"and convert them to .wav using ffmpeg."
		)
	)
	parser.add_argument(
		"root",
		nargs="?",
		default=".",
		help="Root directory to start searching from (default: current directory).",
	)
	parser.add_argument("--model", default="small", help="Whisper model name (default: small).")
	parser.add_argument("--language", default=None, help="Audio language code, e.g. ru (default: auto-detect).")
	args = parser.parse_args()

	root = Path(args.root).expanduser().resolve()
	if not root.exists() or not root.is_dir():
		print(f"Error: root directory does not exist or is not a directory: {root}")
		return 1

	if shutil.which("ffmpeg") is None:
		print("Error: ffmpeg is not installed or not found in PATH.")
		return 1

	try:
		import whisper
	except ImportError:
		print("Error: openai-whisper is not installed. Run: pip install openai-whisper")
		return 1

	print(f"Loading whisper model: {args.model}")
	model = whisper.load_model(args.model)
	txt_file = root / "output.txt"

	output_dir = root / "output"
	if output_dir.exists():
		if output_dir.is_dir():
			shutil.rmtree(output_dir)
		else:
			output_dir.unlink()
	output_dir.mkdir(parents=True, exist_ok=True)
	print(f"Output folder recreated: {output_dir}")

	audio_dirs = find_whatsapp_audio_dirs(root)
	if not audio_dirs:
		print("No folders named 'WhatsApp Audio' were found.")
		return 0

	opus_files = collect_opus_files(audio_dirs)
	print(f"Found 'WhatsApp Audio' folders: {len(audio_dirs)}")
	print(f"Found .opus files: {len(opus_files)}")

	if not opus_files:
		return 0

	success_count = 0
	fail_count = 0

	for i, opus_file in enumerate(opus_files, start=1):
		wav_file = unique_wav_path(output_dir, opus_file.stem)
		print(f"[{i}/{len(opus_files)}] Converting: {opus_file}")
		ok, message = convert_opus_to_wav(opus_file, wav_file)
		print(message)
		if ok:
			success_count += 1
			try:
				result = model.transcribe(str(wav_file), language=args.language)
				append_transcription(txt_file, wav_file.name, result["text"])
			except Exception as exc:
				print(f"TRANSCRIBE FAIL: {wav_file}\n  {exc}")
		else:
			fail_count += 1

	print("\nDone.")
	print(f"Converted successfully: {success_count}")
	print(f"Failed: {fail_count}")

	return 0 if fail_count == 0 else 2


if __name__ == "__main__":
	sys.exit(main())
