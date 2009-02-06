import os, time
from datetime import date
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _
from django.views.generic.simple import direct_to_template
from django.contrib.admin.views.decorators import staff_member_required

try:
    import S3
except ImportError:
    S3 = None


# default dump commands, you can overwrite these in your settings.
MYSQLDUMP_CMD = getattr(settings, 'MYSQLDUMP_CMD', '/usr/bin/mysqldump -h %s --opt --compact --skip-add-locks -u %s -p%s %s | bzip2 -c')
SQLITE3DUMP_CMD = getattr(settings, 'SQLITE3DUMP_CMD', 'echo ".dump" | /usr/bin/sqlite3 %s | bzip2 -c')
DISABLE_STREAMING = getattr(settings, 'DISABLE_STREAMING', False)


@staff_member_required
def export_database(request):
    """
    Dump the database directly to the browser

    """
    if request.method == 'POST':
        if settings.DATABASE_ENGINE == 'mysql':
            cmd = MYSQLDUMP_CMD % (settings.DATABASE_HOST, settings.DATABASE_USER, settings.DATABASE_PASSWORD, settings.DATABASE_NAME)
        elif settings.DATABASE_ENGINE == 'sqlite3':
            cmd = SQLITE3DUMP_CMD % settings.DATABASE_NAME
        else:
            raise ImproperlyConfigured, "Sorry, django-export only supports mysql and sqlite3 database backends."
        stdin, stdout = os.popen2(cmd)
        stdin.close()
        if DISABLE_STREAMING:
            stdout = stdout.read()
        response = HttpResponse(stdout, mimetype="application/octet-stream")
        response['Content-Disposition'] = 'attachment; filename=%s' % date.today().__str__()+'_db.sql.bz2'
        return response
    return direct_to_template(request, 'export/export.html', {'what': _(u'Export Database')})




@staff_member_required
def export_media(request):
    """
    Tar the MEDIA_ROOT and send it directly to the browser

    """
    if request.method == 'POST':
        stdin, stdout = os.popen2('tar -cf - %s' % settings.MEDIA_ROOT)
        stdin.close()
        if DISABLE_STREAMING:
            stdout = stdout.read()
        response = HttpResponse(stdout, mimetype="application/octet-stream")
        response['Content-Disposition'] = 'attachment; filename=%s' % date.today().__str__()+'_media.tar'
        return response
    return direct_to_template(request, 'export/export.html', {'what': _(u'Export Media Root')})




@staff_member_required
def export_to_s3(request):
    """
    Dump the database and upload the dump to Amazon S3

    """
    if request.method == 'POST':
        if settings.DATABASE_ENGINE == 'mysql':
            cmd = MYSQLDUMP_CMD % (settings.DATABASE_HOST, settings.DATABASE_USER, settings.DATABASE_PASSWORD, settings.DATABASE_NAME)
        elif settings.DATABASE_ENGINE == 'sqlite3':
            cmd = SQLITE3DUMP_CMD % settings.DATABASE_NAME
        else:
            raise ImproperlyConfigured, "Sorry, django-export only supports mysql and sqlite3 database backends."
        stdin, stdout = os.popen2(cmd)
        stdin.close()
        file_name = 'dump_%s.sql.bz2' % time.strftime('%Y%m%d-%H%M')
        conn = S3.AWSAuthConnection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        res = conn.put(settings.AWS_BUCKET_NAME, file_name, S3.S3Object(stdout.read()), {'Content-Type': 'application/x-bzip2',})
        if res.http_response.status == 200:
            request.user.message_set.create(message="%s" % _(u"%(filename)s saved on Amazon S3") % {'filename': file_name})
        else:
            request.user.message_set.create(message="%s" % _(u"Upload failed with %(status)s") % {'status': res.http_response.status})
        stdout.close()
        return HttpResponseRedirect('/admin/')
    return direct_to_template(request, 'export/export.html', {'what': _(u'Export Database to S3'), 's3support': (S3 is not None), 's3': True})




@staff_member_required
def list_s3(request):
    """
    List Amazon S3 bucket contents

    """
    if S3 is not None:
        conn = S3.AWSAuthConnection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        generator = S3.QueryStringAuthGenerator(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, calling_format=S3.CallingFormat.VANITY)
        generator.set_expires_in(300)
        bucket_entries = conn.list_bucket(settings.AWS_BUCKET_NAME).entries
        entries = []
        for entry in bucket_entries:
            entry.s3url = generator.get(settings.AWS_BUCKET_NAME, entry.key)
            entries.append(entry)
        return direct_to_template(request, 'export/list_s3.html', {'object_list': entries, 's3support': True})
    else:
        return direct_to_template(request, 'export/list_s3.html', {'object_list': [], 's3support': False})



