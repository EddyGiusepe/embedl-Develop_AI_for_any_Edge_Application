#! /usr/bin/env python3
"""
Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro

Script download_images_and_videos.py
=====================================
This script downloads images and videos of vehicle license
plates using DuckDuckGo Search. These images will be used
in our application, where the 'embedl/Cosmos-Reason2-2B-W4A16'
template will provide a description of the vehicle's license
plate, either as an image or video.

This script runs from the command line (CLI) using Typer.


RUN
---
uv run download_images_and_videos.py --images-count 5 --videos-count 5

"""

import logging
import time
from pathlib import Path
from typing import Annotated

import httpx
import typer
import yt_dlp
from ddgs import DDGS
from PIL import Image, UnidentifiedImageError

logger = logging.getLogger(__name__)
# ─── Configurações ────────────────────────────────────────────────────────────

OUTPUT_DIR_IMAGES = Path(__file__).parent.parent / "data/images"
OUTPUT_DIR_VIDEOS = Path(__file__).parent.parent / "data/videos"

MIN_WIDTH = 300
MIN_HEIGHT = 100
TIMEOUT_SECONDS = 10

ASPECT_RATIO_RANGE = (1.2, 7.0)

IMAGE_SEARCH_TERMS = [
    # "vehicle license plate",
    "shows the vehicle with its license plate.",
]

VIDEO_SEARCH_TERMS = [
    # "car license plate close up short video",
    "Vehicles with license plates",
]

DEFAULT_MAX_DURATION = 60  # segundos
MINUTES_SECONDS_PARTS = 2
HOURS_MINUTES_SECONDS_PARTS = 3

# ─── Typer App ────────────────────────────────────────────────────────────────

EXAMPLES = """
[bold]Examples:[/bold]

  [dim]# Download 5 images (default)[/dim]
  uv run download_images_and_videos.py images

  [dim]# Download 10 images[/dim]
  uv run download_images_and_videos.py images --count 10

  [dim]# Download 3 short videos (max 30 seconds)[/dim]
  uv run download_images_and_videos.py videos --count 3 --max-duration 30

  [dim]# Download images and videos together[/dim]
  uv run download_images_and_videos.py all --images-count 5 --videos-count 3

  [dim]# Download very short videos (max 20 seconds)[/dim]
  uv run download_images_and_videos.py videos -c 5 -d 20
"""

app = typer.Typer(
    help="Download images and videos of vehicle license plates.",
    add_completion=False,
    rich_markup_mode="rich",
    epilog=EXAMPLES,
)

# ─── Image Helpers ────────────────────────────────────────────────────────────


def collect_image_urls(limit: int) -> list[str]:
    """
    Collect up to `limit` unique image URLs via DuckDuckGo.
    """
    urls: list[str] = []
    seen: set[str] = set()

    with DDGS() as ddgs:
        for term in IMAGE_SEARCH_TERMS:
            if len(urls) >= limit:
                break
            needed = limit - len(urls)
            logger.info(f"Searching for images: '{term}' ({needed} slots remaining)...")
            try:
                results = ddgs.images(query=term, max_results=needed)
                for r in results:
                    url = r.get("image", "")
                    if url and url not in seen:
                        seen.add(url)
                        urls.append(url)
                    if len(urls) >= limit:
                        break
            except Exception as exc:
                logger.warning(f"Warning: error searching for '{term}': {exc}")
            time.sleep(3)

    return urls


def validate_image(path: Path) -> tuple[bool, str]:
    """
    Validate minimum dimensions and aspect ratio of the image.
    """
    try:
        with Image.open(path) as img:
            w, h = img.size
            if w < MIN_WIDTH or h < MIN_HEIGHT:
                return False, f"Too small ({w}x{h} pixels)"
            ratio = w / h
            lo, hi = ASPECT_RATIO_RANGE
            if not (lo <= ratio <= hi):
                return False, f"Aspect ratio {ratio:.2f} outside standard ({lo}-{hi})"
            return True, ""
    except (UnidentifiedImageError, Exception) as exc:
        return False, f"Corrupted: {exc}"


def download_images_until_full(urls: list[str], target: int) -> int:
    """
    Download images until the target number of valid images is reached.
    """
    OUTPUT_DIR_IMAGES.mkdir(parents=True, exist_ok=True)

    saved = 0
    for idx, url in enumerate(urls, start=1):
        if saved >= target:
            break

        dest = OUTPUT_DIR_IMAGES / f"plate_{saved + 1:03d}.jpg"
        print(f"  [{idx}/{len(urls)}] {url[:75]}...")

        try:
            with httpx.Client(timeout=TIMEOUT_SECONDS, follow_redirects=True) as client:
                response = client.get(url)
                response.raise_for_status()
                dest.write_bytes(response.content)

            valid, reason = validate_image(dest)
            if not valid:
                logger.warning(f"Discarded: {reason}.")
                dest.unlink(missing_ok=True)
                continue

            saved += 1
            logger.info(f"Saved: {dest.name}  ({saved}/{target})")

        except httpx.HTTPStatusError as exc:
            logger.warning(f"HTTP {exc.response.status_code} — skipping.")
        except httpx.RequestError as exc:
            logger.warning(f"Connection error: {exc} — skipping.")
        except Exception as exc:
            logger.error(f"Error: {exc} — skipping.")

    return saved


# ─── Video Helpers ────────────────────────────────────────────────────────────


def parse_duration_string(duration_str: str) -> int | None:
    """
    Convert duration string (e.g. "0:45", "1:30", "2:15:00") to seconds.
    Return None if parsing fails.
    """
    if not duration_str:
        return None
    try:
        parts = duration_str.split(":")
        if len(parts) == MINUTES_SECONDS_PARTS:
            minutes, seconds = int(parts[0]), int(parts[1])
            return minutes * 60 + seconds
        elif len(parts) == HOURS_MINUTES_SECONDS_PARTS:
            hours, minutes, seconds = int(parts[0]), int(parts[1]), int(parts[2])
            return hours * 3600 + minutes * 60 + seconds
        else:
            return None
    except (ValueError, AttributeError):
        return None


def collect_video_urls(limit: int, max_duration: int = DEFAULT_MAX_DURATION) -> list[dict]:
    """
    Collect up to `limit` video URLs via DuckDuckGo.
    Filter by maximum duration.
    Return list of dicts with 'url', 'title' and 'duration'.
    """
    videos: list[dict] = []
    seen: set[str] = set()

    with DDGS() as ddgs:
        for term in VIDEO_SEARCH_TERMS:
            if len(videos) >= limit:
                break
            needed = limit - len(videos)
            logger.info(f"Searching for videos: '{term}' ({needed} slots remaining)...")
            try:
                results = ddgs.videos(query=term, max_results=needed * 4)
                for r in results:
                    url = r.get("content", "")
                    title = r.get("title", "video")
                    duration_str = r.get("duration", "")
                    duration_sec = parse_duration_string(duration_str)

                    if url and url not in seen:
                        if duration_sec is not None and duration_sec > max_duration:
                            logger.warning(f"Skipping (duration {duration_str} > {max_duration}s): {title[:50]}...")
                            continue

                        seen.add(url)
                        videos.append(
                            {
                                "url": url,
                                "title": title,
                                "duration": duration_sec,
                                "duration_str": duration_str,
                            }
                        )
                    if len(videos) >= limit:
                        break
            except Exception as exc:
                logger.warning(f"Warning: error searching for '{term}': {exc}")
            time.sleep(3)

    return videos


def get_video_duration(url: str) -> int | None:
    """
    Get the actual duration of the video using yt-dlp (without downloading).
    Return duration in seconds or None if fails.
    """
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": 15,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info and "duration" in info:
                return int(info["duration"])
    except Exception:
        pass
    return None


def download_single_video(url: str, output_path: Path, max_duration: int = DEFAULT_MAX_DURATION) -> tuple[bool, str]:
    """
    Download a single video using yt-dlp.
    Validate duration before downloading.
    Return (success, message).
    """
    logger.info("Checking duration...")
    actual_duration = get_video_duration(url)

    if actual_duration is not None:
        if actual_duration > max_duration:
            return False, f"Too long ({actual_duration}s > {max_duration}s)"
        logger.info(f"Duration: {actual_duration}s (OK)")

    ydl_opts = {
        "format": "best[ext=mp4]/best",
        "outtmpl": str(output_path),
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": 30,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        if output_path.exists():
            return True, "OK"
        return False, "File not created."
    except Exception as exc:
        return False, str(exc)


def download_videos_until_full(video_list: list[dict], target: int, max_duration: int = DEFAULT_MAX_DURATION) -> int:
    """
    Download videos until the target number of valid videos is reached.
    Filter by maximum duration.
    """
    OUTPUT_DIR_VIDEOS.mkdir(parents=True, exist_ok=True)

    saved = 0
    for idx, video in enumerate(video_list, start=1):
        if saved >= target:
            break

        url = video["url"]
        title = video.get("title", "")[:40]
        duration_str = video.get("duration_str", "?")
        dest = OUTPUT_DIR_VIDEOS / f"plate_{saved + 1:03d}.mp4"

        logger.info(f"[{idx}/{len(video_list)}] ({duration_str}) {title}...")
        logger.info(f"URL: {url[:60]}...")

        try:
            success, message = download_single_video(url, dest, max_duration)
            if success:
                saved += 1
                logger.info(f"Saved: {dest.name}  ({saved}/{target})")
            else:
                logger.warning(f"Discarded: {message}")
                dest.unlink(missing_ok=True)
        except Exception as exc:
            print(f"Error: {exc}")
            dest.unlink(missing_ok=True)

    return saved


# ─── CLI Commands ─────────────────────────────────────────────────────────────


@app.command()
def images(
    count: Annotated[int, typer.Option("--count", "-c", help="Number of images")] = 5,
) -> None:
    """
    Download only images of vehicle license plates.
    """
    logger.info("DOWNLOADING IMAGES OF VEHICLE LICENSE PLATES")

    url_budget = count * 2
    logger.info(f"Collecting up to {url_budget} candidate URLs...\n")
    urls = collect_image_urls(url_budget)

    if not urls:
        logger.error("No URL found. Check your connection.")
        raise typer.Exit(1)

    logger.info(f"\n{len(urls)} URLs collected. Downloading up to {count} valid images...\n")
    saved = download_images_until_full(urls, target=count)

    status = "OK" if saved >= count else f"PARTIAL ({saved}/{count})"
    logger.info(f"\n[{status}] Images in: {OUTPUT_DIR_IMAGES}")


@app.command()
def videos(
    count: Annotated[int, typer.Option("--count", "-c", help="Number of videos")] = 5,
    max_duration: Annotated[
        int, typer.Option("--max-duration", "-d", help="Maximum duration in seconds")
    ] = DEFAULT_MAX_DURATION,
) -> None:
    """
    Download only videos of vehicle license plates.
    """
    logger.info("DOWNLOADING VIDEOS OF VEHICLE LICENSE PLATES")
    logger.info(f"Maximum duration: {max_duration} seconds")

    url_budget = count * 5
    logger.info(f"Collecting up to {url_budget} candidate URLs (filter: ≤{max_duration}s)...\n")
    video_list = collect_video_urls(url_budget, max_duration=max_duration)

    if not video_list:
        logger.error("No video URL found. Check your connection.")
        raise typer.Exit(1)

    logger.info(f"\n{len(video_list)} URLs collected. Downloading up to {count} videos...\n")
    saved = download_videos_until_full(video_list, target=count, max_duration=max_duration)

    status = "OK" if saved >= count else f"PARTIAL ({saved}/{count})"
    logger.info(f"\n[{status}] Videos in: {OUTPUT_DIR_VIDEOS}")


@app.command(name="all")
def download_all(
    images_count: Annotated[int, typer.Option("--images-count", "-i", help="Number of images")] = 5,
    videos_count: Annotated[int, typer.Option("--videos-count", "-v", help="Number of videos")] = 5,
    max_duration: Annotated[
        int, typer.Option("--max-duration", "-d", help="Maximum duration of videos in seconds")
    ] = DEFAULT_MAX_DURATION,
) -> None:
    """
    Download images and videos of vehicle license plates.
    """
    logger.info("COMPLETE DOWNLOAD: IMAGES + VIDEOS")
    logger.info(f"Maximum duration of videos: {max_duration} seconds")

    # Download images:
    logger.info("\n--- IMAGES ---\n")
    url_budget = images_count * 2
    logger.info(f"Collecting up to {url_budget} image URLs...\n")
    img_urls = collect_image_urls(url_budget)

    if img_urls:
        logger.info(f"\n{len(img_urls)} URLs collected. Downloading up to {images_count} images...\n")
        saved_images = download_images_until_full(img_urls, target=images_count)
        status_img = "OK" if saved_images >= images_count else f"PARTIAL ({saved_images}/{images_count})"
        logger.info(f"\n[{status_img}] Images in: {OUTPUT_DIR_IMAGES}")
    else:
        logger.error("No image URL found.")
        saved_images = 0

    # Download videos:
    logger.info("\n--- VIDEOS ---\n")
    url_budget = videos_count * 5
    logger.info(f"Collecting up to {url_budget} video URLs (filter: ≤{max_duration}s)...\n")
    video_list = collect_video_urls(url_budget, max_duration=max_duration)

    if video_list:
        logger.info(f"\n{len(video_list)} URLs collected. Downloading up to {videos_count} videos...\n")
        saved_videos = download_videos_until_full(video_list, target=videos_count, max_duration=max_duration)
        status_vid = "OK" if saved_videos >= videos_count else f"PARTIAL ({saved_videos}/{videos_count})"
        logger.info(f"\n[{status_vid}] Videos in: {OUTPUT_DIR_VIDEOS}")
    else:
        logger.error("No video URL found.")

        saved_videos = 0

    # Final summary:
    logger.info("FINAL SUMMARY:")
    logger.info(f"Downloaded images: {saved_images}/{images_count}")
    logger.info(f"Downloaded videos:  {saved_videos}/{videos_count}")


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app()
