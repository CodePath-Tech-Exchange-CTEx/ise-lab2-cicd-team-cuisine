### VARIABLES TO CHANGE - START
PROJECT_ID=
SERVICE_NAME=
### VARIABLES TO CHANGE - END

# ----------- Manual Deployment ------------ #
gcloud config set project ${PROJECT_ID}

if [ $? != 0 ]; then
    echo "'gcloud config set project' failed!"
    exit 1
fi

gcloud builds submit --tag gcr.io/${PROJECT_ID}/${SERVICE_NAME}

if [ $? != 0 ]; then
    echo "'gcloud builds' failed!"
    exit 1
fi

gcloud run deploy ${SERVICE_NAME} \
    --image gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest \
    --region us-central1 \
    --allow-unauthenticated

if [ $? != 0 ]; then
    echo "'gcloud run deploy' failed!"
fi
