from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

def generate_feed(show: dict, episodes: list[dict]) -> str:
    fg = FeedGenerator()
    fg.load_extension("podcast")

    fg.title(show["title"])
    fg.description(show["description"] or "")
    fg.link(href=show["base_url"], rel="alternate")
    fg.author({"name": show["author"] or ""})
    fg.language("en")
    if show["image_url"]:
        fg.image(show["image_url"])
        fg.podcast.itunes_image(show["image_url"])
    fg.podcast.itunes_category("Technology")
    fg.podcast.itunes_author(show["author"] or "")
    fg.podcast.itunes_explicit("no")

    for ep in episodes:
        if not ep["published"]:
            continue
        fe = fg.add_entry()
        fe.id(str(ep["id"]))
        fe.title(ep["title"])
        fe.description(ep["description"] or "")
        pub_dt = datetime.fromisoformat(ep["pub_date"]).replace(tzinfo=timezone.utc)
        fe.pubDate(pub_dt)
        audio_url = f"{show['base_url']}/audio/{ep['id']}"
        fe.enclosure(audio_url, str(ep["file_size"]), "audio/mpeg")
        fe.podcast.itunes_duration(int(ep["duration_seconds"]))

    return fg.rss_str(pretty=True).decode("utf-8")
