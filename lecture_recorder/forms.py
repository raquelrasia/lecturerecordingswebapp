# coding: utf-8

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
import re
import datetime
from django.forms import extras

accepted_video_formats = ['mp4', 'mkv', 'ogv', 'webm']
accepted_audio_formats = ['mp3']

class RegistrationForm(forms.Form):
    username = forms.CharField(label = 'Nome de usuario', max_length = 30)
    first_name = forms.CharField(label = 'Nome', max_length = 30)
    last_name = forms.CharField(label = 'Sobrenome', max_length = 30)
    email = forms.EmailField(label = 'Email')
    password1 = forms.CharField(
        label = 'Senha',
        widget = forms.PasswordInput()
    )

    password2 = forms.CharField(
        label = 'Senha (Repita)',
        widget = forms.PasswordInput()
    )
    
    def clean_password2(self) :
        if 'password1' in self.cleaned_data:
            password1 = self.cleaned_data['password1']
            password2 = self.cleaned_data['password2']
            if (password1 == password2):
                return password2
        raise forms.ValidationError('Passwords inseridos sao diferentes')

    def clean_username(self) :
        username = self.cleaned_data['username']
        if not re.search(r'^\w+$', username):
            raise forms.ValidationError('Username deve conter apenas caracteres alfanumericos e undersocre')
        try:
            User.objects.get(username = username)
        except ObjectDoesNotExist:
            return username
        raise forms.ValidationError(' Username ja cadastrado')
        
class BookmarkSaveForm(forms.Form):
    url = forms.URLField(
        label = 'URL',
        widget = forms.TextInput(attrs = { 'size' : 64})
    )
    title = forms.CharField(
        label = 'Title',
        widget = forms.TextInput(attrs = { 'size' : 64})
    )
    tags = forms.CharField(
        label = 'Tags',
        required = False,
        widget = forms.TextInput(attrs = { 'size' : 64})
    )

class SearchForm(forms.Form):
    query = forms.CharField(
        label = 'Digite uma Palavra-Chave para buscar',
        widget = forms.TextInput( attrs = {'size' : 32})
    )

class CourseSaveForm(forms.Form):
    name = forms.CharField(
        label = 'Nome',
        widget = forms.TextInput(attrs = { 'size' : 128})
    )
    code = forms.CharField(
        label = 'Codigo',
        widget = forms.TextInput(attrs = { 'size' : 10})
    )

class VideoUploadForm(forms.Form):
    file = forms.FileField(
        label  = 'Escolha um arquivo de vídeo',
        required = False
    )
    audio_file = forms.FileField(
        label  = 'Escolha um arquivo de áudio',
        required = False
    )
    tags = forms.CharField(
        label = 'Tags',
        required = False,
        widget = forms.TextInput(attrs = { 'size' : 64})
    )
    date = forms.DateTimeField(
        widget = extras.SelectDateWidget(),
        initial= datetime.datetime.now(),
    )

    def clean_file(self):
        if 'file' in self.cleaned_data:
            file = self.cleaned_data['file']
            if file:
                filename = file.name
                extension = filename.split('.')[-1].lower()
                if extension in accepted_video_formats:
                    return file
                else:
                    raise forms.ValidationError("Arquivo de vîdeo inválido")
        else:
            if 'audio_file' not in self.cleaned_data:
                raise forms.ValidationError("Arquivo de áudio ou vídeo necessário")

    def clean_audio_file(self):
        if 'audio_file' in self.cleaned_data:
            file = self.cleaned_data['audio_file']
            if file:
                filename = file.name
                extension = filename.split('.')[-1].lower()
                if extension in accepted_audio_formats:
                    return file
                else:
                    raise forms.ValidationError("Arquivo de áudio inválido")
        else:
            if 'file' not in self.cleaned_data:
                raise forms.ValidationError("Arquivo de áudio ou vídeo necessário")

class VideoUploadForm_API(forms.Form):
    file = forms.FileField()
    tags = forms.CharField(required = False)
    date = forms.DateTimeField()
    course_code = forms.CharField()
    class_name = forms.CharField()
    class_year = forms.CharField()
    class_semester = forms.CharField()

class AudioUploadForm_API(forms.Form):
    file = forms.FileField()
    tags = forms.CharField(required = False)
    date = forms.DateTimeField()
    course_code = forms.CharField()
    class_name = forms.CharField()
    class_year = forms.CharField()
    class_semester = forms.CharField()

class LoginApiForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()
    
class ClassSaveForm(forms.Form):
    name = forms.CharField(
        label = 'Nome',
        widget = forms.TextInput(attrs = { 'size' : 4})
    )

    year = forms.IntegerField(
        label = 'Ano', 
        widget = forms.NumberInput(attrs = { 'size' : 4}),#, default = datetime.datetime.now().year),
    )

    semester = forms.CharField(
        label = 'Semester',
        widget = forms.TextInput(attrs = { 'size' : 1})
    )

    def clean_semester(self) :
        if 'semester' in self.cleaned_data:
            semester = self.cleaned_data['semester']
            if (semester == '1' or semester == '2'):
                return semester
        raise forms.ValidationError('Semestre Invalido')
