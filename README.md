## Welcome to DD-IDE SDK
This is an early alpha version of the DD-IDDE SDK. It is used in combination with the DeepPavlov's DD-IDDE available [here](https://github.com/deepmipt/vscode-dff).

## Prerequisites
### Environment

| Item           | Requirements                                          | Comments                                                     |
| -------------- | ----------------------------------------------------- | ------------------------------------------------------------ |
| OS             | Debian-based distribution, e.g., Ubuntu or Windows 10 | This version was tested on Ubuntu 18.04 under WSL2 on Windows 11 and Windows 10. |
| Python         | v3.9+                                                 | This version was tested on OS with Python 3.9.               |
| Docker         | v20+                                                  | This version was tested with Docker v20.10.7 (64-bit).       |
| Docker-Compose | v1.29.2                                               | This version was tested with Docker-Compose v1.29.2.         |

### Python Modules

| Item | Requirements | Comments                                  |
| ---- | ------------ | ----------------------------------------- |
| lxml | v4.6.3       | This version was tested with lxml v4.6.3. |

## Installation Process
### Runtime
We use [Dialog Flow Framework](https://www.github.com/deepmipt/dialog_flow_framework) as the runtime for the open-domain/scenario-driven chatbots.

Follow these instructions to install Dialog Flow Framework:
```bash
pip install -r requirements.txt
```
## Discourse Moves Recommendation System
We use our Speech Functions Classifier & Predictor from our larger [DeepPavlov Dream](https://www.github.com/deepmipt/dream) Multiskill AI Assistant Platform.

Follow these instructions to run the Discourse Moves Recommendation System:
```bash 
docker-compose up -d --build
```
After that sf predictor is availible on `localhost:8107/annotation` and sf classifier is availible on `localhost:8108/annotation` 
## Generic Responses
TBD
## Entity Detection
TBD
