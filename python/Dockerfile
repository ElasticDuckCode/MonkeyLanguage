FROM condaforge/mambaforge
WORKDIR /root

COPY environment.yml .
RUN mamba env create -f environment.yml
RUN echo "conda activate monkey" >> ~/.bashrc

SHELL ["/bin/bash", "--login", "-c"]
COPY src src
COPY tests tests
COPY run_tests .
ENTRYPOINT ["./run_tests"]
