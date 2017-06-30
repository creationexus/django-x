'''
Created on 11-01-2015

@author: carriagadad
'''
import unicodedata,re
def slugify(st):
    slug = unicodedata.normalize("NFKD",unicode(st)).encode("ascii", "ignore")
    slug = re.sub(r"[^\w]+", " ", slug)
    slug = "-".join(slug.lower().strip().split())
    return slug
def slugify_sp(st):
    slug = unicodedata.normalize("NFKD",unicode(st)).encode("ascii", "ignore")
    slug = re.sub(r"[^\w]+", " ", slug)
    slug = " ".join(slug.lower().strip().split())
    return slug