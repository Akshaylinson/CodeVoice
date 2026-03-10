FROM python:3.12 AS builder

RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
      build-essential cmake ninja-build git

WORKDIR /app

COPY pyproject.toml setup.py CMakeLists.txt MANIFEST.in README.md ./
COPY src/piper/ ./src/piper/
COPY script/setup script/dev_build script/package ./script/

# Fix line endings and make scripts executable
RUN sed -i 's/\r$//' ./script/setup ./script/dev_build ./script/package && \
    chmod +x ./script/setup ./script/dev_build ./script/package

RUN ./script/setup --dev
RUN ./script/dev_build
RUN ./script/package

# -----------------------------------------------------------------------------

FROM python:3.12-slim

ENV PIP_BREAK_SYSTEM_PACKAGES=1

WORKDIR /app
COPY --from=builder /app/dist/piper_tts-*linux*.whl ./dist/
RUN pip3 install ./dist/piper_tts-*linux*.whl
RUN pip3 install 'flask>=3,<4'

COPY docker/entrypoint.sh /

# Fix line endings and make entrypoint executable
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["/entrypoint.sh"]
