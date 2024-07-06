from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Listings, Bid, Comment

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Listings)
admin.site.register(Bid)
admin.site.register(Comment)