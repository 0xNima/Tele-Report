# Tele-Report
Analytics platform for Telegram Channels 🚧👷


## Getting Started

### Docker
clone repository and run docker
```
git clone https://github.com/0xNima/Tele-Report.git

cd Tele-Report

docker-compose up --build
```

### Standalone 
1- Install [redis](https://redis.io/topics/quickstart) and [postgreSQL](https://www.postgresql.org/download/) (it would be more generic in future, like using other cache and DBs)

2- clone repository and install requirements
```
git clone https://github.com/0xNima/Tele-Report.git

cd Tele-Report

virtualenv venv && source venv/bin/activate   # optional

cd telereport && pip3 install -r requirements.txt

```
3- Rename `.env-template` file to `.env` and edit values (you should get telegram api_id and api_hash from [Here](https://my.telegram.org/auth?to=apps)
```
mv .env-template .env
```

4- Run migrations to create tables
```
python3 manage.py makemigrations

python3 manage.py migrate
```

5- Run `main.py` script to gather admin logs and update message informations
```
python3 updater/main.py
```

6- Prepare admin panel
```
python3 manage.py runserver
```

### TODO List

- [x] Write script for gathering admin logs and message informations
- [x] Write queries for extracting useful data and statistics
- [x] Visuallizing data
- [x] Add log
- [x] Display Banlist
- [x] Dockerize
- [ ] Queue async actions to perform in background
- [ ] Get more information about members(if it is possible like display online members)
- [ ] Get more information about messages by click/hover on message charts
- [ ] Better visualization of data

