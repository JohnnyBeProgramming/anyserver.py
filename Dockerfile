FROM python:3.11.3
ENV WORK_DIR="/app"
EXPOSE 9999

# Copy the python scripts for the service
WORKDIR ${WORK_DIR}
COPY . .

# Install required dependencies
RUN pip install -r requirements.txt

# Generate merged output
RUN mkdir -p /dist \
 && python utils/merge.py server.py /dist/server.py
ENTRYPOINT [ "python", "server.py" ]