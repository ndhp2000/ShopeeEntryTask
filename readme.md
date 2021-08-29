## Shopee Intership Entry Task 
To Deploy
```console
sudo sh deploy.sh
```
To create toy database
```console
sudo docker exec -it django-gunicorn python manage.py createdata
```

_**Warning:** The .env file is pushed for easy private deployment._
