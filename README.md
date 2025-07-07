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

### Setup the environment variables

```bash
$ cp .env.example .env
```

Set your environment variables in the .env file. Like OPENAI_API_KEY value.