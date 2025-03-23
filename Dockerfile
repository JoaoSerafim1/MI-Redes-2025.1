FROM python:3.9-slim
WORKDIR /python_redes
# Download Package Information
RUN apt-get update -y
# Install Tkinter
RUN apt-get install tk -y && \
    apt-get install -y python3-pip
# Instalar o CustomTkinter
RUN pip install customtkinter
EXPOSE 8001
EXPOSE 8002