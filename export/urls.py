from django.conf.urls.defaults import *


urlpatterns = patterns('export.views',
	url(r'^database/$', 'export_database', {}, name="export_database"),
	url(r'^database_s3/$', 'export_to_s3', {}, name="export_database_s3"),
	url(r'^media/$', 'export_media', {}, name="export_mediaroot"),
	url(r'^list_s3/$', 'list_s3', {}, name="export_list_s3"),
)