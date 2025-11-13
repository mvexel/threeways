# OSM H3 Metrics Pipeline

This repository contains an **OSM → PostGIS + H3 → pmtiles** pipeline that:

- Downloads OpenStreetMap data for a **bounded region** (Utah first).
- Imports it into **PostGIS** using **osm2pgsql flex + Lua**.
- Computes **metrics on H3 hexagons** (initially “age of POIs”, e.g. `shop=*`).
- Generates **vector tiles as pmtiles** using **tippecanoe**.
- Serves tiles via a simple static server or object storage + CDN.

The design is planned to be **region-parameterised**: once Utah works, you should be able to deploy the same stack other regions by changing a few environment variables and it would "just work". Not there yet.

The deployment target assumed here is:

- **Hetzner Cloud** VM (e.g. 4 vCPU, 8 GB RAM, 160+ GB SSD).
- **Docker Compose as the main “infra as code”** artifact.
- **Dokploy** on the same host to orchestrate the Compose app, manage TLS, and run scheduled jobs.

Dokploy is completely optional - you can totally orchestrate this with just docker-compose, but I'm currently in "Self Hosted PaaS" experimentation mode and testing the limitations of those systems.

---

## architecture

1. **OSM Source**
   - **Geofabrik extract** (`*-latest.osm.pbf`). For state / province / country
   - Could eventually be planet PBF + replication diffs for global/large-region coverage, but that would require some rethinking of bits of this setup.

2. **OSM → PostGIS**
   - Import with **osm2pgsql flex** using a custom Lua style:
     - Right now I want to demonstrate POI age (initially just `shop=*` and perhaps a few `amenity=*`).
     - Preserve **timestamps** (and other extra attributes) so we can compute feature age.
   - Store in PostGIS as `osm_poi_shop` (or similar).
   - this would be an extensible design - drop in another lua file + another metrics declaration, and we'd have another QA layer.

3. **Metrics + H3**
   - Use `h3` + `h3_postgis` extensions to: generate H3 cells at res 6,7,8 (for example) and compute relevant aggrregate metrics like:
       - POI counts
       - Average age
       - P90 age
       - Counts of “older than 1 year”, “younger than 30 days”, etc.

4. **Tiles**
   - Export H3 cells with metrics as GeoJSON/NDJSON.
   - Run **tippecanoe** to generate one or more **pmtiles** files.
   - Drop into Cloudflare R2

5. **Orchestration**
   - A **pipeline container** runs the above steps.
   - Scheduled **daily**:
     - Via `cron` on the host, _or_
     - Via Dokploy’s “Schedule Jobs” against the `pipeline` service.

The of course a simple map viewer! Can be MapLibre with minimal UX. Needs a legend and an about page.

There we go.