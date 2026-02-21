FROM nvidia/cuda:10.1-cudnn7-devel-ubuntu18.04

RUN apt-get update && apt-get install -y \
    wget bzip2 pbzip2 ca-certificates screen \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://repo.anaconda.com/miniconda/Miniconda3-py37_4.8.3-Linux-x86_64.sh -O /miniconda.sh && \
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