#coding: utf-8
from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect 
from django.template import RequestContext
from django.template.loader import get_template
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, get_object_or_404
from lecture_recorder.forms import *
from lecture_recorder.models import *
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from xml_handler import *
import os
from tcc_project.settings import MEDIA_ROOT
from django.utils.encoding import smart_str

# Create your views here.
def main_page(request):
    return render_to_response(
        'main_page.html', RequestContext(request),
    )

def user_page(request, username):
    try:
        user = User.objects.get(username = username)
    except:
        raise Http404('Requested user not found.')

    classes = user.class_set.all()
    for my_class in classes: 
        course = my_class.course
        print(course.code)

    variables = RequestContext (request, {
        'username' : username,
        'classes': classes,
        'show_tags' : True,
    })      
    return render_to_response('user_page.html', variables)

def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')


def register_page(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username = form.cleaned_data["username"],
                password = form.cleaned_data["password1"],
                email = form.cleaned_data["email"],
                first_name = form.cleaned_data["first_name"],
                last_name = form.cleaned_data["last_name"],
            )

            if not '@alunos' in form.cleaned_data["email"] and 'utfpr' in form.cleaned_data["email"]:
                is_teacher =  True
            else:
                is_teacher =  False

            profile = Profile(user = user,
                              is_teacher = is_teacher)
            profile.save()
            user.save()
            return HttpResponseRedirect('/register/success')
    else:
        form = RegistrationForm()

    variables = RequestContext(request, 
        {
            'form' : form,
        }
    )

    return render_to_response(
        'registration/register.html',
        variables
    )

# @login_required(login_url = '/login/')
# def bookmark_save_page(request):
#     if request.method == 'POST':
#         form = BookmarkSaveForm(request.POST)
#         if form.is_valid():
#             bookmark = _bookmark_save(request, form)
#             return HttpResponseRedirect(
#                 '/user/%s' % request.user.username
#             )   
#     elif request.GET.has_key('url'):
#         url = request.GET['url']
#         title = ''
#         tags = ''
#         try:
#             link = Link.objects.get(url = url)
#             bookmark = Bookmark.objects.get(
#                 link = link,
#                 user = request.user,
#             )
#             title =  bookmark.title
#             tags = ' '.join(
#                 tag.name for tag in bookmark.tag_set.all()
#             )
#         except ObjectDoesNotExist:
#             pass

#         form = BookmarkSaveForm(
#             {
#                 'url' : url,
#                 'title' : title,
#                 'tags' : tags,
#             }
#         )
#     else:
#         form = BookmarkSaveForm()

#     variables = RequestContext(request, 
#         {
#             'form' : form,
#         }
#     )
#     return render_to_response('bookmark_save.html', variables)

def tag_page(request, tag_name):
    tag = get_object_or_404(Tag, name = tag_name)
    bookmarks = tag.bookmarks.order_by('-id')
    variables= RequestContext(request,{
        'bookmarks' : bookmarks,
        'tag_name' : tag_name,
        'show_tags' : True,
        'show_user' : True,
        }
    )
    return render_to_response('tag_page.html', variables)

def tag_cloud_page(request):
    MAX_WEIGHT = 5
    tags = Tag.objects.order_by('name')
    my_tag = tags[0]
    min_count = max_count = tags[0].bookmarks.count()
    for tag in tags:
        tag.count = tag.bookmarks.count()
        if  tag.count < min_count:
            min_count = tag.count()
        if max_count < tag.count:
            max_count = tag.count

    my_range = float(max_count - min_count)
    if my_range == 0.0:
        my_range = 1.0  
    for tag in tags:        
        tag.weight = int(MAX_WEIGHT * (tag.count - min_count)/my_range) 

    variables = RequestContext(request, {       
        'tags' : tags       
        }
    )

    return render_to_response('tag_cloud_page.html', variables)

def search_page(request):
    form = SearchForm()
    course = []
    show_results = False
    if request.GET.has_key('query'):
        show_results = True
        query = request.GET['query'].strip()
        if query:
            form = SearchForm({'query' : query})
            course = \
                Course.objects.filter(Q(name__icontains = query) | Q(code__icontains = query))[:10]

    variables = RequestContext(request, {
            'form' : form,
            'course' : course,
            'show_results' : show_results,
            'show_tags': True,
            'show_user': True,
            }
    )
    if request.GET.has_key('ajax'):
        return render_to_response('course_list.html', variables)
    else:
        return render_to_response('search.html', variables)

@login_required(login_url = '/login/')
def course_save_page(request):
    ajax = request.GET.has_key('ajax')
    if request.method == 'POST':
        form = CourseSaveForm(request.POST)
        if form.is_valid():
            course = _course_save(request, form)
            if ajax:
                variables = RequestContext (request, {
                    'course' : [course],
                    'show_edit' : True,
                })      
                return render_to_response('course_list_page.html', variables)
            else:   
                return HttpResponseRedirect(
                    '/class/%s' % course.code
                )   
        else: 
            if ajax:
                return HttpResponse('failure')

    elif request.GET.has_key('code'):
        code = request.GET['code']
        name = ''
        try:
            course = Course.objects.get(code = code)
            name =  course.name
        except ObjectDoesNotExist:
            pass
        form = CourseSaveForm(
            {
                'name' : name,
                'code' : code,
            }
        )
    else:
        form = CourseSaveForm()

    variables = RequestContext(request, 
        {
            'form' : form,
        }
    )
    if ajax:
        return render_to_response('course_save_form.html', variables)
    else:
        return render_to_response('course_save.html', variables)


def handle_uploaded_file(f, dest_name):
    vector = [1, 2, 3, 4]
    chunk_size = 64*1024
    chunk_idx = 0
    total_chunks = f.size/chunk_size

    if not os.path.exists(os.path.dirname(dest_name)):
            os.makedirs(os.path.dirname(dest_name))

    with open(MEDIA_ROOT + dest_name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
            percent = (chunk_idx*100/total_chunks)
            print("uploading", str(percent) + "%")
            chunk_idx = chunk_idx + 1

def video_audio_upload_page(request, course_code, class_name, class_year, class_semester):
    has_video = False
    has_audio = False
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                course = Course.objects.get(code = course_code)
                my_class = course.class_set.get(name = class_name,
                                               year = class_year,
                                               semester = class_semester); 
                
            except:
                raise Http404('Turma não encontrada')
            #try:
            if(True):
                lecture, lecture_created = Lecture.objects.get_or_create(date = form.cleaned_data['date'],
                                            date_name= str(form.cleaned_data['date'].strftime('%d-%m-%Y')),
                                            my_class = my_class) 
                lecture.my_class = my_class
                my_class.save()

                #Video File 
                if request.FILES.has_key('file'):
                    has_video = True
                    file = request.FILES['file']
                    if not lecture_created and hasattr(lecture, 'video'):
                        video = lecture.video
                        if os.path.exists(lecture.video.file.path):
                            os.remove(lecture.video.file.path)
                            remove_video_from_xml(video)
                        video.file = file
                    else:
                        video = Video(file = file, lecture = lecture)
                
                    #dest_path = video.get_video_upload_file_path(video.file.name)
                    #handle_uploaded_file(video.file, dest_path)
                    video.save()

                #Audio File
                if request.FILES.has_key('audio_file'): 
                    has_audio = True
                    audio_file =  request.FILES['audio_file']
                    if not lecture_created and hasattr(lecture, 'audio'):
                        audio = lecture.audio
                        if os.path.exists(lecture.audio.audio_file.path):
                            os.remove(lecture.audio.audio_file.path)
                            remove_audio_from_xml(audio)
                        audio.audio_file = audio_file
                    else:
                        audio = Audio(audio_file = audio_file, lecture = lecture)
                    audio.save()  
                lecture.save()
            #except:
            #   raise Http404('Erro ao criar Aula')

            tag_names = form.cleaned_data['tags'].split()
            for tag_name in tag_names:
                tag = Tag.objects.get_or_create(
                    name = tag_name
                )
                #lecture.tag_set.add(tag)

            #adiciona video ao arquivo xml da class
            if has_video:
                add_video_to_xml(video)
            if has_audio:
                #dest_path = audio.get_audio_upload_file_path(audio.audio_file.name)
                #handle_uploaded_file(audio.audio_file, dest_path)
                add_audio_to_xml(audio)


            return HttpResponseRedirect(
                '/class/%s' % course.code
            )
    else:
        form = VideoUploadForm()

    variables = RequestContext(request, 
        {
            'form' : form,
        }
    )
    return render_to_response('video_audio_upload.html', variables)


def course_page(request, course_code):
    show_button = False
    try:
        course = Course.objects.get(code = course_code)
        show_button = request.user.profile.is_teacher;
    except:    
        raise Http404('Disciplina nao encontrada.')
    classes = course.class_set.all()
    #videos = course.video_set.all()
    variables = RequestContext (request, {
        'course' : course,
        'classes': classes,
        'show_tags': False,
        'show_button' : show_button
    })      
    return render_to_response('course_page.html', variables)


def course_list_page(request):
    course = Course.objects.all() 
    variables = RequestContext (request, {
        'course' : course,
        'show_edit' : True,
    })      
    return render_to_response('course_list_page.html', variables)

# def _bookmark_save(request, form):
#     #Create or get a link
#     link, dummy = Link.objects.get_or_create(
#         url = form.cleaned_data['url']
#     )
#     #Create or get a bookmark
#     bookmark, created = Bookmark.objects.get_or_create(
#         user = request.user,
#         link = link,
#     )   
#     bookmark.title = form.cleaned_data['title']
#     if not created:
#         bookmark.tag_set.clear()

#     tag_names = form.cleaned_data['tags'].split()
#     for tag_name in tag_names:
#         tag, dummy = Tag.objects.get_or_create(
#             name = tag_name
#         )
#         bookmark.tag_set.add(tag)
#         #tag.bookmarks.add(bookmark)
#     bookmark.save()
#     return bookmark


def _course_save(request, form):
    course, created = Course.objects.get_or_create(
        code = form.cleaned_data['code'],
        #user_creator = request.user,
    )
    course.name = form.cleaned_data['name']
    course.save()
    return course

def class_save_page(request, course_code):
    course =  Course.objects.get(code = course_code)
    if course:
        if request.method == 'POST':
            form = ClassSaveForm(request.POST, request.FILES)
            if form.is_valid():
                my_class, created = Class.objects.get_or_create(name = form.cleaned_data['name'],
                                                                year = form.cleaned_data['year'], 
                                                                semester = form.cleaned_data['semester'])
                                                                                                                       
                                                             
                # my_class = Class(name = form.cleaned_data['name'])
                # my_class.year = form.cleaned_data['year']
                # my_class.semester = form.cleaned_data['semester']
                if created:
                    course.class_set.add(my_class)
                    my_class.user_teacher = request.user
                    my_class.save()
                    #caso seja professorclass_set
                    create_xml_teacher_file(request.user)
                    add_course_class(course, my_class, request.user)
                    return HttpResponseRedirect(
                            '/class/{}/{}/{}/{}/'.format(course_code, my_class.name, my_class.year, my_class.semester)
                        )
                else:
                    form = ClassSaveForm() 
        else:
            form = ClassSaveForm()
        variables = RequestContext(request, 
            {
                'course' : course,
                'form' : form,
            }
        )
        return render_to_response('class_save.html', variables)          
    else:
        return HttpResponseRedirect('/')

def class_page(request, course_code, class_code, class_year, class_semester):
    try:
        course = Course.objects.get(code = course_code)
    except:
        raise Http404('Disciplina nao encontrada.')

    try:
        my_class = course.class_set.get(name = class_code, 
                                        year = class_year,
                                        semester = class_semester)
    except:
        raise Http404('Turma nao encontrada.')

    lectures = my_class.lecture_set.all()
    class_teacher = False

    if my_class in request.user.class_set.all():
        class_teacher = True

    variables = RequestContext (request, {
        'course': course,
        'class': my_class,
        'lectures' : lectures,
        'is_class_teacher' : class_teacher,
    })      
    return render_to_response('class_page.html', variables)


def lecture_page(request, course_code, class_code, class_year, class_semester, lecture_date):
    try:
        course = Course.objects.get(code = course_code)
    except:
        raise Http404('Disciplina nao encontrada.')

    try:
        my_class = course.class_set.get(name = class_code, 
                                        year = class_year,
                                        semester = class_semester)
    except:
        raise Http404('Turma nao encontrada.')


    try:
        lecture = my_class.lecture_set.get(date_name = lecture_date)
    except:
        raise Http404('Aula nao encontrada.')

    variables = RequestContext (request, {
        'lecture' : lecture,
    })      
    return render_to_response('lecture_page.html', variables)



def index(request):
    response = JsonResponse({'foo':'bar'})
    # Get the number of visits to the site.
    # We use the COOKIES.get() function to obtain the visits cookie.
    # If the cookie exists, the value returned is casted to an integer.
    # If the cookie doesn't exist, we default to zero and cast that.
    visits = request.session.get('visits')

    reset_last_visit_time = False
 
    # Does the cookie last_visit exist?
    if 'last_visit' in request.COOKIES:
        # Yes it does! Get the cookie's value.
        last_visit = request.COOKIES['last_visit']
        # Cast the value to a Python date/time object.
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        # If it's been more than a day since the last visit...
        #if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
            # ...and flag that the cookie last visit needs to be updated
        reset_last_visit_time = True
    else:
        print('nenhuma visita anterior')
        # Cookie last_visit doesn't exist, so flag that it should be set.
        reset_last_visit_time = True

    if reset_last_visit_time:
        response.set_cookie('last_visit', datetime.now())
        response.set_cookie('visits', visits)

    # Return response back to the user, updating any cookies that need changed.
    return response


def video_view_page(request, path):
    video_url= path
    variables = RequestContext (request, {
        'video_url': video_url,
    })      
    return render_to_response('video_view.html', variables)

def audio_view_page(request, path):
    audio_url= path
    variables = RequestContext (request, {
        'audio_url': audio_url,
    })      
    return render_to_response('audio_view.html', variables)


"""
################################################################################################
#                                           API FUNCTIONS                                      #
################################################################################################
"""
#@login_required(login_url = '/login/')
@csrf_exempt
def api_video_upload(request):
    if request.method == 'POST':
        form = VideoUploadForm_API(request.POST, request.FILES)
        if form.is_valid():
            try:
                course = Course.objects.get(
                        code = form.cleaned_data['course_code']
                    )
            except:             
                response = JsonResponse({'state': 'class does not exist'})
                return response

            try:
                my_class = course.class_set.get(
                        name = form.cleaned_data['class_name'],
                        semester = form.cleaned_data['class_semester'],
                        year = form.cleaned_data['class_year'],
                    )
                lecture, lecture_created = Lecture.objects.get_or_create(date = form.cleaned_data['date'],
                                                                date_name= str(form.cleaned_data['date'].strftime('%d-%m-%Y')), 
                                                                my_class = my_class)
            except:
                response = JsonResponse({'state': 'class does not exist'})
                return response

            if form.cleaned_data.has_key('tags'):
                tag_names = form.cleaned_data['tags'].split()
                for tag_name in tag_names:
                    tag, dummy = Tag.objects.get_or_create(
                        name = tag_name
                    )

            #Video File 
            if request.FILES.has_key('file'):
                has_video = True
                file = request.FILES['file']
                if not lecture_created and hasattr(lecture, 'video'):
                    video = lecture.video
                    if os.path.exists(lecture.video.file.path):
                        os.remove(lecture.video.file.path)
                        remove_video_from_xml(video)
                    video.file = file
                else:
                    video = Video(file = file, lecture = lecture)

                video.save()
                add_video_to_xml(video)
                lecture.save()
                response = JsonResponse({'state': 'video uploaded'})
        else:
            response = JsonResponse({'state': 'invalid form'})
        return response
    else:
        response = JsonResponse({'state': 'no gets allowed'})
        return HttpResponseRedirect('/')

@csrf_exempt
def api_audio_upload(request):
    if request.method == 'POST':
        form = AudioUploadForm_API(request.POST, request.FILES)
        if form.is_valid():
            try:
                course = Course.objects.get(
                        code = form.cleaned_data['course_code']
                    )
            except:             
                response = JsonResponse({'state': 'class does not exist'})
                return response
            try:
                my_class = course.class_set.get(
                        name = form.cleaned_data['class_name'],
                        semester = form.cleaned_data['class_semester'],
                        year = form.cleaned_data['class_year'],
                    )
            except:
                response = JsonResponse({'state': 'class does not exist'})
                return response
            try:
                lecture, lecture_created = Lecture.objects.get_or_create(date = form.cleaned_data['date'],
                                        date_name= str(form.cleaned_data['date'].strftime('%d-%m-%Y')), 
                                        my_class = my_class)
            except: 
                response = JsonResponse({'state': 'error in creating class'})
                return response

            if form.cleaned_data.has_key('tags'):
                tag_names = form.cleaned_data['tags'].split()
                for tag_name in tag_names:
                    tag, dummy = Tag.objects.get_or_create(
                        name = tag_name
                    )
            #Audio File 
            if request.FILES.has_key('file'):
                has_video = True
                file = request.FILES['file']
                if not lecture_created and hasattr(lecture, 'audio'):
                    print('new lecture!!! kkk')
                    audio = lecture.audio
                    if os.path.exists(lecture.audio.audio_file.path):
                        os.remove(lecture.audio.audio_file.path)
                        remove_audio_from_xml(audio)
                    audio.audio_file = file
                else:
                    audio = Audio(audio_file = file, lecture = lecture)
                audio.save()
                add_audio_to_xml(audio)
                lecture.save()
                response = JsonResponse({'state': 'audio uploaded'})
        else:
            response = JsonResponse({'state': 'invalid form'})
        return response
    else:
        response = JsonResponse({'state': 'no gets allowed'})
        return HttpResponseRedirect('/')

#@login_required(login_url = '/login/')
@csrf_exempt
def api_return_teacher_info(request):
    response = HttpResponse()
    if request.GET.has_key('teacher_username'):
        user_name = request.GET['teacher_username']
    else:
        response.text = 'invalid username'
        return response

    file_name = MEDIA_ROOT + '/teachers/' + user_name + '.xml'
    if os.path.exists(file_name):
        xml_file = open(file_name, 'r')
        path_to_file = os.path.dirname(file_name)
        response = HttpResponse(xml_file.read() ,content_type='application/xml') # mimetype is replaced by content_type for django 1.7
        response['Content-Disposition'] = 'attachment; filename=%s' % file_name
        response['Content-Length'] = os.path.getsize(file_name)
        xml_file.close()
    else:
        response = HttpResponse("-1")
    return response

@csrf_exempt
def api_login(request):
    if request.method == 'POST':
        form = LoginApiForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.has_key('username') and form.cleaned_data.has_key('password'):
                    username = form.cleaned_data['username']
                    password = form.cleaned_data['password']
                    user = authenticate(username=username, password=password)
                    if user is not None:
                        #autenticacao correta
                        return HttpResponse(1)
                    else:
                        #autenticacao incorreta
                        return HttpResponse(-1)

    return HttpResponse(0)

@csrf_exempt
def api_return_videos_file(request):
    get_user = True
    now = datetime.datetime.now()
    test = now.month/3 + now.day
    try:
        course_code = request.GET['course_code']
        class_name = request.GET['class_name']
        class_year = request.GET['class_year']
        class_semester = request.GET['class_semester']
        username = request.GET['username']
        if user_name == 'unsyncd' + str(test):
            get_user = False
    except:
        response = HttpResponse('invalid params')
        return response
    try:
        course = Course.objects.get(code = course_code)
        my_class = course.class_set.get(name = class_name,
                                        year = class_year,
                                        semester = class_semester)
        if get_user:
            user = User.objects.get(username = username)
    except:
         response = HttpResponse('invalid params')

    if get_user:
        if my_class not in user.class_set.all():
            response = HttpResponse('invalid teacher')
            return response

    file_name = MEDIA_ROOT + '/videos/'  + get_course_class_path(course, my_class)
    names_split = file_name.split('/')
    name = names_split[-2] + names_split[-1]
    file_name =  file_name + name + '.xml' 
    if not os.path.exists(file_name):
        create_xml_video_file(course, my_class)
    print(file_name)
    if(os.path.exists(file_name)):
        xml_file = open(file_name, 'r')
        response = HttpResponse(xml_file.read() , content_type='application/xml') # mimetype is replaced by content_type for django 1.7
        response['Content-Disposition'] = 'attachment; filename=%s' % file_name
        response['Content-Length'] = os.path.getsize(file_name)
        xml_file.close()
        return response
    else:
        response = HttpResponse('invalid xml')