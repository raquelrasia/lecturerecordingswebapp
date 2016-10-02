from django.contrib import admin
from .models import Course, Class, Video, Tag

admin.site.register(Course)
admin.site.register(Class)
admin.site.register(Video)
admin.site.register(Tag)

# Register your models here.
