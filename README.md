# mini-rag

This is a minimal implementation of The RAG model for question answering.

## Requirements

- Python 3.8 or later

### Install python using MiniConda

1) Download and insall MiniConda from [here](https://www.anaconda.com/docs/getting-started/miniconda/install)

2) Create a new environment using the following command:
```bash
$ conda create -n mini-rag python=3.8
```
3) Activate the environment:
```bash
$ conda activate mini-rag   
```

### (Optional) Setup you command line interface for better readability

```bash
export PS1="\[\033[01;32m\]\u@\h:\w\n\[\033[00m\]\$ "
```

## Installation

### Install the required packages

```bash
$ pip install -r requirements.txt
```

### Install Docker

Docker is required to run MongoDB locally.  
Follow the official instructions for your OS:  
- [Get Docker](https://docs.docker.com/get-docker/)

## Run Docker Compose Services

```bash
$ cd docker
$ cp .env.example .env
```

- update `.env` with your credentials



```bash
$ cd docker
$ sudo docker compose up -d
```

You can start a MongoDB container with:

```bash
$ docker run -d -p 27007:27017 --name mongodb mongo:7-jammy
```

This will run MongoDB on `localhost:27007`.

### (Optional) Install Studio 3T

[Studio 3T](https://studio3t.com/download/) is a GUI client for MongoDB, making it easier to view and manage your database.

1. Download Studio 3T from [here](https://studio3t.com/download/).
2. Install and launch the application.
3. Connect to your local MongoDB instance using:
   - Host: `localhost`
   - Port: `27007`

---

Set your environment variables in the .env file. Like `OPENAI_API_KEY` value.

## Run the FastAPI server

```bash
$ uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

## POSTMAN Collection

Download the POSTMAN collection from [/assets/mini-rag-app.postman_collection.json](/assets/mini-rag-app.postman_collection.json])