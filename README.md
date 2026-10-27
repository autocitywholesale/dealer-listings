# Auto City Fredericton – dealer-to-dealer listings
Live: https://autocitywholesale.github.io/dealer-listings/ (GitHub Pages, repo https://github.com/autocitywholesale/dealer-listings; every push to `main` builds via `.github/workflows/pages.yml`).
Optional preview: https://autocity-fredericton-dealers.surge.sh (surge.sh; account autocityfredericton+surge@mail.grokbot.com, logged in on this box).

## Private links (important)
The home page lists no cars. Each vehicle is published only at `/v/<slug>/` where `slug` is a random 12-char token that `build.py` generates once and stores in `vehicles.json` (never change it; the old `/v/<VIN>/` paths are not published). `build.py` prints each unsold car's share URL. Sold cars are not published. Pages carry noindex/nofollow and `robots.txt` disallows all. Always publish with `build.py --deploy` so a new car's slug is saved and committed (the GitHub Action refuses to build an unsold car without a slug).
NOTE: the repo itself is public, so `vehicles.json` (with slugs) is readable by anyone who finds the repo.

## Add a vehicle
1. Put photos in `incoming/<VIN>/` (first photo = main photo). Put Carfax / build-sheet PDFs there too if you have them.
2. Add an entry to `vehicles.json` -> "vehicles" list. Only `vin`, `year`, `make`, `model`, `km` are required:
```json
{"vin":"...","year":2024,"make":"Subaru","model":"Forester","trim":"Touring","km":47000,
 "asking_price":null,"wholesale_price":null,
 "photos":["incoming/VIN/1.jpg","incoming/VIN/2.jpg"],
 "specs":{"Engine":"...","Drivetrain":"...","Exterior colour":"..."},
 "build_sheet":{"msrp":41000,"packages":["..."],"options":["..."],"pdf":"incoming/VIN/sticker.pdf"},
 "carfax":{"Last reported odometer":"...","Accidents/damage":"...","Registration":"...","Open recalls":"...","records":["..."],"pdf":"incoming/VIN/carfax.pdf"},
 "notes":"", "sold":false}
```
3. Build + publish: `cd /workspace/dealer-listings && python3 build.py --deploy --msg="Add <VIN>"` (commits and `git push`es to main; the Action rebuilds and deploys). Push auth uses `$GITHUB_DEALER_LISTINGS_TOKEN` via a git credential helper (token is not stored in the repo).
   Optional surge preview: `python3 build.py --preview`.

Photos are auto-rotated and resized to max 1600 px (plus a 640 px thumbnail). Set `"sold": true` to hide a unit. Never commit invented data – leave fields out if unknown.

## Carfax + spec sheet on every listing (do this for each new vehicle)
- Carfax: save the PDF as `incoming/<VIN>/carfax.pdf`, fill `carfax` (summary fields, `records`, `pdf`, optional `url` = online report link, shown as a link).
- Build sheet: if a real window sticker/build sheet exists, use `build_sheet.pdf` path with msrp/packages/options. If not, save the NHTSA decode to `incoming/<VIN>/vpic.json` (https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvalues/<VIN>?format=json), run `python3 make_specsheet.py <VIN>` and set `"build_sheet":{"spec_sheet":true,"pdf":"incoming/<VIN>/build_sheet.pdf"}`. The page then shows a "Factory specifications" section (never labelled as a window sticker; no MSRP/options invented).
