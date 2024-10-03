CAN: Certainly! I’ll modify the script to pass the host’s http_proxy, https_proxy, and no_proxy environment variables to the Docker container. Here’s the updated version of the “docker-jira-bin.sh” script:

#!/bin/bash

# docker-jira-bin.sh

# Set variables
DOCKER_IMAGE="python:3.9-slim"
SOURCE_DIR="$(pwd)/src"
TARGET_DIR="$(pwd)/build"
MAIN_FILE="main.py"
BINARY_NAME="jira_app"

# Ensure the build directory exists
mkdir -p "$TARGET_DIR"

# Pass proxy settings to Docker
PROXY_ARGS=""
if [ -n "$http_proxy" ]; then
    PROXY_ARGS="$PROXY_ARGS --env http_proxy=$http_proxy"
fi
if [ -n "$https_proxy" ]; then
    PROXY_ARGS="$PROXY_ARGS --env https_proxy=$https_proxy"
fi
if [ -n "$no_proxy" ]; then
    PROXY_ARGS="$PROXY_ARGS --env no_proxy=$no_proxy"
fi

# Run Docker container to build the binary
docker run --rm \
    -v "$SOURCE_DIR:/app/src" \
    -v "$TARGET_DIR:/app/build" \
    $PROXY_ARGS \
    "$DOCKER_IMAGE" \
    /bin/bash -c "
        set -e
        cd /app
        pip install pyinstaller
        pip install -r src/requirements.txt
        pyinstaller --onefile --name $BINARY_NAME src/$MAIN_FILE
        mv dist/$BINARY_NAME build/
    "

# Check if the binary was created successfully
if [ -f "$TARGET_DIR/$BINARY_NAME" ]; then
    echo "Binary created successfully: $TARGET_DIR/$BINARY_NAME"
else
    echo "Failed to create binary"
    exit 1
fi

In this updated script, I’ve made the following changes:

1. Added a section to capture the host’s proxy settings:
PROXY_ARGS=""
if [ -n "$http_proxy" ]; then
    PROXY_ARGS="$PROXY_ARGS --env http_proxy=$http_proxy"
fi
if [ -n "$https_proxy" ]; then
    PROXY_ARGS="$PROXY_ARGS --env https_proxy=$https_proxy"
fi
if [ -n "$no_proxy" ]; then
    PROXY_ARGS="$PROXY_ARGS --env no_proxy=$no_proxy"
fi

2. Modified the docker run command to include the proxy arguments:
docker run --rm \
    -v "$SOURCE_DIR:/app/src" \
    -v "$TARGET_DIR:/app/build" \
    $PROXY_ARGS \
    "$DOCKER_IMAGE" \
    ...


These changes will pass the host’s http_proxy, https_proxy, and no_proxy environment variables to the Docker container if they are set. This allows the container to use the same proxy settings as the host machine, which can be crucial for network operations like downloading packages or dependencies.

To use this script:

1. Save it as “docker-jira-bin.sh” in the same directory as your “src” folder.
2. Make it executable: chmod +x docker-jira-bin.sh
3. Run it: ./docker-jira-bin.sh

The script will now automatically use the host’s proxy settings when creating and running the Docker container for building the binary.

Is there anything else you’d like me to modify or add to the script?

CAN: Certainly! I’ll split this Shell command into two parts as you requested. I’ll create a script that first creates a Docker container without removing it, and then provides a separate command to manually execute the Python compilation within the Docker container. Here’s the code:

#!/bin/bash

# Part 1: Create Docker container without removing it
container_id=$(docker run -d -v "$(pwd):/src/" --entrypoint /bin/bash docker.pyinstaller:3.10.4-slim -c "tail -f /dev/null")

echo "Docker container created with ID: $container_id"

# Part 2: Command to manually execute Python compilation
echo "To compile the Python script, run the following command:"
echo "docker exec $container_id /bin/bash -c 'pip install -r requirements.txt && pyinstaller jira-update.py --onefile --clean'"

echo "After compilation, you can stop and remove the container using:"
echo "docker stop $container_id"
echo "docker rm $container_id"

This script does the following:

1. Creates a Docker container that stays running using the tail -f /dev/null command.
2. Captures the container ID and displays it.
3. Provides the command to manually execute the Python compilation inside the container.
4. Provides commands to stop and remove the container when you’re done.

To use this script:

1. Save it to a file, e.g., docker_compile.sh
2. Make it executable: chmod +x docker_compile.sh
3. Run it: ./docker_compile.sh

After running the script, you’ll see the container ID and the command to execute the compilation. You can then run the compilation command manually when you’re ready.

Is there anything else you’d like me to modify or explain about this script?
