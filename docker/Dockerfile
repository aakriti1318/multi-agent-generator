FROM python:3.11.13-slim

WORKDIR /app

# Install system dependencies to update the base environment
RUN apt-get update \
    && apt-get install -y build-essential

# Copy all the necessary files to the working directory (app)
COPY requirements.txt /app/
COPY multi_agent_generator/ /app/multi_agent_generator/
COPY streamlit_app.py /app/

# Install the python dependencies
RUN pip install -r requirements.txt --no-cache-dir

# Expose 
EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py"]
