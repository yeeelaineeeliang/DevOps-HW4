FROM jenkins/ssh-agent:latest
USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      openjdk-21-jre-headless \
      docker.io \
      python3 \
      python3-pip \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*
ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-arm64
ENV PATH="${JAVA_HOME}/bin:${PATH}"
RUN mkdir -p /home/jenkins/.ssh && \
    chown -R jenkins:jenkins /home/jenkins/.ssh
USER jenkins
