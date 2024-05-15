ARG pyver
FROM python:${pyver}
ARG listen_port
ARG git_repo
RUN apt-get update && apt-get install -y \
	netcat-traditional \
	vim \
	awscli \
&& rm -rf /var/lib/apt/lists/*
WORKDIR /app
RUN --mount=type=bind,source=${git_repo}/requirements.txt,target=/tmp/requirements.txt \
    pip install --no-cache-dir -r /tmp/requirements.txt
EXPOSE $listen_port 
CMD ["/bin/bash"]
