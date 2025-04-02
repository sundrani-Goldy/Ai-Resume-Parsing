# Pull the official base image
FROM python:3.13

# Set work directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Install dependencies
RUN apt-get update && apt-get install -y postgresql-client

RUN pip install --upgrade pip

COPY ./requirements.txt /app/
RUN pip install -r requirements.txt --no-cache-dir

# Copy project
COPY . /app/

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/media

# Set permissions
RUN chmod -R 755 /app

# Create startup script
RUN echo '#!/bin/bash\n\
python manage.py wait_for_db\n\
python manage.py migrate\n\
python manage.py populate_job_postings\n\
python manage.py runserver 0.0.0.0:8000 & \n\
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose ports for both Django and Streamlit
EXPOSE 8000 8501

# Use the startup script
CMD ["/app/start.sh"]
