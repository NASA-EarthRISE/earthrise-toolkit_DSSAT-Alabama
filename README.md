# DSSAT Web App - Alabama
## Setup and Installation
The installation described here will make use of conda to ensure there are no package conflicts with
existing or future applications on the machine.  It is highly recommended to use a dedicated environment
for this application to avoid any issues.

### Recommended
Conda (To manage packages within the application own environment)

### Environment
- Create the env

```commandline
conda env create -f environment.yml
```

Add a file named data.json in the base directory.  This file will hold a json object containing
the siteID for your application, SECRET_KEY, ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, ACCOUNT_DEFAULT_HTTP_PROTOCOL,
UPLOAD_ROOT, CACHE_LOCATION, DEBUG_ENABLED, and LOG_FILE.  
Both ALLOWED_HOSTS and CSRF_TRUSTED_ORIGINS can include multiple entries comma separated in the array.

The format will be:

```json
{
    "SECRET_KEY": "your-django-secret-key",
    "ALLOWED_HOSTS": ["your-host"],
    "CSRF_TRUSTED_ORIGINS": ["https://app-url"],
    "ACCOUNT_DEFAULT_HTTP_PROTOCOL": "http-or-https",
    "DBUSER": "database-user",
    "USERNAME": "your-database-name",
    "PASSWORD": "your-database-password",
    "HOST": "your-database-host",
    "HTTP_HTTPS": "your-http-prototcol",
    "DEBUG": false
}
```

- enter the environment

```shell
conda activate DssatWeb
```
- Install dssat_service and spatialDSSAT by going into respective directories and running the following command

```shell
pip install . e
```

At this point you should be able to start the application.  From the root directory you can run the following command

```shell
python manage.py runserver
```

Note: These instructions are for development only.