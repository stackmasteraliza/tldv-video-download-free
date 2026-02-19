#!/usr/bin/env python3
"""TLDV Video Downloader by Aliza Ali — Download your TLDV meeting recordings."""

import argparse
import sys
from datetime import datetime
import subprocess
import shutil
import requests
import json
import re
import os
import time as time_module

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich.rule import Rule
from rich.prompt import Prompt
from rich import box

console = Console()

VERSION = "2"

# ── Banner ────────────────────────────────────────────────────────────────────

_LOGO = [
    "████████╗██╗     ██████╗ ██╗   ██╗",
    "╚══██╔══╝██║     ██╔══██╗██║   ██║",
    "   ██║   ██║     ██║  ██║██║   ██║",
    "   ██║   ██║     ██║  ██║╚██╗ ██╔╝",
    "   ██║   ███████╗██████╔╝ ╚████╔╝ ",
    "   ╚═╝   ╚══════╝╚═════╝   ╚═══╝  ",
]

# ── Utility functions ─────────────────────────────────────────────────────────


def parse_time_to_seconds(time_str):
    """Parse ffmpeg time string like '00:14:51.95' to total seconds."""
    match = re.match(r"(\d+):(\d+):(\d+)\.(\d+)", time_str)
    if match:
        h, m, s, ms = match.groups()
        return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 100
    return 0


def format_duration(total_seconds):
    """Format seconds into a human-readable string."""
    total_seconds = int(total_seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    return f"{minutes}m {seconds}s"


def format_time_short(seconds):
    """Format seconds to MM:SS or HH:MM:SS."""
    seconds = int(seconds)
    if seconds >= 3600:
        return f"{seconds // 3600}:{(seconds % 3600) // 60:02d}:{seconds % 60:02d}"
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


def get_duration(ffprobe_path, source_url):
    """Get video duration in seconds using ffprobe."""
    try:
        result = subprocess.run(
            [ffprobe_path, "-v", "quiet", "-print_format", "json",
             "-show_format", source_url],
            capture_output=True, text=True, timeout=30
        )
        info = json.loads(result.stdout)
        return float(info.get("format", {}).get("duration", 0))
    except Exception:
        return 0


# ── Progress UI ───────────────────────────────────────────────────────────────


def make_progress_panel(pct, elapsed, speed, eta, current_time, total_time, dl_speed="--", finished=False):
    """Build a rich panel showing the download progress with labeled stats."""
    pct = min(pct, 100.0)
    filled = int(pct / 100 * 50)
    empty = 50 - filled

    if finished:
        bar_str = "[bold green]" + "\u2588" * 50 + "[/bold green]"
        status_text = "[bold green]COMPLETE[/bold green]"
    else:
        bar_str = "[bold blue]" + "\u2588" * filled + "[/bold blue][dim]" + "\u2591" * empty + "[/dim]"
        status_text = "[bold blue]DOWNLOADING[/bold blue]"

    progress_line = f"  {bar_str}  [bold white]{pct:5.1f}%[/bold white]"

    stats_table = Table(box=None, show_header=True, show_edge=False, padding=(0, 2), expand=True)
    stats_table.add_column("Elapsed", style="bold yellow", justify="center", header_style="dim")
    stats_table.add_column("Speed", style="bold magenta", justify="center", header_style="dim")
    stats_table.add_column("Download", style="bold cyan", justify="center", header_style="dim")
    stats_table.add_column("ETA", style="bold green", justify="center", header_style="dim")
    stats_table.add_column("Progress", style="bold white", justify="center", header_style="dim")

    eta_display = eta if eta else "--:--"
    progress_display = f"{current_time} / {total_time}" if total_time != "?" else current_time

    stats_table.add_row(elapsed, speed, dl_speed, eta_display, progress_display)

    content = Group(
        Text(""),
        Text.from_markup(f"  {status_text}"),
        Text(""),
        Text.from_markup(progress_line),
        Text(""),
        stats_table,
        Text(""),
    )

    border = "green" if finished else "blue"
    title_text = "[bold green] Download Complete [/bold green]" if finished else "[bold blue] Downloading Video [/bold blue]"

    return Panel(
        content,
        border_style=border,
        box=box.HEAVY,
        title=title_text,
        title_align="left",
        padding=(0, 1),
    )


def download_video(ffmpeg_path, source_url, output_file, total_duration):
    """Download video with a rich live progress panel."""
    cmd = [ffmpeg_path, "-v", "quiet", "-stats", "-i", source_url,
           "-c", "copy", output_file]

    process = subprocess.Popen(
        cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL,
        universal_newlines=True, bufsize=1
    )

    total_time_str = format_time_short(total_duration) if total_duration > 0 else "?"
    start_time = time_module.time()

    panel = make_progress_panel(0, "00:00", "--.-x", "--:--", "00:00", total_time_str)

    with Live(panel, console=console, refresh_per_second=4, transient=True) as live:
        buffer = ""
        last_size = 0
        last_size_time = start_time
        dl_speed_str = "--"

        while True:
            char = process.stderr.read(1)
            if not char:
                break
            buffer += char
            if char == "\r" or char == "\n":
                line = buffer.strip()
                buffer = ""
                if not line:
                    continue

                time_match = re.search(r"time=(\d+:\d+:\d+\.\d+)", line)
                speed_match = re.search(r"speed=\s*([\d.]+)x", line)
                size_match = re.search(r"size=\s*(\d+)\s*[kK]i?B", line)

                if time_match:
                    current_seconds = parse_time_to_seconds(time_match.group(1))
                    speed_str = f"{speed_match.group(1)}x" if speed_match else "--.-x"

                    elapsed = time_module.time() - start_time
                    elapsed_str = format_time_short(elapsed)

                    pct = (current_seconds / total_duration * 100) if total_duration > 0 else 0
                    current_time_str = format_time_short(current_seconds)

                    if size_match:
                        current_size_kb = int(size_match.group(1))
                        now = time_module.time()
                        dt = now - last_size_time
                        if dt >= 0.5:
                            rate_kbs = (current_size_kb - last_size) / dt
                            last_size = current_size_kb
                            last_size_time = now
                            if rate_kbs >= 1024:
                                dl_speed_str = f"{rate_kbs / 1024:.1f} MB/s"
                            else:
                                dl_speed_str = f"{rate_kbs:.0f} KB/s"

                    if total_duration > 0 and current_seconds > 0:
                        remaining_video = total_duration - current_seconds
                        rate = current_seconds / elapsed if elapsed > 0 else 1
                        eta_seconds = remaining_video / rate if rate > 0 else 0
                        eta_str = format_time_short(eta_seconds)
                    else:
                        eta_str = "--:--"

                    panel = make_progress_panel(
                        pct, elapsed_str, speed_str, eta_str,
                        current_time_str, total_time_str, dl_speed=dl_speed_str
                    )
                    live.update(panel)

        process.wait()

        final_size_kb = 0
        if os.path.exists(output_file):
            final_size_kb = os.path.getsize(output_file) / 1024
        elapsed = time_module.time() - start_time
        elapsed_str = format_time_short(elapsed)
        avg_speed = final_size_kb / elapsed if elapsed > 0 else 0
        if avg_speed >= 1024:
            final_dl = f"{avg_speed / 1024:.1f} MB/s avg"
        else:
            final_dl = f"{avg_speed:.0f} KB/s avg"

        panel = make_progress_panel(
            100, elapsed_str, "---", "00:00",
            total_time_str, total_time_str, dl_speed=final_dl, finished=True
        )
        live.update(panel)
        time_module.sleep(1)

    return process.returncode


# ── Step indicators ───────────────────────────────────────────────────────────


def step(number, total, msg, style="green"):
    console.print(f"  [{style}]\u2502[/{style}]")
    console.print(f"  [{style}]\u251c\u2500[/{style}] [{style}]Step {number}/{total}[/{style}] {msg}")


def step_done(msg):
    console.print(f"  [green]\u2502[/green]  [green]\u2714[/green] {msg}")


def step_warn(msg):
    console.print(f"  [yellow]\u2502[/yellow]  [yellow]\u26a0[/yellow] {msg}")


# ── Configuration helpers ─────────────────────────────────────────────────────


def extract_meeting_id(url):
    """Extract the meeting ID from a TLDV meeting URL."""
    if url.startswith("http"):
        return url.rstrip("/").split("/")[-1]
    return url.strip()


def find_ffmpeg():
    """Locate ffmpeg and ffprobe on the system."""
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        common_paths = []
        if sys.platform == "win32":
            common_paths = [
                os.path.expandvars(r"%LOCALAPPDATA%\Programs\ffmpeg\bin\ffmpeg.exe"),
                os.path.expandvars(r"%ProgramFiles%\ffmpeg\bin\ffmpeg.exe"),
                os.path.expandvars(r"%ProgramFiles(x86)%\ffmpeg\bin\ffmpeg.exe"),
            ]
        else:
            common_paths = [
                "/usr/local/bin/ffmpeg",
                "/usr/bin/ffmpeg",
                "/opt/homebrew/bin/ffmpeg",
            ]
        for path in common_paths:
            if os.path.isfile(path):
                ffmpeg_path = path
                break

    if not ffmpeg_path:
        return None, None

    ffprobe_path = shutil.which("ffprobe")
    if not ffprobe_path:
        ffmpeg_dir = os.path.dirname(ffmpeg_path)
        ext = ".exe" if sys.platform == "win32" else ""
        candidate = os.path.join(ffmpeg_dir, f"ffprobe{ext}")
        ffprobe_path = candidate if os.path.isfile(candidate) else None

    return ffmpeg_path, ffprobe_path


# ── Banner & UI ───────────────────────────────────────────────────────────────


def show_banner():
    """Display the application banner."""
    console.clear()
    console.print()
    for line in _LOGO:
        console.print(f"  [bold cyan]{line}[/bold cyan]")
    console.print()
    console.print(f"  [dim]Video Downloader v{VERSION}[/dim]")
    console.print(f"  [dim]     By[/dim] [bold cyan]Aliza Ali[/bold cyan]")
    console.print()
    console.print(Rule(style="cyan"))
    console.print()


# ── CLI argument parsing ──────────────────────────────────────────────────────


def parse_args():
    parser = argparse.ArgumentParser(
        description="TLDV Video Downloader by Aliza Ali — download meeting recordings with transcripts.",
        epilog="Example: python tldv.py --url https://tldv.io/app/meetings/abc123 --token 'Bearer eyJ...'",
    )
    parser.add_argument("-u", "--url", help="TLDV meeting URL")
    parser.add_argument("-t", "--token", help="Authorization token (Bearer token from browser dev tools)")
    parser.add_argument("-o", "--output-dir", default=".", help="Directory to save files (default: current directory)")
    parser.add_argument("--ffmpeg", help="Path to ffmpeg binary (auto-detected if omitted)")
    parser.add_argument("--ffprobe", help="Path to ffprobe binary (auto-detected if omitted)")
    return parser.parse_args()


def get_config(args):
    """Build config from CLI args → env vars → interactive prompts."""

    # ── Meeting URL ───────────────────────────────────────────────────────
    url = args.url or os.environ.get("TLDV_URL")
    if not url:
        console.print("  [bold cyan]Enter meeting details[/bold cyan]")
        console.print()
        url = Prompt.ask("  [cyan]Meeting URL[/cyan]")

    # ── Auth token ────────────────────────────────────────────────────────
    token = args.token or os.environ.get("TLDV_TOKEN")
    if not token:
        console.print()
        token = Prompt.ask("  [cyan]Bearer token[/cyan]")

    token = token.strip()
    if not token.lower().startswith("bearer "):
        token = f"Bearer {token}"

    # ── FFmpeg / FFprobe ──────────────────────────────────────────────────
    ffmpeg_path = args.ffmpeg or os.environ.get("FFMPEG_PATH")
    ffprobe_path = args.ffprobe or os.environ.get("FFPROBE_PATH")

    if not ffmpeg_path:
        ffmpeg_path, auto_ffprobe = find_ffmpeg()
        if not ffprobe_path:
            ffprobe_path = auto_ffprobe

    if not ffmpeg_path:
        console.print()
        console.print(Panel(
            "[bold red]FFmpeg not found![/bold red]\n\n"
            "Install FFmpeg and make sure it's on your PATH:\n"
            "  [cyan]Windows:[/cyan]  winget install ffmpeg\n"
            "  [cyan]macOS:[/cyan]    brew install ffmpeg\n"
            "  [cyan]Linux:[/cyan]    sudo apt install ffmpeg\n\n"
            "Or provide the path with [bold]--ffmpeg /path/to/ffmpeg[/bold]",
            border_style="red",
            box=box.HEAVY,
            title="[bold red] Missing Dependency [/bold red]",
            title_align="left",
        ))
        sys.exit(1)

    if not ffprobe_path:
        ffprobe_path = ffmpeg_path

    # ── Output directory ──────────────────────────────────────────────────
    output_dir = args.output_dir
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    return {
        "url": url,
        "token": token,
        "ffmpeg": ffmpeg_path,
        "ffprobe": ffprobe_path,
        "output_dir": output_dir,
    }


# ── Main ──────────────────────────────────────────────────────────────────────


def main():
    args = parse_args()
    show_banner()
    config = get_config(args)

    meeting_id = extract_meeting_id(config["url"])
    console.print()

    # ── Step 1: Fetch metadata ────────────────────────────────────────────
    step(1, 3, "[bold]Fetching meeting metadata...[/bold]", "cyan")

    with console.status("  [dim]Connecting to TLDV servers...[/dim]", spinner="dots"):
        data = requests.get(
            f"https://gw.tldv.io/v1/meetings/{meeting_id}/watch-page",
            headers={"Authorization": config["token"]},
        )

    if data.status_code == 401:
        console.print()
        console.print(Panel(
            "[bold red]Authentication failed![/bold red]\n\n"
            "[dim]Your token may be expired or invalid.\n"
            "Get a fresh token from your browser developer tools (F12 → Network tab).[/dim]",
            border_style="red", box=box.HEAVY,
            title="[bold red] Auth Error (401) [/bold red]", title_align="left",
        ))
        sys.exit(1)

    if data.status_code == 404:
        console.print()
        console.print(Panel(
            "[bold red]Meeting not found![/bold red]\n\n"
            f"[dim]Meeting ID: {meeting_id}\n"
            "Check that the URL is correct and you have access to this meeting.[/dim]",
            border_style="red", box=box.HEAVY,
            title="[bold red] Not Found (404) [/bold red]", title_align="left",
        ))
        sys.exit(1)

    try:
        response = json.loads(data.text)

        meeting = response.get("meeting", {})
        name = meeting.get("name", "No name")
        createdAt = meeting.get("createdAt", datetime.now().isoformat())
        source = response.get("video", {}).get("source", None)

        if not source:
            console.print()
            console.print(Panel(
                "[bold red]No video source found![/bold red]\n\n"
                "[dim]The meeting may still be processing or the video is unavailable.[/dim]",
                border_style="red", box=box.HEAVY,
                title="[bold red] Error [/bold red]", title_align="left",
            ))
            sys.exit(1)

        date = datetime.fromisoformat(createdAt.replace("Z", "+00:00"))
        normalised_date = date.strftime("%Y-%m-%d-%H-%M-%S")
        display_date = date.strftime("%b %d, %Y  %I:%M %p")

        safe_name = re.sub(r'[<>:"/\\|?*]', '-', name)
        filename = f"{normalised_date}_{safe_name}"
        output_file = os.path.join(config["output_dir"], f"{filename}.mp4")

        # Get total duration via ffprobe
        with console.status("  [dim]Probing video duration...[/dim]", spinner="dots"):
            total_duration = get_duration(config["ffprobe"], source)

        step_done("Metadata fetched successfully")

        # ── Meeting info card ─────────────────────────────────────────────
        duration_str = format_duration(total_duration) if total_duration > 0 else "Unknown"

        info_table = Table(box=None, show_header=False, show_edge=False, padding=(0, 1))
        info_table.add_column("Key", style="dim cyan", width=14)
        info_table.add_column("Value", style="white")
        info_table.add_row("  Meeting", f"[bold bright_white]{name}[/bold bright_white]")
        info_table.add_row("  Date", display_date)
        info_table.add_row("  Duration", f"[bold]{duration_str}[/bold]" if total_duration > 0 else "[dim]Unknown[/dim]")
        info_table.add_row("  Meeting ID", f"[dim]{meeting_id}[/dim]")
        info_table.add_row("  Output", f"[dim]{os.path.basename(output_file)}[/dim]")

        console.print()
        console.print(Panel(
            info_table,
            border_style="bright_blue", box=box.HEAVY,
            title="[bold bright_blue] Meeting Info [/bold bright_blue]",
            title_align="left", padding=(1, 1),
        ))

        # ── Step 2: Save files ────────────────────────────────────────────
        step(2, 3, "[bold]Saving meeting data...[/bold]", "cyan")

        json_filename = os.path.join(config["output_dir"], f"{filename}.json")
        with open(json_filename, "w") as f:
            f.write(data.text)
        step_done(f"Metadata  \u2192  [bold]{os.path.basename(json_filename)}[/bold]")

        transcript_data = response.get("video", {}).get("transcript", {}).get("data", [])
        transcript_filename = None

        if transcript_data:
            transcript_filename = os.path.join(config["output_dir"], f"{filename}_transcript.txt")
            with open(transcript_filename, "w", encoding="utf-8") as f:
                for segment in transcript_data:
                    if not segment:
                        continue
                    first_word = segment[0]
                    speaker = first_word.get("speaker", "Unknown")
                    start_time = first_word.get("startTime", {})
                    seconds_total = int(start_time.get("seconds", 0))
                    minutes = seconds_total // 60
                    seconds = seconds_total % 60
                    timestamp = f"{minutes:02d}:{seconds:02d}"
                    text = " ".join(word.get("word", "") for word in segment)
                    f.write(f"[{timestamp}] {speaker}: {text}\n")
            step_done(f"Transcript \u2192  [bold]{os.path.basename(transcript_filename)}[/bold]")
        else:
            step_warn("No transcript available for this meeting")

        # ── Step 3: Download video ────────────────────────────────────────
        step(3, 3, "[bold]Downloading video...[/bold]", "cyan")
        console.print("  [green]\u2502[/green]")
        console.print()

        return_code = download_video(config["ffmpeg"], source, output_file, total_duration)

        if return_code == 0 and os.path.exists(output_file):
            file_size_mb = os.path.getsize(output_file) / (1024 * 1024)

            files_table = Table(box=None, show_header=True, show_edge=False, padding=(0, 2), expand=True)
            files_table.add_column("Type", style="dim", width=12, header_style="dim bold")
            files_table.add_column("File", style="bold white", header_style="dim bold")
            files_table.add_column("Size", style="dim", justify="right", header_style="dim bold")

            files_table.add_row("[bold cyan]Video[/bold cyan]", os.path.basename(output_file), f"{file_size_mb:.1f} MB")
            files_table.add_row("[bold yellow]Metadata[/bold yellow]", os.path.basename(json_filename), f"{os.path.getsize(json_filename) / 1024:.0f} KB")
            if transcript_filename:
                files_table.add_row("[bold magenta]Transcript[/bold magenta]", os.path.basename(transcript_filename), f"{os.path.getsize(transcript_filename) / 1024:.0f} KB")

            console.print()
            console.print(Panel(
                Group(
                    Text(""),
                    Text.from_markup("  [bold green]\u2714 All tasks completed successfully![/bold green]"),
                    Text(""),
                    files_table,
                    Text(""),
                ),
                border_style="green", box=box.HEAVY,
                title="[bold green] Download Complete [/bold green]",
                title_align="left",
                subtitle=f"[dim]Files saved to {os.path.abspath(config['output_dir'])}[/dim]",
                subtitle_align="right",
                padding=(0, 1),
            ))
            console.print()
        else:
            console.print()
            console.print(Panel(
                f"[bold red]ffmpeg exited with code {return_code}[/bold red]\n"
                "[dim]Try running the ffmpeg command manually to see detailed errors.[/dim]",
                border_style="red", box=box.HEAVY,
                title="[bold red] Error [/bold red]", title_align="left",
            ))
            sys.exit(1)

    except Exception as e:
        console.print()
        console.print(Panel(
            f"[bold red]{e}[/bold red]\n\n[dim]{data.text[:300]}[/dim]",
            border_style="red", box=box.HEAVY,
            title="[bold red] Error [/bold red]", title_align="left",
        ))
        sys.exit(1)


if __name__ == "__main__":
    main()
