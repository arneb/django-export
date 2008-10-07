======================================================
A Django app to export a database dump and media files
======================================================

This app provides a few views to export the database and the media-root. 
Default templates are provided for an easy integration with django.contrib.admin.

Currently mysql and sqlite3 database backends are supported.

Additionally the app provides some Amazon S3 integration. Exporting a
database dump directly to S3 and listing the bucket contents is implemented.


.. note ::

    I originally posted the views on djangosnippets a few month ago `here`_
    
.. _`here` : http://www.djangosnippets.org/snippets/580/

 
Installation
------------

Add the folder ``export`` to your Python-Path.

Then add ``export`` to your INSTALLED_APPS setting::

    INSTALLED_APPS = (
        ...
        'export',
    )
    
Then hook the app into your url-conf, for example diretly under the admin
url-space::

    urlpatterns += pattern('',
        url(r'^admin/export/', include('export.urls')),
    )


.. note ::

    Be sure to add this pattern before the django.contrib.admin pattern, 
    otherwise your urls will never be picked up, because they are catched by
    the ``r'^admin/(.*)'`` pattern.
    
    
Now add Links to the export views to your Admin Index Template, or anywhere 
else you like. The Links to the views are accessible via::

    Export Database: {% url export_database %}
    Export Database to S3: {% url export_database_s3 %}
    Export Media Root: {% url export_mediaroot %}
    List S3 Bucket: {% url export_list_s3 %}

    
Settings
--------

There are currently two **optional** settings:

  MYSQLDUMP_CMD : The command used to dump a mysql database.
                  Defaults to: '/usr/bin/mysqldump -h %s --opt --compact \
                  --skip-add-locks -u %s -p%s %s | bzip2 -c'
                  
  SQLITE3DUMP_CMD: The command used to dump a sqlite2 database.
                   Defaults to: 'echo ".dump" | /usr/bin/sqlite3 %s | bzip2 -c'
  
