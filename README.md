# womchat backend
### Project scheme:
Client ---> Nginx (reverse proxy) -> Gunicorn (WSGI) -> Django (Application).

## setting up your VPS to run this project
We use Nginx as a reverse proxy, Gunicorn as WSGI, Django as an application server.
1. Install Nginx
```
sudo apt install nginx
```
2. Clone this repository
```
git clone https://github.com/CrazyDuck192/hackathon-project.git
```
3. Set up your virtual environment
```
cd hackathon-project
mkdir .venv
python3 -m venv ./.venv
source ./.venv/bin/activate
pip install -r requirements.txt
```
4. Set up Gunicorn
```
gunicorn -c conf/gunicorn_config.py api.wsgi
```

to be continued...
