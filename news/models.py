from django.db import models, IntegrityError
from django import forms
from django.contrib.auth.models import User

from wagtail.core.models import Page
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel

from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from datetime import date


# Create your models here.
class RssFeed(ClusterableModel):
    CATEGORIES = [
        ('evt', 'Events'),
        ('fid', 'Related FID'),
        ('job', 'Job Opportunities'),
        ('cfx', 'Call for Papers'),
        ('nws', 'News and Blog Articles'),
        ('oth', 'Miscellenious')
    ]
    feed_name = models.CharField(blank=False, max_length=1500)
    homepage = models.URLField(max_length=500, blank=False)
    feed_url = models.URLField(max_length=500, blank=False, unique=True)
    category = models.CharField(max_length=3, blank=False, choices=CATEGORIES, default='oth')

    panels = [
        FieldPanel('feed_name', heading="Name of the Instution or Feed"),
        FieldPanel('homepage', heading="Home Page of the Instution"),
        FieldPanel('feed_url', heading="URL of RSS Feed"),
        FieldPanel('category', widget=forms.Select, heading="Category to which the feed belongs. Choose one!"),
    ]

    def __str__(self):
        return f'{self.feed_name}'


class FeedEntry(ClusterableModel):
    uri = models.URLField(max_length=500, blank=False, unique=True)
    title = models.CharField(max_length=1500)
    description = RichTextField(blank=True, null=True)
    pub_date = models.DateField(blank=True, null=True)
    expires_on = models.DateField()
    feed = ParentalKey('RssFeed', related_name='feedentry_feed', on_delete=models.CASCADE)
    category = models.CharField(max_length=3, blank=False, choices=RssFeed.CATEGORIES, default="oth")

    panels = [
        FieldPanel('uri', heading='URL of the news entry'),
        FieldPanel('title', heading='Title of the news entry'),
        FieldPanel('description', heading='Teaser text of the news entry'),
        FieldPanel('pub_date', heading='Date of Publication'),
        FieldPanel('expires_on', heading='Date of invalidation, i.e. when the record gets deleted, should be between 7 and 10 days, or a deadline in the future.'),
        FieldPanel('feed', heading='To which Feed does this news entry belong?', widget=forms.Select),
        FieldPanel('category', widget=forms.Select, heading="Category to which the feed belongs. Choose one!"),
    ]

    def __str__(self):
        return self.title


class UserFeedEntry(ClusterableModel):
    submitter = models.ForeignKey(User, related_name='submitter', on_delete=models.CASCADE)
    submitter_email = models.EmailField(blank=False)
    submitter_name = models.CharField(max_length=255)
    uri = models.URLField(max_length=500, blank=False, unique=True)
    title = models.CharField(max_length=1500)
    description = RichTextField(blank=True, null=True)
    pub_date = models.DateField(blank=True, null=True)
    expires_on = models.DateField(null=True, default=None)
    feed = ParentalKey('RssFeed', related_name='userentry_feed', on_delete=models.CASCADE, null=True, default=None)
    category = models.CharField(max_length=3, blank=False, choices=RssFeed.CATEGORIES, default="oth")
    approved = models.BooleanField(default=False)

    panels = [
        FieldPanel('uri', heading='URL of the news entry'),
        FieldPanel('title', heading='Title of the news entry'),
        FieldPanel('description', heading='Teaser text of the news entry'),
        FieldPanel('pub_date', heading='Date of Publication'),
        FieldPanel('expires_on', heading='Date of invalidation, i.e. when the record gets deleted, should be between 7 and 10 days, or a deadline in the future.'),
        FieldPanel('feed', heading='To which Feed does this news entry belong?', widget=forms.Select),
        FieldPanel('category', widget=forms.Select, heading="Category to which the feed belongs. Choose one!"),
        FieldPanel('approved', heading='If this flag is set, a new Feed Entry will be created on save.')
    ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.approved and self.feed is not None:
            new_feedentry = FeedEntry.objects.create(
                uri=self.uri,
                title=self.title,
                description=self.description,
                pub_date=self.pub_date,
                expires_on=self.expires_on,
                feed=self.feed,
                category=self.category,
            )
            new_feedentry.save()

            print('approved')
            super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)


class SubmitForm(forms.Form):
    url = forms.URLField(max_length=500, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    title = forms.CharField(max_length=1500, widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    category = forms.ChoiceField(choices=RssFeed.CATEGORIES, widget=forms.Select(attrs={'class': 'form-select'}))


class NewsIndex(RoutablePageMixin, Page):
    """
        This page displays all FeedEntries in the database in chronological order.
    """
    parent_page_types = ['home.HomePage']
    subpage_types = []
    max_count = 1

    page_heading = models.CharField(max_length=100, blank=True, default='Some Heading')
    intro_text = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel('page_heading'),
        FieldPanel('intro_text'),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        context['news'] = dict()
        context['categories'] = dict()
        context['feeds'] = dict()
        for category_tag, category_name in RssFeed.CATEGORIES:
            context['feeds'][category_tag] = RssFeed.objects.filter(category=category_tag).order_by('feed_name')
            context['categories'][category_tag] = category_name
            context['news'][category_tag] = FeedEntry.objects.filter(category=category_tag).order_by('-pub_date')

        return context

    @login_required
    @route(r'^submit')
    def submit_entry(self, request, *args, **kwargs):
        context = {'page': self, 'form': SubmitForm()}

        if request.method == 'GET':
            return render(request=request, template_name='news/news_submit.html', context=context)
        else:
            form = SubmitForm(request.POST)
            if form.is_valid():
                try:
                    new_userentry = UserFeedEntry.objects.get_or_create(
                        submitter=request.user,
                        submitter_name=form.cleaned_data['name'],
                        submitter_email=form.cleaned_data['email'],
                        uri=form.cleaned_data['url'],
                        title=form.cleaned_data['title'],
                        description=form.cleaned_data['description'],
                        pub_date=date.today(),
                        category=form.cleaned_data['category']
                    )
                    new_userentry.save()
                except IntegrityError:
                    # Fail silently to avoid spam
                    pass
                context['success'] = True
                return render(request=request, template_name='news/news_submit.html', context=context)
            else:
                print('Form invalid')
                return redirect('/')
