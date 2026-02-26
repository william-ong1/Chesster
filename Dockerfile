FROM --platform=linux/amd64 ubuntu:22.04

# Avoid prompts during installation
ENV DEBIAN_FRONTEND=noninteractive
ENV CONDA_DIR=/opt/conda
ENV PATH="${CONDA_DIR}/bin:${PATH}"

# 1. Install system dependencies
# Added: cmake and libboost-all-dev for trainingdata-tool compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    # REQUIRED: gnupg is needed to fix the status 2 GPG error
    gnupg software-properties-common && \
    add-apt-repository ppa:ubuntu-toolchain-r/test -y && \
    apt-get update && apt-get install -y --no-install-recommends \
    python3-setuptools python3-wheel \
    libgoogle-perftools-dev \
    wget bzip2 pbzip2 ca-certificates git build-essential \
    # We install the specific versions here
    gcc-9 g++-9 make cmake libboost-all-dev \
    libgl1-mesa-glx libgl1 libglib2.0-0 \
    ninja-build meson python3-pip libgtest-dev zlib1g-dev \
    python-is-python3 \
    libopenblas-dev pkg-config libprotobuf-dev protobuf-compiler \
    screen \
    && rm -rf /var/lib/apt/lists/*
# 2. Install Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /miniconda.sh && \
    bash /miniconda.sh -b -p ${CONDA_DIR} && \
    rm /miniconda.sh

RUN conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main && \
    conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

# 3. Create the environment
RUN conda create -n transfer_chess -y -c conda-forge \
    python=3.7 \
    numpy=1.18.5 \
    pandas \
    scikit-learn \
    scipy \
    jupyter \
    matplotlib \
    seaborn \
    h5py \
    pyyaml \
    tqdm && \
    conda clean -afy

# 4. Use Pip for the specific ML versions
RUN ${CONDA_DIR}/envs/transfer_chess/bin/pip install --no-cache-dir \
    torch==1.4.0 \
    torchvision==0.5.0 \
    tensorflow-cpu==2.1.0 \
    python-chess==0.30.1 \
    tensorboardx==2.0 \
    humanize==2.4.0 \
    natsort==7.0.1

# 5. Setup Binaries (Compiling pgn-extract, Lc0 v0.23, and trainingdata-tool)
RUN mkdir -p /bin-dir

# Compile pgn-extract
RUN wget https://www.cs.kent.ac.uk/~djb/pgn-extract/pgn-extract-25-01.tgz && \
    tar -zxvf pgn-extract-25-01.tgz && \
    cd pgn-extract && \
    make && \
    cp pgn-extract /bin-dir/ && \
    cd .. && \
    rm -rf pgn-extract pgn-extract-25-01.tgz

# Compile Lc0 v0.23 from source
# Compile Lc0 v0.23 from source
RUN git clone -b release/0.23 --recurse-submodules https://github.com/LeelaChessZero/lc0.git && \
    cd lc0 && \
    CC=gcc-9 CXX=g++-9 ./build.sh -Ddnnl=false -Dopencl=false -Dblas=true && \
    cp build/release/lc0 /bin-dir/ && \
    cd .. && \
    rm -rf lc0

# Compile trainingdata-tool from source
RUN git clone --recurse-submodules https://github.com/DanielUranga/trainingdata-tool.git && \
    cd trainingdata-tool && \
    # We force CMake to use GCC 9 to match Lc0
    CC=gcc-9 CXX=g++-9 cmake . && \
    cmake --build . && \
    cp trainingdata-tool /bin-dir/ && \
    cd .. && \
    rm -rf trainingdata-tool

# Copy your local tools
# Wildcard ensures we don't overwrite the fresh binaries if old versions are in your local bin/
COPY bin/ /tmp/bin_local/
RUN cp -n /tmp/bin_local/* /bin-dir/ || true && rm -rf /tmp/bin_local
RUN chmod +x /bin-dir/*
ENV PATH="/bin-dir:$PATH"

# 6. Setup maia-individual backend
COPY maia-individual/ /maia-individual/
WORKDIR /maia-individual

RUN ${CONDA_DIR}/envs/transfer_chess/bin/pip install -e .

RUN echo "source activate transfer_chess" >> ~/.bashrc
ENV CONDA_DEFAULT_ENV=transfer_chess

WORKDIR /maia-individual