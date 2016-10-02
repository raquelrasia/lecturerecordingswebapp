import xml.etree.cElementTree as ET
try:
    from tcc_project.settings import MEDIA_ROOT
except:
    from includes import MEDIA_ROOT
import os
import datetime
from xml.dom import minidom
from lecture_recorder.models import *

def get_course_class_path(course, my_class):
    path = course.code +'/'+ my_class.name + '/' + str(my_class.year) + '_' + my_class.semester + '/'
    return path

def get_videos_xml_name(course, my_class):
    path = MEDIA_ROOT +'/videos/'+ get_course_class_path(course, my_class)
    names_split = path.split('/')
    name = names_split[-2] + names_split[-1]
    fname =  path + name + '.xml'
    return fname

def create_xml_video_file(course, my_class): 
    fname =  get_videos_xml_name(course, my_class)
    if os.path.exists(fname) and os.path.getsize(fname) != 0:
        return fname
    else:
        if not os.path.exists(os.path.dirname(fname)):
            os.makedirs(os.path.dirname(fname))
        root = ET.Element('root')
    course_et = ET.SubElement(root, 'course')
    course_et.set('code', course.code)
    class_et = ET.SubElement(course_et, 'class')
    class_et.set('name', my_class.name)
    write_xml(fname, root)
    #f = open(fname, 'w')
    #f.write(ET.tostring(root))
    #f.close()
    return fname

def add_video(video, fname):
    if find_video(video, fname):
        return 0
    tree = ET.parse(fname)
    root = tree.getroot()
    exists = False
    lecture_et = goto_lecture(root,video)
    if(lecture_et != 0):
        exists = True
        video_et = ET.SubElement(lecture_et, 'video')
        video_et.set( 'name', video.name)
        video_et.set( 'path', video.file.name)
        size = ET.SubElement(video_et, 'size')
        size.text = str(video.file.size)
    if exists:
        write_xml(fname, root)
        return 1
    else:
        return -1

def add_audio(audio, fname):
    if find_audio(audio, fname):
        return 0
    tree = ET.parse(fname)
    root = tree.getroot()
    exists = False
    lecture_et = goto_lecture(root,audio)
    if(lecture_et != 0):
        exists = True
        audio_et = ET.SubElement(lecture_et, 'audio')
        audio_et.set( 'name', audio.audio_name)
        audio_et.set( 'path', audio.audio_file.name)
        size = ET.SubElement(audio_et, 'size')
        size.text = str(audio.audio_file.size)
    if exists:
        write_xml(fname, root)
        return 1
    else:
        return -1

def remove_audio(audio, fname):
    if not os.path.exists(fname) or os.path.getsize(fname) == 0:
        return -1
    tree = ET.parse(fname)
    root = tree.getroot()
    exists = False
    lecture_et = goto_lecture(root,audio)
    if(lecture_et != 0):
        for audio_et in lecture_et.findall('audio'):
            if audio_et.get('name') == audio.audio_name and audio_et.get('path') == audio.audio_file.name:
                lecture_et.remove(audio_et)
                exists = True
    if exists:
        write_xml(fname, root)
        return 1
    else:
        return -1

def remove_video(video, fname):
    if not os.path.exists(fname) or os.path.getsize(fname) == 0:
        return -1
    tree = ET.parse(fname)
    root = tree.getroot()
    exists = False
    lecture_et = goto_lecture(root,video)
    if(lecture_et != 0):
        for video_et in lecture_et.findall('video'):
            if video_et.get('name') == video.name and video_et.get('path') == video.file.name:
                lecture_et.remove(video_et)
                exists = True
    if exists:
        write_xml(fname, root)
        return 1
    else:
        return -1

def find_audio(audio, fname):
    if not os.path.exists(fname) or os.path.getsize(fname) == 0:
        return -1
    tree = ET.parse(fname)
    root = tree.getroot()
    exists = False
    lecture_et = goto_lecture(root,audio)
    if(lecture_et != 0):
        for audio_et in lecture_et.findall('audio'):
            if audio_et.get('name') == audio.audio_name and audio_et.get('path') == audio.audio_file.name:
                exists = True
                break
    return exists

def find_video(video, fname):
    if not os.path.exists(fname) or os.path.getsize(fname) == 0:
        return -1
    tree = ET.parse(fname)
    root = tree.getroot()
    exists = False
    lecture_et = goto_lecture(root,video)
    if(lecture_et != 0):
        for video_et in lecture_et.findall('video'):
            if video_et.get('name') == video.name and video_et.get('path') == video.file.name:
                exists = True
                break
    return exists

def create_xml_teacher_file(user): 
    f_name = MEDIA_ROOT +'teachers/'+ user.username
    fname =  f_name + '.xml'
    if os.path.exists(fname) and os.path.getsize(fname) != 0:
        return fname
    else:
        if not os.path.exists(os.path.dirname(fname)):
            os.makedirs(os.path.dirname(fname))
    root = ET.Element('root')
    teacher_et = ET.SubElement(root, 'teacher')
    teacher_et.set('username', user.username)
    write_xml(fname, root)

def add_course_class(course, my_class, user):
    f_name = MEDIA_ROOT +'teachers/'+ user.username
    fname =  f_name + '.xml'
    tree = ET.parse(fname)
    root = tree.getroot()
    existing_course = False
    teacher_et = root.findall('teacher')[0]
    if teacher_et.get('username') == user.username:
        for course_et in teacher_et.findall('course'):
            code = course_et.get('code')
            if code == course.code:
                existing_course = True
                _add_class(course_et, my_class)
        if not existing_course:
              course_et =  ET.SubElement(teacher_et, 'course')
              course_et.set('code', str(course.code))
              course_et.set('name', str(course.name))
              _add_class(course_et, my_class)
        write_xml(fname, root)

def add_lecture(lecture, fname):
    my_class = lecture.my_class
    course = my_class.course
    tree = ET.parse(fname)
    root = tree.getroot()
    lecture_exists = False
    for course_et in root.findall('course'):
        if course_et.get('code') == course.code:
            for class_et in course_et.findall('class'):
                if my_class.name == class_et.get('name'):
                    for lecture_et in class_et.findall('lecture'):
                        if(lecture_et.get('date') == lecture.date_name):
                            lecture_exists = True
                            break
                    if not lecture_exists:
                        existing_class_course = True
                        lecture_et = ET.SubElement(class_et, 'lecture')
                        lecture_et.set('date', str(lecture.date.strftime('%d-%m-%Y')))
    if not lecture_exists:
        write_xml(fname, root)
        return 1
    return 0



def _add_class( course_node, my_class):
    class_et =  ET.SubElement(course_node, 'class')
    class_et.set('name', my_class.name)
    class_et.set('year', str(my_class.year))
    class_et.set('semester', str(my_class.semester))
     

def compare_files( f_remote, f_local, course, my_class):
    if not os.path.isfile(f_remote):
        return -1, -1
    if not os.path.isfile(f_local):
        return -2, -2
    missing_video_files = list()
    missing_audio_files = list()
    remote_video_list = list()
    local_video_list = list()
    remote_video_list, remote_audio_list = _return_video_audio_list(f_remote, course, my_class)
    local_video_list, local_audio_list = _return_video_audio_list(f_local, course, my_class)
    video_found = False
    audio_found = False
    for video in local_video_list:
        video_found = False
        for video_remote in remote_video_list:
            if video.file.name == video_remote.file.name:
                video_found = True
                break
        if not video_found and video not in missing_video_files:
            #file needs to be uploaded
            print ('missing video', video.file.name)
            missing_video_files.append(video)
    for audio in local_audio_list:
        audio_found = False
        for audio_remote in remote_audio_list:
            if audio.audio_file.name == audio_remote.audio_file.name:
                audio_found = True
                break
        if not audio_found and audio not in missing_audio_files:
            #file needs to be uploaded
            print ('missing audio', audio.audio_file.name)
            missing_audio_files.append(audio)
    return missing_video_files, missing_audio_files 

def _return_video_audio_list( fname, course, my_class):
    tree = ET.parse(fname)
    root = tree.getroot()
    correct_class = False
    correct_course = False
    video_list = list()
    audio_list = list()
    course_et = _find_course(root, course)
    if(course_et  != 0):
        class_et = _find_class(course_et, my_class) 
        if(class_et  != 0):
            for lecture_et in class_et.findall('lecture'):
                    date = lecture_et.get('date')
                    lecture = Lecture(date_name = date, my_class = my_class)
                    for video_et in lecture_et.findall('video'):
                        path = video_et.get('path')
                        video = Video({'total_path' : path}, lecture = lecture) 
                        video_list.append(video)
                    for audio_et in lecture_et.findall('audio'):
                        path = audio_et.get('path')
                        audio = Audio({'total_path' : path}, lecture = lecture) 
                        audio_list.append(audio)

        return video_list, audio_list
    return -1

def get_ccl(component):
    try:
        lecture = component.lecture
        my_class = lecture.my_class
        course = my_class.course
        return course, my_class, lecture
    except:
        try:
            my_class = component.my_class
            course = my_class.course
            return my_class, course
        except:
            try:
                course = component.course
                return course
            except:
                return 0

def write_xml(fname, root_et):
    f = open(fname, 'w')
    ET.tostring(root_et)
    f.write(ET.tostring(root_et))
    f.close()

def goto_lecture(root_et, video_audio):
    course, my_class, lecture = get_ccl(video_audio)
    course_et = _find_course(root_et, course)
    if(course_et != 0):
        class_et = _find_class(course_et, my_class) 
        if(class_et != 0):
            lecture_et = _find_lecture(class_et, lecture)
            if(lecture_et != 0):
                return lecture_et
    else:
        return 0

def _find_course(root_et, course):
    for course_et in root_et.findall('course'):
        if course_et.get('code') == course.code:
            return course_et
    return 0


def _find_class(course_et, my_class):
    for class_et in course_et.findall('class'):
        if my_class.name == class_et.get('name'):
            return class_et
    return 0

def _find_lecture(class_et, lecture):
    for lecture_et in class_et.findall('lecture'):
        if lecture.date_name == lecture_et.get('date'):
            return lecture_et
    return 0
     

def prettify_all(fname):
    tree = ET.parse(fname)
    root = tree.getroot()
    prettified = _prettify(root)
    return prettified

def _prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def add_video_to_xml(video):
    lecture = video.lecture
    my_class = lecture.my_class
    course = my_class.course
    fname = create_xml_video_file(course, my_class)
    add_lecture(lecture, fname)
    add_video(video, fname)

def add_audio_to_xml(audio):
    lecture = audio.lecture
    my_class = lecture.my_class
    course = my_class.course
    fname = create_xml_video_file(course, my_class)
    add_lecture(lecture, fname)
    add_audio(audio, fname)

def remove_video_from_xml(video):
    my_class = video.lecture.my_class
    course = my_class.course
    fname = get_videos_xml_name(course, my_class)
    remove_video(video, fname)

def remove_audio_from_xml(audio):
    my_class = audio.lecture.my_class
    course = my_class.course
    fname = get_videos_xml_name(course, my_class)
    remove_audio(audio, fname)



#####################################################################
#                             #OLD#                                 #
#####################################################################
"""
def add_video_old(video, fname):
    if find_video(video, fname):
        return 0
    lecture = video.lecture
    my_class = lecture.my_class
    course = my_class.course
    tree = ET.parse(fname)
    root = tree.getroot()
    exists = False
    for course_et in root.findall('course'):
        if course_et.get('code') == course.code:
            for class_et in course_et.findall('class'):
                if my_class.name == class_et.get('name'):
                    for lecture_et in class_et.findall('lecture'):
                        if lecture.date_name == lecture_et.get('date'):
                            exists = True
                            video_et = ET.SubElement(lecture_et, 'video')
                            video_et.set( 'name', video.name)
                            video_et.set( 'path', video.file.name)
                            size = ET.SubElement(video_et, 'size')
                            size.text = str(video.file.size)
    if exists:
        f = open(fname, 'w')
        ET.tostring(root)
        #prettify(video_et)
        #f.write(ET.tostring(root))
        f.write(ET.tostring(root))#ET.tostring(root))
        f.close()
        return 1
    else:
        return -1



def add_audio_old(audio, fname):
    if find_audio(audio, fname):
        return 0
    lecture = audio.lecture
    my_class = lecture.my_class
    course = my_class.course
    tree = ET.parse(fname)
    root = tree.getroot()
    exists = False
    for course_et in root.findall('course'):
        if course_et.get('code') == course.code:
            for class_et in course_et.findall('class'):
                if my_class.name == class_et.get('name'):
                    for lecture_et in class_et.findall('lecture'):
                        if lecture.date_name == lecture_et.get('date'):
                            exists = True
                            audio_et = ET.SubElement(lecture_et, 'audio')
                            audio_et.set( 'name', audio.audio_name)
                            audio_et.set( 'path', audio.audio_file.name)
                            size = ET.SubElement(audio_et, 'size')
                            size.text = str(audio.audio_file.size)
    if exists:
        f = open(fname, 'w')
        ET.tostring(root)
        #prettify(video_et)
        #f.write(ET.tostring(root))
        f.write(ET.tostring(root))#ET.tostring(root))
        f.close()
        return 1
    else:
        return -1

        
def remove_audio_old(audio, fname):
    lecture = audio.lecture
    my_class = lecture.my_class
    course = my_class.course
    if not os.path.exists(fname) or os.path.getsize(fname) == 0:
        return -1

    tree = ET.parse(fname)
    root = tree.getroot()
    exists = False
    for course_et in root.findall('course'):
        if course_et.get('code') == course.code:
            for class_et in course_et.findall('class'):
                if my_class.name == class_et.get('name'):
                    for lecture_et in class_et.findall('lecture'):
                        if lecture.date_name == lecture_et.get('date'):
                            for audio_et in lecture_et.findall('audio'):
                                if audio_et.get('name') == audio.audio_name and audio_et.get('path') == audio.audio_file.name:
                                    lecture_et.remove(audio_et)
                                    exists = True
    if exists:
        f = open(fname, 'w')
        ET.tostring(root)
        #prettify(video_et)
        #f.write(ET.tostring(root))
        f.write(ET.tostring(root))#ET.tostring(root))
        f.close()



def remove_video_old(video, fname):
    lecture = video.lecture
    my_class = lecture.my_class
    course = my_class.course
    if not os.path.exists(fname) or os.path.getsize(fname) == 0:
        return -1
        
    tree = ET.parse(fname)
    root = tree.getroot()
    exists = False
    for course_et in root.findall('course'):
        if course_et.get('code') == course.code:
            for class_et in course_et.findall('class'):
                if my_class.name == class_et.get('name'):
                    for lecture_et in class_et.findall('lecture'):
                        if lecture.date_name == lecture_et.get('date'):
                            for video_et in lecture_et.findall('video'):
                                if video_et.get('name') == video.name and video_et.get('path') == video.file.name:
                                    lecture_et.remove(video_et)
                                    exists = True
    if exists:
        f = open(fname, 'w')
        ET.tostring(root)
        #prettify(video_et)
        #f.write(ET.tostring(root))
        f.write(ET.tostring(root))#ET.tostring(root))
        f.close()


def find_audio_old(audio, fname):
    lecture = audio.lecture
    my_class = lecture.my_class
    course = my_class.course
    if not os.path.exists(fname) or os.path.getsize(fname) == 0:
        return -1

    tree = ET.parse(fname)
    root = tree.getroot()
    exists = False
    for course_et in root.findall('course'):
        if course_et.get('code') == course.code:
            for class_et in course_et.findall('class'):
                if my_class.name == class_et.get('name'):
                    for lecture_et in class_et.findall('lecture'):
                        if lecture.date_name == lecture_et.get('date'):
                            for audio_et in lecture_et.findall('audio'):
                                if audio_et.get('name') == audio.audio_name and audio_et.get('path') == audio.audio_file.name:
                                   exists = True
                                   break
    return exists

def find_video_old(video, fname):
    lecture = video.lecture
    my_class = lecture.my_class
    course = my_class.course
    if not os.path.exists(fname) or os.path.getsize(fname) == 0:
        return -1
        
    tree = ET.parse(fname)
    root = tree.getroot()
    exists = False
    for course_et in root.findall('course'):
        if course_et.get('code') == course.code:
            for class_et in course_et.findall('class'):
                if my_class.name == class_et.get('name'):
                    for lecture_et in class_et.findall('lecture'):
                        if lecture.date_name == lecture_et.get('date'):
                            for video_et in lecture_et.findall('video'):
                                if video_et.get('name') == video.name and video_et.get('path') == video.file.name:
                                    exists = True
                                    break
    return exists

def _return_video_audio_list_old( fname, course, my_class):
    tree = ET.parse(fname)
    root = tree.getroot()
    correct_class = False
    correct_course = False
    video_list = list()
    audio_list = list()
    for course_et in root.findall('course'):
        code = course_et.get('code')
        if code == course.code:
            correct_course = True
            for class_et in course_et.findall('class'):
                if my_class.name == class_et.get('name'):
                    correct_class = True
                    for lecture_et in class_et.findall('lecture'):
                        date = lecture_et.get('date')
                        lecture = Lecture(date_name = date, my_class = my_class)
                        for video_et in lecture_et.findall('video'):
                            path = video_et.get('path')
                            video = Video({'total_path' : path}, lecture = lecture) 
                            video_list.append(video)
                        for audio_et in lecture_et.findall('audio'):
                            path = audio_et.get('path')
                            audio = Audio({'total_path' : path}, lecture = lecture) 
                            audio_list.append(audio)
    if not correct_course:
        return -1
    if not correct_class:
        return -2
    return video_list, audio_list
"""
