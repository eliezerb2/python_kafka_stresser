FROM python:3.11

# Set the working directory
WORKDIR /app

# Copy the application files
COPY . ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "src/main.py"]