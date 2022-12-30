# tl;dr

tl;dr is an application that allows users to upload PDFs and generates a summary of the PDF using OpenAI's Text-Davinci-003 model. The app consists of a React frontend and a Python Django backend.

I built this application to learn the basics of the React framework and to familiarze myself with OpenAI API's. 

![Demo](https://cdn.discordapp.com/attachments/611191473601511434/1058503561182457926/tldr-1.gif)

## Features

- Upload PDFs from your local machine
- Generate a summary of the PDF using OpenAI's Text-Davinci-003 model
- View the summary directly in the app

## Prerequisites
Decide how you want to run the applications. Both the backend and frontend have Dockerfiles for building container images, as well as Helm charts for deploying to a Kubernetes cluster using the pre-built images.

If you want to run locally on your own machine without Docker, you will need to install the following
- Node.js and npm (for the frontend)
- Python 3.x and Django (for the backend)

You will also need an OpenAI API key to utilize the Text-Davinci-003 model

## Getting Started
Clone the repository:
```sh
  git clone https://github.com/tks98/tldr
```

### Running locally without Docker
Start the frontend. It will automatically open your browser to localhost:3000
```sh
  cd frontend
  npm start
```

Start the backend
```sh
  cd ..
  cd backend
  python app/server.py
```

### Running locally with Docker

Quickstart with prebuilt images. Run the following then visit localhost:3000 in your browser. 
```sh
docker run -p 3000:3000 tks98/tldr-frontend:1.0
docker run -p 5000:5000 tks98/tldr-backend:1.0
```

If you want to build yourself, follow the guide below. 

Building & starting the frontend
```sh
cd frontend
docker build -t tldr-frontend:latest .
docker run -p 3000:3000 tldr-frontend:latest
```
Building & starting the backend
```sh
cd backend
docker build -t tldr-backend:latest .
docker run -p 5000:5000 tldr-backend:latest
```

## Running on Kubernetes
To deploy on Kubernetes, you can utilize the helm charts located in the frontend/deploy and backend/deploy directories.

## Contributing
Contributions are always welcome. Please open a PR if you would like to contribute a change.
