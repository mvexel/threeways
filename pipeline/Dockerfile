FROM python:3.12-slim

# Install system dependencies for osm2pgsql, tippecanoe, Postgres client tools
RUN apt-get update && apt-get install -y \
    osm2pgsql \
    postgresql-client \
    git \
    build-essential \
    libsqlite3-dev \
    zlib1g-dev \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Build and install tippecanoe from source
RUN git clone https://github.com/felt/tippecanoe.git /tmp/tippecanoe \
    && cd /tmp/tippecanoe \
    && make -j"$(nproc)" \
    && make install \
    && rm -rf /tmp/tippecanoe

WORKDIR /workspace

# Copy only what we need into the image
COPY osm2pgsql /workspace/osm2pgsql
COPY pipeline /workspace/pipeline

WORKDIR /workspace/pipeline

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create runtime directories for data artifacts
RUN mkdir -p /data/osm /data/tiles /data/logs

CMD ["python", "-m", "pipeline"]
