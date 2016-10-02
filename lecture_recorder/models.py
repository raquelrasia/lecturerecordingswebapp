from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
import os
from tcc_project.settings import MEDIA_ROOT
from aux_funcs import get_course_class_path

class Profile(models.Model):  
    user = models.OneToOneField(User, on_delete=models.CASCADE)  
    #other fields here
    is_teacher=models.BooleanField(default = False)


# Create your models here.
class Link(models.Model):
    url = models.URLField(unique = True)
    
    def __str__(self):
        return self.url 


class Bookmark(models.Model):
    title = models.CharField(max_length = 200)
    user = models.ForeignKey(User)
    link = models.ForeignKey(Link)
    
    def __str__(self):
        return ("{}, {}".format(self.user.username, self.link.url))


class Course(models.Model):
    name = models.CharField(max_length = 200)
    code = models.CharField(max_length = 10)
    #class = models.ForeignKey(Class, null=True)
    #user_creator = models.ForeignKey(User)
    def __str__(self):
        return ("{}, {}".format(self.name, self.code))

class Class(models.Model):
    name = models.CharField(max_length = 4)
    year = models.PositiveIntegerField()
    #year = models.CharField(max_length = 4)
    semester = models.CharField(max_length = 1)
    course  = models.ForeignKey(Course, null = True)
    user_teacher = models.ForeignKey(User, null = True)

    def __str__(self):
        return ("{}, {}, {}".format(self.name, self.year, self.semester))

class Lecture(models.Model):
    date = models.DateField()
    date_name = models.CharField(max_length = 20)
    my_class = models.ForeignKey(Class)

    def __str__(self):
        return ("{}, {}".format(self.date, self.my_class.name))

class Video(models.Model):
    def get_video_upload_file_path(self, filename):
        classes = self.lecture.my_class
        course = self.lecture.my_class.course
        path = 'videos/' + get_course_class_path(course, self.lecture.my_class) + filename  
        self.name = filename
        self.path = path
        return path

    lecture = models.OneToOneField(Lecture, on_delete=models.CASCADE)
    file = models.FileField(upload_to = get_video_upload_file_path)
    name = models.CharField(max_length = 100)
    
    def __str__(self):
        return ("{}, {}".format(self.file.url, self.lecture))

class Audio(models.Model):
    def get_audio_upload_file_path(self, filename):
        classes = self.lecture.my_class
        course = self.lecture.my_class.course
        path = 'videos/' + get_course_class_path(course, self.lecture.my_class) + filename  
        self.audio_name = filename     
        return path
    
    lecture = models.OneToOneField(Lecture, on_delete=models.CASCADE)
    audio_file = models.FileField(upload_to = get_audio_upload_file_path)
    audio_name = models.CharField(max_length = 100)

class Tag(models.Model):
    name = models.CharField(max_length = 64, unique = True)
    lecture = models.ManyToManyField(Lecture)

    def __str__(self):
        return self.name

