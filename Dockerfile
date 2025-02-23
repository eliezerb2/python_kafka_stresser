FROM python:3.11

ARG HOST_PROJECT_FOLDER_NAME
ARG WORKDIR_FOLDER_NAME
ARG CONTAINER_PROJECT_FOLDER_NAME
ARG UTILS_FOLDER_NAME

# Set the working directory
WORKDIR /${WORKDIR_FOLDER_NAME}

# Copy the shared utils files
COPY ./${UTILS_FOLDER_NAME}/ ./${UTILS_FOLDER_NAME}/

# Copy the project files
COPY ./${HOST_PROJECT_FOLDER_NAME}/ ./${CONTAINER_PROJECT_FOLDER_NAME}/

# Install dependencies
RUN pip install --no-cache-dir -r ${CONTAINER_PROJECT_FOLDER_NAME}/requirements.txt
RUN pip install --no-cache-dir -r ${UTILS_FOLDER_NAME}/requirements.txt

# Set the PYTHONPATH to include the src folders
ENV CONTAINER_PROJECT_SRC_PATH /${WORKDIR_FOLDER_NAME}/${CONTAINER_PROJECT_FOLDER_NAME}/src
ENV CONTAINER_UTILS_SRC_PATH /${WORKDIR_FOLDER_NAME}/${UTILS_FOLDER_NAME}/src
ENV PYTHONPATH "${PYTHONPATH}:${CONTAINER_UTILS_SRC_PATH}:${CONTAINER_PROJECT_SRC_PATH}" 

ENTRYPOINT /bin/sh -c "python /${CONTAINER_PROJECT_SRC_PATH}/main.py"