![Logo](https://raw.githubusercontent.com/ClaudiuGeorgiu/miniCAP/master/docs/logo/logo.png)

> A simple and minimal microservice for generating and validating CAPTCHA.

[![Codacy](https://app.codacy.com/project/badge/Grade/f0c8737e04c045269e23f8a35735c7d7)](https://app.codacy.com/gh/ClaudiuGeorgiu/miniCAP)
[![Ubuntu Build Status](https://github.com/ClaudiuGeorgiu/miniCAP/actions/workflows/ubuntu.yml/badge.svg)](https://github.com/ClaudiuGeorgiu/miniCAP/actions/workflows/ubuntu.yml)
[![Windows Build Status](https://github.com/ClaudiuGeorgiu/miniCAP/actions/workflows/windows.yml/badge.svg)](https://github.com/ClaudiuGeorgiu/miniCAP/actions/workflows/windows.yml)
[![MacOS Build Status](https://github.com/ClaudiuGeorgiu/miniCAP/actions/workflows/macos.yml/badge.svg)](https://github.com/ClaudiuGeorgiu/miniCAP/actions/workflows/macos.yml)
[![Code Coverage](https://codecov.io/gh/ClaudiuGeorgiu/miniCAP/badge.svg)](https://codecov.io/gh/ClaudiuGeorgiu/miniCAP)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-green.svg?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/ClaudiuGeorgiu/miniCAP/blob/master/LICENSE)



**miniCAP** is a simple microservice, written in Python, with only two REST endpoints:
one for creating CAPTCHAs (`/api/captcha/generate/`) and one for verifying them
(`/api/captcha/validate/`).



## ❱ Demo

Some random samples of CAPTCHAs generated with miniCAP:

|                                                    |                                                          Light theme                                                          |                                                          Dark theme                                                          |
|:--------------------------------------------------:|:-----------------------------------------------------------------------------------------------------------------------------:|:----------------------------------------------------------------------------------------------------------------------------:|
|                     Only text                      |    ![CAPTCHA](https://raw.githubusercontent.com/ClaudiuGeorgiu/miniCAP/master/docs/demo/img/light.png)<br/>**wFKdfr**<br/>    |    ![CAPTCHA](https://raw.githubusercontent.com/ClaudiuGeorgiu/miniCAP/master/docs/demo/img/dark.png)<br/>**N9sx2G**<br/>    |
|            Text +<br/>background noise             |  ![CAPTCHA](https://raw.githubusercontent.com/ClaudiuGeorgiu/miniCAP/master/docs/demo/img/light_bg.png)<br/>**A4G9bu**<br/>   |  ![CAPTCHA](https://raw.githubusercontent.com/ClaudiuGeorgiu/miniCAP/master/docs/demo/img/dark_bg.png)<br/>**D46JLk**<br/>   |
|            Text +<br/>foreground noise             |  ![CAPTCHA](https://raw.githubusercontent.com/ClaudiuGeorgiu/miniCAP/master/docs/demo/img/light_fg.png)<br/>**Sx6pU7**<br/>   |  ![CAPTCHA](https://raw.githubusercontent.com/ClaudiuGeorgiu/miniCAP/master/docs/demo/img/dark_fg.png)<br/>**3mtNKE**<br/>   |
| Text +<br/>background noise +<br/>foreground noise | ![CAPTCHA](https://raw.githubusercontent.com/ClaudiuGeorgiu/miniCAP/master/docs/demo/img/light_bg_fg.png)<br/>**MdEMFd**<br/> | ![CAPTCHA](https://raw.githubusercontent.com/ClaudiuGeorgiu/miniCAP/master/docs/demo/img/dark_bg_fg.png)<br/>**95ScZ5**<br/> |



## ❱ Installation

There are two ways of getting a working copy of miniCAP on your own computer: either
by [using Docker](#docker-image) or by [using directly the source code](#from-source)
in a `Python 3` (at least `3.10`) environment. In both cases, the first thing to do is
to get a local copy of this repository, so open up a terminal in the directory where you
want to save the project and clone the repository:

```Shell
$ git clone https://github.com/ClaudiuGeorgiu/miniCAP.git
```

### Docker image

----------------------------------------------------------------------------------------

#### Prerequisites

This is the suggested way of installing miniCAP, since the only requirement is to have
a recent version of Docker installed:

```Shell
$ docker --version
Docker version 28.0.1, build 068a01e
```

#### Official Docker Hub image

The [official miniCAP Docker image](https://hub.docker.com/r/claudiugeorgiu/minicap)
is available on Docker Hub (automatically built from this repository):

```Shell
$ # Download the Docker image.
$ docker pull claudiugeorgiu/minicap
$ # Give it a shorter name.
$ docker tag claudiugeorgiu/minicap minicap
```

#### Install

If you downloaded the official image from Docker Hub, you are ready to use the service,
otherwise execute the following command in the previously created `miniCAP/` directory
(the folder containing the `Dockerfile`) to build the Docker image:

```Shell
$ # Make sure to run the command in miniCAP/ directory.
$ # It will download and install all the project's dependencies.
$ docker build -t minicap .
```

#### Start miniCAP

miniCAP is now ready to be used, run the following command to start the service on port
`8000`:

```Shell
$ docker run --rm -p 8000:8000 minicap
```

miniCAP microservice is now running, see the [usage instructions](#-usage) for more
information.

### From source

----------------------------------------------------------------------------------------

#### Prerequisites

The only requirement of this project is [uv](https://github.com/astral-sh/uv).

#### Install

Run the following commands in the main directory of the project (`miniCAP/`) to
install the needed dependencies:

```Shell
$ # Make sure to run the command in miniCAP/ directory.
$ uv sync --frozen --no-dev
```

#### Start miniCAP

miniCAP is now ready to be used, run the following command to start the service on port
`8000`:

```Shell
$ # Make sure to run the command in miniCAP/ directory.
$ uv run --frozen -m minicap.main
```

miniCAP microservice is now running, see the [usage instructions](#-usage) for more
information.



## ❱ Usage

When miniCAP microservice is running, it exposes only two REST endpoints for interacting
with CAPTCHAs:

* `POST` `/api/captcha/generate/` - returns a new CAPTCHA image in the response body
(of type `image/png`) and a `Captcha-Id` header needed to validate the CAPTCHA. This
endpoint needs `POST` instead of `GET` requests because every request generates a new
`Captcha-Id` that is saved into the database (`GET` requests should be idempotent).

* `POST` `/api/captcha/validate/` - validates a CAPTCHA by accepting a request
containing a previously generated `Captcha-Id` and the text displayed in the CAPTCHA.
The request must be a JSON containing a text field `id` with the value of `Captcha-Id`
header and a text field `text` with the solution of the CAPTCHA.

> [!TIP]  
> While the microservice is running, the complete REST OpenAPI documentation is
> available at <http://localhost:8000/docs>.

> [!NOTE]  
> Each CAPTCHA is deleted from the database after:
> * 10 minutes since its creation
> * a successful validation
> * 3 unsuccessful validation requests

#### Example usage with `curl`

1. Request the generation of a new CAPTCHA image and save the result into a file
(e.g., `CAPTCHA.png`). Take note of the value of `Captcha-Id` response header, as it
will be needed later for the validation request:
   ```Shell
   $ curl -v -s -X POST "http://localhost:8000/api/captcha/generate/" --output CAPTCHA.png
   * ...
   < HTTP/1.1 200 OK
   < captcha-id: 1cc70567-8124-40f8-ba74-062c896f1535
   < ...
   ```

2. Open the file with the CAPTCHA and solve it (e.g., the image displays the string
`X575u6`).

3. Send the CAPTCHA solution and the value of `Captcha-Id` header back to the server for
validation:
   ```Shell
   $ curl -X POST "http://localhost:8000/api/captcha/validate/" \
      -H "Content-Type: application/json" \
      -d '{
        "id": "1cc70567-8124-40f8-ba74-062c896f1535",
        "text": "X575u6"
      }'
   {"status":200,"message":"CAPTCHA validated successfully"}%
   ```

#### Example usage with `Python`

```Python
import requests

# 1. Generate CAPTCHA and retrieve its id from Captcha-Id header.
res = requests.post("http://localhost:8000/api/captcha/generate/")
res.raise_for_status()
captcha_id = res.headers.get("Captcha-Id")
with open("CAPTCHA.png", "wb") as img:
    img.write(res.content)

# 2. Open CAPTCHA image and solve it.
solution = "captcha solution here"

# 3. Validate CAPTCHA.
res = requests.post(
    "http://localhost:8000/api/captcha/validate/",
    json={"id": captcha_id, "text": solution},
)
res.raise_for_status()
```



## ❱ Test

Run the following command in the main directory of the project (`miniCAP/`) to also
install test dependencies (needed only the first time):

```Shell
$ uv sync --frozen
```

Then run the following command to execute the automatic test suite:

```Shell
$ uv run --frozen pytest --verbose
```



## ❱ Contributing

Questions, bug reports and pull requests are welcome on GitHub at
[https://github.com/ClaudiuGeorgiu/miniCAP](https://github.com/ClaudiuGeorgiu/miniCAP).



## ❱ License

You are free to use this code under the
[MIT License](https://github.com/ClaudiuGeorgiu/miniCAP/blob/master/LICENSE).
