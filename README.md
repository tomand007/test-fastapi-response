To run this code:
```bash
docker build -t test-fastapi-response .
docker run --rm --add-host=host.docker.internal:host-gateway -v ~/code/tmp/tests_results/:/app/logs/ test-fastapi-response:latest
```