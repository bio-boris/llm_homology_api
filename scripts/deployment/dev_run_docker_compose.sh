export VCS_REF=$(git rev-parse HEAD)  # Set VCS_REF to the current Git commit hash
export VERSION=1.0.0  # Set VERSION to your application's current version, adjust as necessary
docker-compose up --build -d