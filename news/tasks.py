import logging
import feedparser

from celery import shared_task
from django.core.exceptions import ValidationError
from news.models import RssFeed,FeedEntry

from datetime import date, timedelta, datetime
from time import mktime
from django.core.mail import send_mail

from random import randint

@shared_task
def rss_scraper():
    """
        This task scrapes all RSS Feeds in the database and stores new FeedEntries. It also adds an expiry date
    """

    feeds = RssFeed.objects.all()

    for feed in feeds:
        feed_entries = feedparser.parse(feed.feed_url)

        for entry in feed_entries.entries:
            try:
                if FeedEntry.objects.get(uri=entry.link):
                    # log something, maybe? pass for now
                    pass
            except FeedEntry.DoesNotExist:
                today = date.today()
                if entry.get('published_parsed') is not None:
                    pub_date = date.fromtimestamp(mktime(entry.published_parsed))
                elif entry.get('date_parsed') is not None:
                    pub_date = date.fromtimestamp(mktime(entry.date_parsed))
                else:
                    pub_date = None

                if pub_date is not None:
                    if pub_date > today:
                        expire_on_date = pub_date
                    else:
                        expire_on_date = today + timedelta(days=7 + randint(0, 3))  # add some variation in expiry dates, so make it seem more natural

                # only store news that are no less than 62 days old
                if pub_date >= today - timedelta(days=62):
                    new_entry = FeedEntry(
                        uri=entry.link,
                        title=entry.get('title'),
                        description=entry.get('description'),
                        pub_date=pub_date,
                        expires_on=expire_on_date,
                        feed=feed,
                        category=feed.category
                    )

                    try:
                        new_entry.full_clean()
                        new_entry.save()
                    except ValidationError as verror:
                        # Add some form of error handling here
                        logging.error(verror)
                        print(verror)

    logging.info('scraped up news entries')


@shared_task
def news_cleanup():
    today = date.today()

    feed_entries_to_delete = FeedEntry.objects.filter(expires_on__lte=today)

    for entry in feed_entries_to_delete:
        entry.delete()

    logging.info('Cleaned up news entries')


@shared_task
def news_full_cleanup():

    feed_entries_to_delete = FeedEntry.objects.all()

    for entry in feed_entries_to_delete:
        entry.delete()

    logging.info('Fully Cleaned up news entries')
