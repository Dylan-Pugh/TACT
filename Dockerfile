FROM mambaorg/micromamba:latest

# Set working directory
WORKDIR /app

# Copy environment file
COPY tact/environment.yml /tmp/environment.yml

# Install dependencies based on the environment file
RUN micromamba install -y -n base -f /tmp/environment.yml && \
    micromamba clean --all --yes

# Copy the application code
COPY . /app

# Expose port
EXPOSE 5000

# Activate the environment and run the application
# Note: In micromamba docker, 'base' is the default env if we install into it as above.
# We ensure the python path is correct or just run with python directly if it's in path.
ARG MAMBA_DOCKERFILE_ACTIVATE=1
ENV PATH="$MAMBA_ROOT_PREFIX/bin:$PATH"
ENV PYTHONPATH="/app"

CMD ["python", "tact/API/tact_api.py"]
