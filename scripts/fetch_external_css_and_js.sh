#!/bin/bash

# cd ..
# URLs for e.g. blueprints are relative assuming you are in the scout folder (repo root)

# CSS
mkdir scout/server/blueprints/public/static/external
# create a url list for later reference
for url in `git grep \\.css |grep "src\|href" |grep -v "url_for" |perl -ne 'm/href=\"([^"]+)/; print $1,"\n";'|sort|uniq`; do echo $url >> tmp.css_urls; done
# retrieve external css files with http(s)
for url in `git grep \\.css |grep "src\|href" |grep -v "url_for" |perl -ne 'm/href=\"([^"]+)/; print $1,"\n";'|sort|uniq`; do wget -P scout/server/blueprints/public/static/ $url; done
# list files that need url changes
for file in scout/server/blueprints/public/static/external/*css ; do git grep `basename $file`; done |grep -v demo |cut -f 1 -d\: |sort|uniq> tmp.css_files
# construct a substitution perl script to change the urls to point to url_for('public.static', filename)
for file in scout/server/blueprints/public/static/external/*css ; do git grep `basename $file`; done |grep -v demo |perl -ne 'm/href=\"([^"]+)/; $url=$1;$old_url=$url; $url=~s/https\:\/\/.+?([^\/]+)$/\{\{ url_for\("public.static", filename="external\/$1"\) \}\}/; $old_url=~s/\@/\\\@/; print "s+",$old_url,"+",$url,"+;\n";' | sort |uniq| sed -e 's/"/'\''/g' > tmp.css_patterns
echo "print; ">> tmp.css_patterns
# and actually apply the script
for file in `cat tmp.css_files`; do perl -n tmp.css_patterns < $file > ${file}.external; mv ${file}.external $file; done

# JS

# create a url list for later reference
for url in `git grep \\.js |grep "src" |grep -v "url_for\|demo" |perl -ne 'm/src=\"([^"]+)/; print $1,"\n";'|sort|uniq`;do echo $url >> tmp.js_urls; done
# retrieve external js files with http(s)
for url in `git grep \\.js |grep "src\|href" |grep -v "demo\|url_for" |perl -ne 'm/src=\"([^"]+)/; print $1,"\n";'|sort|uniq` ; do wget -P scout/server/blueprints/public/static/ $url; done
# list files that need url changes
for file in scout/server/blueprints/public/static/external/*js ; do git grep `basename $file`; done |grep -v demo |cut -f 1 -d\: |sort|uniq > tmp.js_files
# construct a substitution perl script to change the urls to point to url_for('public.static', filename)
for file in scout/server/blueprints/public/static/external/*js ; do git grep `basename $file`; done |grep -v demo |perl -ne 'm/src=\"([^"]+)/; $url=$1;$old_url=$url; $url=~s/https\:\/\/.+?([^\/]+)$/\{\{ url_for\("public.static", filename="external\/$1"\) \}\}/; $old_url=~s/\@/\\\@/; print "s+",$old_url,"+",$url,"+;\n";' |sort|uniq| sed -e 's/"/'\''/g'> tmp.js_patterns
echo "print; ">> tmp.js_patterns
# and actually apply the script
for file in `cat tmp.js_files`; do perl -n tmp.js_patterns < $file > ${file}.external; mv ${file}.external $file; done
