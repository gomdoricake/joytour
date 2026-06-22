# Use the official Python runtime image
FROM python:3.13
# Set the working directory inside the container
WORKDIR /joyapp


# docker run --name my-django-container \
#   --network my-network \
#   -p 8000:8000 \
#   -v "$(pwd)":/app \
#   -d my-django-app

# Copy the Django project  and install dependencies
COPY requirements.txt  ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy in the source code
COPY . .
EXPOSE 8000


CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
