#!/bin/bash
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID="887664210442"
GCP_PROJECT_ID="sportapp-417820"
GCP_PROJECT_REGION="us-central1"

# Parse command-line arguments
while getopts "c:s:" opt; do
    case $opt in
        c)
            CLOUD_PROVIDER=$OPTARG
            ;;
        s)
            SERVICES=$OPTARG
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            exit 1
            ;;
        :)
            echo "Option -$OPTARG requires an argument." >&2
            exit 1
            ;;
    esac
done

echo "$SERVICES"

# Validate cloud provider option
if [ "$CLOUD_PROVIDER" != "aws" ] && [ "$CLOUD_PROVIDER" != "gcp" ]; then
    echo "Invalid cloud provider specified. Use -c (aws|gcp)" >&2
    exit 1
fi

if [ "$CLOUD_PROVIDER" == "gcp" ]; then
    if [ -f "./gcloud-credentials.json" ]; then
        export GCP_SERVICE_ACCOUNT_JSON="./gcloud-credentials.json"
    else
        echo "GCP service account JSON file not found" >&2
        exit 1
    fi
fi

# Define allowed folder names
ALLOWED_FOLDERS=("users" "sports" "authorizer")

# Function to check if a folder name is allowed
is_allowed_folder() {
    local folder_name="$1"
    for allowed_folder in "${ALLOWED_FOLDERS[@]}"; do
        if [ "$folder_name" == "$allowed_folder" ]; then
            return 0  # Folder name is allowed
        fi
    done
    return 1  # Folder name is not allowed
}

IFS=',' read -ra SERVICES_ARRAY <<< "$SERVICES"
for folder_name in "${SERVICES_ARRAY[@]}"; do
    if ! is_allowed_folder "$folder_name"; then
        echo "Invalid service name: $folder_name" >&2
        exit 1
    fi
done

# Login to Docker registry
if [ "$CLOUD_PROVIDER" == "aws" ]; then
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
elif [ "$CLOUD_PROVIDER" == "gcp" ]; then
    docker login -u _json_key --password-stdin $GCP_PROJECT_REGION-docker.pkg.dev < "$GCP_SERVICE_ACCOUNT_JSON"
fi

cd projects || exit

# Iterate through provided folder names
for folder_name in "${SERVICES_ARRAY[@]}"; do
    # Check if the folder contains a Dockerfile
    if [ -f "$folder_name/Dockerfile" ]; then
        echo "Building and pushing $folder_name"

        # Build Docker image
        docker build -t "$folder_name" "$folder_name"

        # Tag Docker image
        if [ "$CLOUD_PROVIDER" == "aws" ]; then
            docker tag "$folder_name:latest" "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$folder_name:latest"
            # Push Docker image to AWS ECR
            docker push "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$folder_name:latest"
        elif [ "$CLOUD_PROVIDER" == "gcp" ]; then
            docker tag "$folder_name:latest" "$GCP_PROJECT_REGION-docker.pkg.dev/$GCP_PROJECT_ID/sportapp/$folder_name:latest"
            # Push Docker image to GCP Artifact Registry
            docker push "$GCP_PROJECT_REGION-docker.pkg.dev/$GCP_PROJECT_ID/sportapp/$folder_name:latest"
        fi
    else
        echo "Skipping $folder_name: No Dockerfile found" >&2
    fi
done

echo "All images pushed to $CLOUD_PROVIDER registry"
