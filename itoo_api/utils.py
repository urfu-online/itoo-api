# -*- coding: utf-8 -*-

import time
import uuid
import os

def generate_new_filename(instance, filename):
    f, ext = os.path.splitext(filename)
    filename = '%s%s%s' % (uuid.uuid4().hex, ext, instance.first_name)
    fullpath = "verified_profile/{subdir}/{filename}".format(
        subdir=time.strftime('%Y-%m'),
        filename=filename
    )
    return fullpath
