## Welcome to DD-IDE SDK
This is an early alpha version of the DD-IDDE SDK. It is used in combination with the DeepPavlov's DD-IDDE available [here](https://github.com/deepmipt/vscode-dff).

## Requirements

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# install dff
pip install dff
# install dashboard for stats
pip install dff-node-stats[dashboard] 
```
### Environment

| Item           | Requirements                                          | Comments                                                     |
| -------------- | ----------------------------------------------------- | ------------------------------------------------------------ |
| OS             | Debian-based distribution, e.g., Ubuntu or Windows 10 | This version was tested on Ubuntu 18.04 under WSL2 on Windows 11 and Windows 10. |
| Python         | v3.9+                                                 | This version was tested on OS with Python 3.9.               |
| Docker         | v20+                                                  | This version was tested with Docker v20.10.7 (64-bit).       |
| Docker-Compose | v1.29.2                                               | This version was tested with Docker-Compose v1.29.2.         |

### VS Code
#### Required Extensions
* DD-IDDE
* Python
* Docker

#### Optional Extensions
* Remote - WSL 

#### Set WSL-based Terminal As Default One
If needed, set your WSL-based terminal app as the default one in your VS Code by following these [instructions](https://dev.to/giannellitech/setting-the-default-terminal-in-vs-code-95c).

### Python 3.9 - set as default (optional)
1. Install the python3.9 package using apt-get

```sudo apt-get install python3.9```

Add *Python3.6* & *Python 3.9* to update-alternatives

```sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 1```
```sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 2```

Update Python 3 to point to Python 3.9:

```sudo update-alternatives --config python3```

Enter 2 for Python 3.9

Test the version of python:

```python3 --version```
```Python 3.9``` 

Test the version of python used by pip3 command:

```pip3 --version```
```pip 21.3.1 from /home/danielko/.local/lib/python3.9/site-packages/pip (python 3.9)```

### Prerequisites

```pip3 install lxml```

## Installation Process
### Runtime
We use [Dialog Flow Framework](https://www.github.com/deepmipt/dialog_flow_framework) as the runtime for the open-domain/scenario-driven chatbots.

Follow these instructions to install Dialog Flow Framework:
```bash
# install dff
pip install dff
# install dashboard for stats
pip install dff-node-stats[dashboard] 
```

Follow these requirements to prepare DD-IDDE SDK to run on your machine:

```bash
pip install -r requirements.txt
```

### Discourse Moves Recommendation System
We use our Speech Functions Classifier & Predictor from our larger [DeepPavlov Dream](https://www.github.com/deepmipt/dream) Multiskill AI Assistant Platform.

Follow these instructions to run the Discourse Moves Recommendation System:
```bash 
docker-compose up -d --build
```
After that sf predictor is available on `localhost:8107/annotation` and sf classifier is availible on `localhost:8108/annotation` 

## Usage
### DD-IDDE as Designer
Go to your local clone of this repo and run:

```code .```

This will ensure that your VS Code will run from this folder, and will (in case you use WSL) run through WSL.

### Discourse Moves Recommendation System
TBD

## Generic Responses
TBD
## Entity Detection
TBD
