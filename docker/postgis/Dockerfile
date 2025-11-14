FROM postgis/postgis:16-3.4

# Install toolchain + pgxn client so we can compile extensions from PGXN.
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    build-essential \
    cmake \
    git \
    pgxnclient \
    postgresql-server-dev-16 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install libh3 + h3_postgis via PGXN. pgxn bundles libh3 sources,
# so we do not need additional system packages beyond the toolchain above.
RUN pgxn install h3 \
    && pgxn install h3_postgis
