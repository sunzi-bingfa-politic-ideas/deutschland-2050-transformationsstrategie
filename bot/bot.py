#!/usr/bin/env python3
"""
Reform-Twitter-Bot
==================

Liest Inhalte aus dem Deutschland-2050-Repo, waehlt zufaellig ein Thema,
generiert einen Tweet oder Thread via LLM, und postet ihn auf X/Twitter.

Verwendung:
  python bot/bot.py                    # Generiert + postet
  python bot/bot.py --dry-run          # Nur generieren, nicht posten
  python bot/bot.py --topic Rente      # Bestimmtes Thema erzwingen
  python bot/bot.py --thread           # Thread erzwingen
  python bot/bot.py --single           # Einzeltweet erzwingen

Umgebungsvariablen:
  TWITTER_API_KEY, TWITTER_API_SECRET,
  TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET
  ANTHROPIC_API_KEY  (oder OPENAI_API_KEY)
"""

import os
import sys
import random
import argparse
import yaml
from pathlib import Path

# Bot-Verzeichnis als Basis
BOT_DIR = Path(__file__).parent
REPO_ROOT = BOT_DIR.parent
CONFIG_PATH = BOT_DIR / "config.yaml"


def load_config() -> dict:
    """Laedt die Bot-Konfiguration."""
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def discover_content(config: dict) -> list:
    """Entdeckt alle verfuegbaren Themen und Dateien."""
    topics = []
    for source in config["content_sources"]:
        source_path = REPO_ROOT / source["path"]
        if not source_path.exists():
            continue
        md_files = list(source_path.glob("*.md"))
        if md_files:
            topics.append({
                "label": source["label"],
                "hashtags": source["hashtags"],
                "files": md_files,
            })
    return topics


def select_content(topics: list, forced_topic: str = None) -> tuple:
    """Waehlt zufaellig ein Thema und eine Datei, liest einen Ausschnitt."""
    if forced_topic:
        matching = [t for t in topics if forced_topic.lower() in t["label"].lower()]
        if matching:
            topic = matching[0]
        else:
            print(f"Thema '{forced_topic}' nicht gefunden. Verfuegbar: "
                  f"{[t['label'] for t in topics]}")
            sys.exit(1)
    else:
        topic = random.choice(topics)

    md_file = random.choice(topic["files"])
    content = md_file.read_text(encoding="utf-8")

    # Zufaelligen Abschnitt waehlen (nicht den ganzen File)
    sections = content.split("\n## ")
    if len(sections) > 1:
        # Ueberspringe den Header, waehle einen zufaelligen Abschnitt
        section = random.choice(sections[1:])
        # Begrenze auf ~2000 Zeichen (LLM-Input)
        section = section[:2000]
    else:
        section = content[:2000]

    return topic, md_file.name, section


def generate_tweet_anthropic(prompt: str, config: dict) -> str:
    """Generiert Tweet-Text mit Claude API."""
    try:
        import anthropic
    except ImportError:
        print("FEHLER: 'anthropic' Paket nicht installiert. Bitte: pip install anthropic")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    llm_config = config["llm"]

    response = client.messages.create(
        model=llm_config["model"],
        max_tokens=llm_config["max_tokens"],
        temperature=llm_config["temperature"],
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


def generate_tweet_openai(prompt: str, config: dict) -> str:
    """Generiert Tweet-Text mit OpenAI API."""
    try:
        from openai import OpenAI
    except ImportError:
        print("FEHLER: 'openai' Paket nicht installiert. Bitte: pip install openai")
        sys.exit(1)

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    llm_config = config["llm"]

    response = client.chat.completions.create(
        model=llm_config["model"],
        max_tokens=llm_config["max_tokens"],
        temperature=llm_config["temperature"],
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()


def generate_tweet(prompt: str, config: dict) -> str:
    """Generiert Tweet via konfiguriertem LLM-Provider."""
    provider = config["llm"]["provider"]
    if provider == "anthropic":
        return generate_tweet_anthropic(prompt, config)
    elif provider == "openai":
        return generate_tweet_openai(prompt, config)
    else:
        raise ValueError(f"Unbekannter LLM-Provider: {provider}")


def format_tweets(raw_text: str, topic: dict, config: dict, is_thread: bool) -> list:
    """Formatiert generierte Tweets mit Hashtags."""
    global_tags = " ".join(config["global_hashtags"])
    topic_tags = " ".join(random.sample(topic["hashtags"], min(2, len(topic["hashtags"]))))
    hashtag_str = f"{topic_tags} {global_tags}"

    if config["tweet"]["include_repo_link"]:
        link = f"\n{config['tweet']['repo_url']}"
    else:
        link = ""

    if is_thread:
        tweets = [t.strip() for t in raw_text.split("---") if t.strip()]
        # Hashtags nur am letzten Tweet
        if tweets:
            tweets[-1] = f"{tweets[-1]}\n\n{hashtag_str}{link}"
        return tweets
    else:
        return [f"{raw_text}\n\n{hashtag_str}{link}"]


def post_to_twitter(tweets: list, dry_run: bool = False):
    """Postet Tweet(s) auf X/Twitter."""
    if dry_run:
        print("\n=== DRY RUN (nicht gepostet) ===\n")
        for i, tweet in enumerate(tweets):
            print(f"--- Tweet {i+1}/{len(tweets)} ({len(tweet)} Zeichen) ---")
            print(tweet)
            print()
        return

    try:
        import tweepy
    except ImportError:
        print("FEHLER: 'tweepy' Paket nicht installiert. Bitte: pip install tweepy")
        sys.exit(1)

    client = tweepy.Client(
        consumer_key=os.environ["TWITTER_API_KEY"],
        consumer_secret=os.environ["TWITTER_API_SECRET"],
        access_token=os.environ["TWITTER_ACCESS_TOKEN"],
        access_token_secret=os.environ["TWITTER_ACCESS_SECRET"],
    )

    previous_id = None
    for i, tweet in enumerate(tweets):
        try:
            if previous_id:
                response = client.create_tweet(
                    text=tweet, in_reply_to_tweet_id=previous_id
                )
            else:
                response = client.create_tweet(text=tweet)
            previous_id = response.data["id"]
            print(f"Tweet {i+1}/{len(tweets)} gepostet (ID: {previous_id})")
        except Exception as e:
            print(f"FEHLER beim Posten von Tweet {i+1}: {e}")
            break


def main():
    parser = argparse.ArgumentParser(description="Reform-Twitter-Bot")
    parser.add_argument("--dry-run", action="store_true",
                        help="Nur generieren, nicht posten")
    parser.add_argument("--topic", type=str, default=None,
                        help="Thema erzwingen (z.B. 'Rente', 'Sicherheit')")
    parser.add_argument("--thread", action="store_true",
                        help="Thread erzwingen")
    parser.add_argument("--single", action="store_true",
                        help="Einzeltweet erzwingen")
    args = parser.parse_args()

    # Config laden
    config = load_config()

    # Inhalte entdecken
    topics = discover_content(config)
    if not topics:
        print("FEHLER: Keine Themen gefunden!")
        sys.exit(1)

    print(f"Gefunden: {len(topics)} Themen mit "
          f"{sum(len(t['files']) for t in topics)} Dateien")

    # Thema + Inhalt waehlen
    topic, filename, content = select_content(topics, args.topic)
    print(f"Gewaehltes Thema: {topic['label']} ({filename})")

    # Thread oder Einzeltweet?
    if args.thread:
        is_thread = True
    elif args.single:
        is_thread = False
    else:
        is_thread = random.random() < config["tweet"]["thread_probability"]

    print(f"Format: {'Thread' if is_thread else 'Einzeltweet'}")

    # Prompt bauen
    from prompts import SINGLE_TWEET_PROMPT, THREAD_PROMPT

    if is_thread:
        thread_length = random.randint(3, config["tweet"]["thread_max_posts"])
        prompt = THREAD_PROMPT.format(
            topic=topic["label"],
            content=content,
            thread_length=thread_length,
        )
    else:
        prompt = SINGLE_TWEET_PROMPT.format(
            topic=topic["label"],
            content=content,
        )

    # Tweet generieren
    print("Generiere Tweet...")
    if args.dry_run and not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY")):
        print("[Kein API-Key gesetzt — zeige Prompt statt generierten Tweet]\n")
        raw_tweet = f"[DEMO] Thema: {topic['label']} | Datei: {filename} | Modus: {'Thread' if is_thread else 'Einzeltweet'}"
    else:
        raw_tweet = generate_tweet(prompt, config)

    # Formatieren
    tweets = format_tweets(raw_tweet, topic, config, is_thread)

    # Posten (oder Dry Run)
    post_to_twitter(tweets, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
