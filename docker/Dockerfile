FROM --platform=linux/amd64 ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    wget bzip2 pbzip2 ca-certificates screen \
    libgl1-mesa-glx libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /miniconda.sh && \
    bash /miniconda.sh -b -p /opt/conda && \
    rm /miniconda.sh

ENV PATH="/opt/conda/bin:/bin-dir:$PATH"

COPY maia-individual/environment.yml /environment.yml
RUN conda env create -f /environment.yml && conda clean -afy

COPY maia-individual/ /maia-individual/
WORKDIR /maia-individual
RUN conda run -n transfer_chess python setup.py install

COPY bin/ /bin-dir/
RUN chmod +x /bin-dir/* 2>/dev/null || true

COPY models/ /models/
WORKDIR /
