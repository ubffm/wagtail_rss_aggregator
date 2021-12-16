from wagtail.contrib.modeladmin.options import (
    ModelAdmin, ModelAdminGroup, modeladmin_register)

from news.models import RssFeed, FeedEntry, UserFeedEntry


class RssFeedAdmin(ModelAdmin):
    model = RssFeed
    menu_label = 'Rss Feeds to harvest'  # ditch this to use verbose_name_plural from model
    menu_icon = 'placeholder'  # change as required
    list_display = ('feed_name', 'feed_url', 'homepage', 'category')
    search_fields = ('feed_name',)


class FeedEntryAdmin(ModelAdmin):
    model = FeedEntry
    mdenu_label = 'Entries in News'
    menu_icon = 'placeholder'
    list_display = ('category', 'title', 'expires_on')


class UserFeedEntryAdmin(ModelAdmin):
    model = UserFeedEntry
    mdenu_label = 'Entries in News'
    menu_icon = 'placeholder'
    list_display = ('pub_date', 'submitter', 'category', 'title', 'approved')


class RegisterGroup(ModelAdminGroup):
    menu_label = 'RSS Harvester'
    menu_icon = 'placeholder'  # change as required
    menu_order = 300  # will put in 4th place (000 being 1st, 100 2nd)
    items = (RssFeedAdmin, FeedEntryAdmin, UserFeedEntryAdmin)


# When using a ModelAdminGroup class to group several ModelAdmin classes together,
# you only need to register the ModelAdminGroup class with Wagtail:
modeladmin_register(RegisterGroup)