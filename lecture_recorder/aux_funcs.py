

def get_course_class_path(course, my_class):
	path = course.code +'/'+ my_class.name + '/' + str(my_class.year) + '_' + my_class.semester + '/'
	return path