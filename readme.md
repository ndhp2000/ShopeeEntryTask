## Shopee Intership Entry Task 
To Deploy
```console
sudo sh deploy.sh
```
To create toy database
```console
sudo docker exec -it django-gunicorn python manage.py createdata
```
After deploying and creating toy database, test the app by connect to:
```127.0.0.1```

Login with username: admin[1-1000000] and password: admin. (use admin1/admin for example)

For administration, connect to ```127.0.0.1/form.html```

_**Warning:** The .env file is pushed for easy private deployment._
