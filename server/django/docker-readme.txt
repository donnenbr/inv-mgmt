Docker commands:

to build:
sudo docker build -t inv-mgmt-django .

to run the container, exposing container port 8000 on host port 5000
sudo docker run -it --rm --name inv-mgmt-django --volume /home/bobby/inv-data:/usr/src/inv-data -p 5000:8000 inv-mgmt-django

docker images now stored on old 1tb drive

docker login is optimum acct and usual SW pwd


