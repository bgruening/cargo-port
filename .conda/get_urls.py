#!/usr/bin/env python
"""
Creates a yaml file with all URL that needs to be downloaded, given a file with a list of all meta.yaml file.

Usage:

./get_urls.py meta_files.list
"""

import os
import sys
import yaml

from conda.base.context import context
from conda_build.metadata import MetaData

platform = context.subdir

sys.stderr.write('CWD: %s\nCONDA_SUBDIR: %s\n' % (os.getcwd(), platform))
url_file = open(sys.argv[1], 'r')


res = list()
for meta_path in url_file:
    input_dir = os.path.join( './bioconda-recipes', os.path.dirname(meta_path) )
    if os.path.exists(input_dir):
        try:
            package = dict()
            package['arch'] = platform

            recipe_meta = MetaData(input_dir)
            package['name'] = recipe_meta.get_value('package/name')
            package['version'] = recipe_meta.get_value('package/version')
            url = recipe_meta.get_value('source/url')
            if url:
                package['sha256'] = recipe_meta.get_value('source/sha256')
                package['md5'] = recipe_meta.get_value('source/md5')
            else:
                # git_url and hopefully git_rev
                git_url = recipe_meta.get_value('source/git_url')
                git_rev = recipe_meta.get_value('source/git_rev')
                url = '%s/%s.tar.gz' % (git_url.rstrip('.git'), git_rev)
                if not git_rev:
                    sys.stderr.write('git revision is missing for: %s\n' % input_dir)
                    continue
            package['url'] = url
            res.append(package)
        except Exception as e:
            sys.stderr.write('%s\n' % e)
            continue


with open('data_%s.yml' % (platform), 'w') as outfile:
    yaml.safe_dump(res, outfile, default_flow_style=False)
