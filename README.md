# *eosapy*

*EOS API sample*

## *DOCKER Build*:
  
  Once cloned, enter repository dir and execute:
  ```bash
  $ docker build -t geoapi:latest .
  >... (geoapi must be builded)
  $ docker images
  >... list of images (geoapi listed)
  $ docker run -p 5000:5000 geoapi
  >... server output
  ```
## *Python virtualenv Build*:
  
  OS Requirements:
  * Python=>3.10
  * Pip=>22.0.2
  * virtualenv => A guide to install and create envs: [Virtualenv Python](https://gist.github.com/Geoyi/d9fab4f609e9f75941946be45000632b)
  
  Activate created venv and execute (on geoapi path):
   ```bash
  $ pip install -r requirements.txt
  >... (Dependecies must be installed)
  $ python eosapy.py
  >... eosapy output
  ```
  
## *Usage*:
    API built in Python with Flask as entry point. Routes in this api indicates the operation or process to execute:
    * Catalog (http://localhost/pruebaeos/catalog)
    * Download (http://localhost/pruebaeos/download)

