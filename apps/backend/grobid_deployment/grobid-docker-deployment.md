# Deploying GROBID with Docker

GROBID is a machine learning software for extracting information from scholarly documents. This guide will help you deploy GROBID using Docker.

## Prerequisites

- Docker installed ([Docker Installation Guide](https://docs.docker.com/get-docker/))
- If you want to use GPU acceleration (recommended for the full version image), make sure NVIDIA Docker support is installed

## Deployment Options

GROBID provides two official Docker images:

### 1. Full Version Image (about 10GB)

This image provides the best accuracy, including all required Python and TensorFlow libraries, GPU support, and all deep learning model resources. Use this version if you have a limited number of PDF files to process, have a good performance machine, and prioritize accuracy.

```bash
# Pull the latest full version image
docker pull grobid/grobid:0.8.1

# Run container (with GPU)
docker run --rm --gpus all --init --ulimit core=0 -p 8070:8070 grobid/grobid:0.8.1

# Run container (without GPU)
docker run --rm --init --ulimit core=0 -p 8070:8070 grobid/grobid:0.8.1
```

### 2. Lightweight Image (about 300MB)

This image provides the best runtime performance, memory usage, and Docker image size. However, it doesn't use some models that perform best in terms of accuracy. Use this version if you have a large number of PDF files to process, limited system resources, and accuracy is not as important.

```bash
# Pull the latest lightweight image
docker pull lfoppiano/grobid:0.8.1

# Run container
docker run --rm --init --ulimit core=0 -p 8070:8070 lfoppiano/grobid:0.8.1
```

## Port Mapping

By default, GROBID runs on port `8070` inside the container. You can map it to any port on the host, such as the traditional `8080` port:

```bash
# Map container port 8070 to host port 8080
docker run --rm --init --ulimit core=0 -p 8080:8070 lfoppiano/grobid:0.8.1

# Also map health check port
docker run --rm --init --ulimit core=0 -p 8080:8070 -p 8081:8071 lfoppiano/grobid:0.8.1
```

## Accessing GROBID Service

After deployment, you can access GROBID through:

- Open a browser and visit `http://localhost:8070` (or your mapped port, such as `http://localhost:8080`)
- Health check can be accessed via `http://localhost:8071` (or your mapped port, such as `http://localhost:8081`)

## Using GROBID Web Services

GROBID provides various Web service APIs that you can use through HTTP requests. Detailed API documentation can be found in the GROBID service console.

Common services include:

- `/api/processHeaderDocument`: Process document headers
- `/api/processFulltextDocument`: Process full text
- `/api/processReferences`: Process references

## Data Persistence (Optional)

If you need to persist GROBID data or configuration, you can use volume mounts:

```bash
# Mount configuration directory
docker run --rm --init --ulimit core=0 -p 8070:8070 -v /path/to/local/config:/opt/grobid/config lfoppiano/grobid:0.8.1
```

## Troubleshooting

- If you encounter out-of-memory issues when running on MacOS, increase the default memory limit for Docker containers
- Make sure your system has sufficient resources to run GROBID, especially when using the full version image

## References

- [GROBID Official Documentation](https://grobid.readthedocs.io/)
- [GROBID GitHub Repository](https://github.com/kermitt2/grobid)
- [GROBID Docker Documentation](https://grobid.readthedocs.io/en/latest/Grobid-docker/) 