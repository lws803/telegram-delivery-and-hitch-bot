# telegram-delivery-and-hitch-bot
Telegram bot for managing the matches between hitchers/ delivery customers and drivers.

## Description:
Bot will allow listings from both drivers and customers. Request entries are stored in a Mysql table while matches are stored in redis. Telegram handle will only be revealed to both parties once there is a match.

### Setup:
1. Install all necessary python requirements
```bash
pip install -r requirements.txt
```
2. Install redis-server and mysql
3. Setup the following environment variables
```bash
MYSQL_PROD
REDIS_PROD
TELE_KEY_PROD
GOOGLE_API_KEY  # For google maps
```
4. Run alembic script `alembic upgrade head`
5. Run the main service
```bash
python service.py
```
6. Run the cleanup service
```bash
python cleanup_service.py
```
