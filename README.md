![](images/banner.jpeg)

# Emby MDBList Collection Creator — Home Assistant Add-on

A Home Assistant add-on that syncs [MDBList.com](https://mdblist.com/) lists to [Emby](https://emby.media/) collections, with a built-in Web UI for configuration and monitoring.

> **Based on [Emby-MDBList-Collection-Creator](https://github.com/jonjonsson/Emby-MDBList-Collection-Creator) by [jonjonsson](https://github.com/jonjonsson).**
> The core sync engine (MDBList API, Emby API, item sorting, metadata refresh, seasonal collections) is entirely his work.
> This fork adds a Web UI, Home Assistant add-on packaging, and Docker/ingress support.
> Please consider [supporting the original author on Patreon](https://www.patreon.com/c/acdbtv).

---

## What This Fork Adds

| Feature | Details |
|---|---|
| **Web UI** | Flask-based dashboard with pages for Settings, Collections, and Logs — no more editing `config.cfg` by hand |
| **Home Assistant Add-on** | One-click install via HACS, with ingress support (runs inside the HA sidebar) |
| **Docker image** | Standalone Docker image published to `ghcr.io/lymestone/embymdblist-ha` |
| **Live sync controls** | Dashboard shows sync status, last/next sync time, and a "Sync Now" button |
| **Background sync** | Daemon thread runs sync cycles automatically; config changes via the Web UI are picked up each cycle |

Everything else — the sync logic, MDBList integration, Emby API calls, seasonal collections, sort-name tricks, metadata refresh — comes from the original project.

---

## Installation

### Home Assistant (HACS)

1. In Home Assistant, go to **HACS > 3-dot menu > Custom repositories**
2. Add this repository URL: `https://github.com/Lymestone/EmbyMBDList-HA`
3. Category: **Add-on**
4. Install **Emby MDBList Collection Creator** from the add-on store
5. Start the add-on and open the Web UI from the sidebar or add-on page

### Docker (standalone)

```bash
docker run -d \
  -v /path/to/config.cfg:/data/config.cfg \
  -p 5000:5000 \
  ghcr.io/lymestone/embymdblist-ha:latest
```

Or with Docker Compose:

```yml
services:
  emby-mdblist:
    image: ghcr.io/lymestone/embymdblist-ha:latest
    ports:
      - "5000:5000"
    volumes:
      - ./config.cfg:/data/config.cfg
```

Then open `http://localhost:5000` in your browser.

### Manual (Python)

```bash
pip install -r requirements.txt
python run.py
```

This starts the Web UI on port 5000 and the sync loop in the background.

To run just the sync script without the Web UI (original behavior):

```bash
python app.py
```

---

## Web UI

The Web UI provides four pages:

- **Dashboard** — sync status, last/next sync time, configured collections overview, and a manual "Sync Now" button
- **Settings** — configure Emby server URL, API keys, MDBList API key, sync interval, and all toggle options
- **Collections** — add, edit, and remove collections with their MDBList source URLs and per-collection settings
- **Logs** — live view of sync output

*Screenshots coming soon — contributions welcome!*

---

## Configuration

All original `config.cfg` options are supported. The Web UI reads and writes the same config file. See the [original project's documentation](https://github.com/jonjonsson/Emby-MDBList-Collection-Creator) for full details on:

- Collection setup (MDBList URLs, list IDs, user/list names)
- Sorting items by date added
- Metadata refresh for newly released content
- Seasonal/temporary collections
- Collection posters
- Backup & restore of watch history

---

## Original Features (from upstream)

All features from [jonjonsson's v1.84](https://github.com/jonjonsson/Emby-MDBList-Collection-Creator) are included:

- List Conversion: Transform MDBList lists into Emby collections
- Metadata Refresh: Keep ratings up-to-date for newly released content
- Collection Images: Upload local or remote images for collection posters
- Seasonal Collections: Specify when a collection should be visible
- Collection Ordering: Show collections in order of last update
- Collection Descriptions: From MDBList or custom
- Backup & Restore: Utilities for watch history and favorites (`app_backup.py`, `app_restore_backup.py`)

---

## Credits

- **Original project**: [Emby-MDBList-Collection-Creator](https://github.com/jonjonsson/Emby-MDBList-Collection-Creator) by [jonjonsson](https://github.com/jonjonsson)
- **Plugin alternative**: [ACdb.tv Automated Collections](https://acdb.tv/) — if you prefer an Emby plugin over a standalone script
- **This fork**: Web UI, Home Assistant add-on packaging, and Docker support by [Lymestone](https://github.com/Lymestone)

---

## License

The original project does not include a license file. This fork adds a Web UI and Home Assistant integration on top of that work. Please refer to the [original repository](https://github.com/jonjonsson/Emby-MDBList-Collection-Creator) for licensing questions.
