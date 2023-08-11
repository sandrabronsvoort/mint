# MINT
Welcome to MINT v0.1: your emissions MINimization Tool.

MINT is supply chain optimization tool made for entrepreneurs and small companies who are serious about minimizing their supply chain emissions but do not have the financial means for extensive software programs. It is my mission to make analytics and mathematical modeling available to a wide range of people and give them the tools to “do the right thing”. At the same time, MINT is a personal project I work on in my free time, and currently is a very simplistic solution. Please reach out if you need help in the process of getting it up and running or have any other questions. I am very open to suggestions and feedback, and would love to chat about your experiences and insights!

MINT is developed by Sandra Bronsvoort <br>
[sandrabronsvoort.com](www.sandrabronsvoort.com)<br>
[hi@sandrabronsvoort.com](hi@sandrabronsvoort.com)

## How-to

MINT can be run either within Docker or using Python.

### Run with Docker

Make sure you've got Docker installed on your computer. Then checkout this repository on your computer, and run:

```bash
docker-compose up
```

If you're using a Mac M1, run:

```bash
docker-compose -f docker-compose.m1.yaml up
```

### Run with Python

Running with Python requires a few more extra things to be installed on your computer. To run with Python, install:

* Python 3 

* Poetry

And run the following commands:

```bash
# Install dependencies
poetry install

# Run app
python main.py
```
