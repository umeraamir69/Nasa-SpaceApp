# EchoLens

NASA Space Apps Toronto 2026 — Dancing with the SARs.

Track surface change with **NISAR** radar. Working notes live in `notes/` (Obsidian vault). Start at `notes/00 Home.md`.

## This week

1. Create a free Earthdata account: https://urs.earthdata.nasa.gov/
2. On this machine: `source venv/bin/activate && python -c "import earthaccess; earthaccess.login()"`
3. Search candidate events (no download yet):

```text
source venv/bin/activate
python scripts/search_nisar.py --event snyder
python scripts/search_nisar.py --event thunder-bay
```

Do not put Earthdata passwords in this repo or in `notes/`.

## Layout

| Path | What |
|---|---|
| `notes/` | Project brain |
| `scripts/` | Data search / later processing |
| `data/` | Local granules (gitignored) |
