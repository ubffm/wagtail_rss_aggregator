# wagtail_rss_aggregator
This application allows you to display aggregated rss feeds in your wagtail project

To display aggregated RSS-Feeds this app allows editors to put in RSS-Feeds to scrape via the backend and to categorize these feeds into categories defined by the developer (see below).

The entered Feeds are scraped via a [Django-Celery](https://docs.celeryproject.org/en/stable/django/first-steps-with-django.html) background task and cleaned up the same way. These tasks can be managed via the Django-Admin panel, using [Django Celery Beat](https://github.com/celery/django-celery-beat).

# Installation

Clone this repository and copy the ```news``` directory into your Wagtail Project.
Enable the app by adding it to your ```INSTALLED_APPS``` like so:
```python
INSTALLED_APPS = [
	...,
	'news',
	...,
	'django_celery_beat',
]
```
Afterwards, run ```python manage.py makemigrations``` to create the necessary migrations and ```python manage.py migrate``` to apply them to your database.

To use the background tasks, make sure you have ```django_celery_beat``` installed. Also make sure you have a working Celery worker and scheduler.

# Usage

This App adds a menu to your Wagtail CMS backend that allows you to simply enter new Feeds to scrape and even enter your own news by hand. All news entries belong to a feed however, so if you want to enter your own news, make sure to create at least a "dummy" feed for your own page. All news entries inherit their category from their respective feeds. They can however be changed in the menu.

All news entries have a specific expiry date. This is either a deadline read from the respective feed (in case there is one), or it is added during scraping. All news entries expire after 7 to 10 days (some randomization is added, to make expiry look more natural and not have large numbers of entries expire the same day).

Frontend users can can enter their own news (Calls for papers, etc.). These are stored in the database and have to be curated by and editor, i.e. have an expiry date added and be added to a (dummy) feed. If this feature is not desired, change ```news/models.py``` accordingly, by deleting the necessary code.

# Dependencies

- [Django Celery](https://docs.celeryproject.org/en/stable/django/first-steps-with-django.html)
- [Django Celery Beat](https://github.com/celery/django-celery-beat)
- [Wagtail CMS](https://wagtail.io)

# Environment

This App was tested on:

- Python 3.8, 3.9, 3.10
- Django 3.1, 3.2
- Wagtail 2.14, 2.15
- Django-Celery >= 2.2
- Celery 5.0.5