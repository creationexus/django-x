'''
Created on 13-01-2015

@author: carriagadad
'''
from google.appengine.api import images
from google.appengine.api import files
from google.appengine.ext import blobstore
import cloudstorage as gcs
import mimetypes
import hashlib
import time
import logging
from google.appengine.api import app_identity
import os
import sys
import StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import urllib2, cStringIO
try:
    from PIL import Image, ImageDraw, ImageFont, ImageEnhance
except:
    import Image, ImageDraw, ImageFont, ImageEnhance
 
class ImpropertlyConfigured(Exception):
    pass
import copy
my_default_retry_params = gcs.RetryParams(initial_delay=0.2,max_delay=5.0,backoff_factor=2,max_retry_period=15)
gcs.set_default_retry_params(my_default_retry_params)

def get_size(image):
    img=images.Image(image)
    return "%s x %s"%(str(img.width()),str(img.height()))
def clean_photo(image):
    img=Image.open(image)
    w,h=img.size
    max_width=max_height=5000
    if w>max_width or h>max_height:
        del img,image
        return 0
    max_aspect=3
    if (w/h)>max_aspect or (h/w)>max_aspect:
        del img,image
        return 1
    main,sub=image.content_type.split('/')
    logging.debug(str(main)+" "+str(sub))
    if not (main.lower() in ['image','application'] and sub.lower() in ['png','jpg','jpeg','bmp','octet-stream']):
        del img,image
        return 2
    if len(image)>(8*1024*1024):
        del img,image
        return 3
    img.thumbnail((640,640),Image.ANTIALIAS)
    #del image
    return img
""""def init_image(fil):
    file_name_hash=hashlib.sha1(str(time.time())).hexdigest()
    filename='/oclock-static/%s.jpg'%file_name_hash
    image=copy.deepcopy(fil)
    fil=clean_photo(fil)
    if type(fil) is int:
        del image
        return fil
    fil=image
    del image
    return create_file(filename,fil)"""
def create_img(img):
    return Image.open(img)
def images_stamp(img,typ=0):
    ROOT_PATH=os.path.dirname(__file__)
    if typ==0:
        skin=Image.open(ROOT_PATH+"/clock_estampa.png")
        img=img.resize((640,640),Image.BILINEAR)
        img=watermark2(img,skin,'tile',1)
    else:
        skin=Image.open(ROOT_PATH+"/clock_estampa.png")
        img=img.resize((640,640),Image.BILINEAR)
        img=watermark2(img,skin,'tile',1)
    del skin
    return img

def init_image(fil,typ):
    file_name_hash=hashlib.sha1(str(time.time())).hexdigest()
    filename='/oclock-static/%s.jpg'%file_name_hash
    filename2='/oclock-static/%s-stamp.jpg'%file_name_hash
    img=clean_photo(fil)
    if type(img) is int:
        return img
    thumb_io=StringIO.StringIO()
    omg=InMemoryUploadedFile(thumb_io,None,'%s.jpg'%file_name_hash,'image/jpeg',thumb_io.len,None)
    try:
        img.save(omg,quality=60,optimize=True,progressive=True)
    except IOError:
        img.save(omg,quality=80)
    img2=images_stamp(img,typ)
    thumb_io=StringIO.StringIO()
    omg2=InMemoryUploadedFile(thumb_io,None,'%s.jpg'%file_name_hash,'image/jpeg',thumb_io.len,None)
    try:
        img2.save(omg2,quality=60,optimize=True,progressive=True)
    except IOError:
        img2.save(omg2,quality=80)
    del fil
    del img
    return [create_file2(filename,omg),create_file2(filename2,omg2)]
def thumbnail_image(img):
    img=Image.open(img)
    img.thumbnail((600,600),Image.ANTIALIAS)
    return img
def remote_to_img(URL,res):
    img=cStringIO.StringIO(urllib2.urlopen(URL).read())
    img=Image.open(img)
    return img.save(res,'PNG')
def remote_image(fil):
    file_name_hash=hashlib.sha1(str(time.time())).hexdigest()
    filename='/oclock-static/%s.jpg'%file_name_hash
    return create_file(filename,fil)
def remote_image2(fil):
    file_name_hash=hashlib.sha1(str(time.time())).hexdigest()
    filename='/oclock-static/%s.jpg'%file_name_hash
    return create_file2(filename,fil)
def stat_file(filename):
    stat=gcs.stat(filename)
    return repr(stat)
def create_file(filename,fil):
    write_retry_params=gcs.RetryParams(backoff_factor=1.1)
    content_type=mimetypes.guess_type(filename)[0]
    with gcs.open(filename,'w',content_type=content_type,options={b'x-goog-acl':b'public-read'}) as f:
        while True:
            chunk=fil.read(8192)
            if not chunk:
                break
            f.write(chunk)
    del fil
    return 'https://storage.googleapis.com%s'%(filename)
def create_file2(filename,fil):
    write_retry_params=gcs.RetryParams(backoff_factor=1.1)
    content_type=mimetypes.guess_type(filename)[0]
    with gcs.open(filename,'w',content_type=content_type,options={b'x-goog-acl':b'public-read'}) as f:
        for chunk in fil.chunks():
            f.write(chunk)
    del fil
    return 'https://storage.googleapis.com%s'%(filename)    
 
 
def ReduceOpacity(im, opacity):
    """
    Returns an image with reduced opacity.
    Taken from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/362879
    """
    assert opacity >= 0 and opacity <= 1
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    else:
        im = im.copy()
    alpha = im.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    im.putalpha(alpha)
    return im
 
def Imprint(im, inputtext, font=None, color=None, opacity=0.6, margin=(30,30)):
    """
    imprints a PIL image with the indicated text in lower-right corner
    """
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    textlayer = im#Image.new("RGBA", im.size, (0,0,0,80))
    #textdraw = ImageDraw.Draw(textlayer)
    textdraw = ImageDraw.Draw(im)
    textsize = textdraw.textsize(inputtext, font=font)
    textpos = [(im.size[i]/2)-(textsize[i]/2)-margin[i] for i in [0,1]]
    textdraw.text(textpos, inputtext, font=font, fill=color)
    if opacity != 1:
        textlayer = ReduceOpacity(textlayer,opacity)
    return Image.composite(textlayer, im, textlayer)
 
def watermark(image, text, font_path, font_scale=None, font_size=None, color=(0,0,0), opacity=0.6, margin=(0, 0)):
    """
    image - PIL Image instance
    text - text to add over image
    font_path - font that will be used
    font_scale - font size will be set as percent of image height
    """
    if font_scale and font_size:
        raise ImpropertlyConfigured("You should provide only font_scale or font_size option, but not both")
    elif font_scale:
        width, height = image.size
        font_size = int(font_scale*width)
    elif not (font_size or font_scale):
        raise ImpropertlyConfigured("You should provide font_scale or font_size option")
    font=ImageFont.truetype(font_path,font_size)
    im0 = Imprint(image, text, font=font, opacity=opacity, color=color, margin=margin)
    return im0 

def timestamp(file,days,time,response,type=0):
    ROOT_PATH=os.path.dirname(__file__)
    FONTS=[ROOT_PATH+"/Snowinter.ttf",ROOT_PATH+"/heartfont.TTF",ROOT_PATH+"/good-times.ttf",ROOT_PATH+"/loveness.ttf"]
    img=Image.open(file)
    #img.thumbnail(100,Image.ANTIALIAS)
    #logging.debug(ROOT_PATH)
    #dir=open(os.path.abspath('static/fonts')+'/Snowinter.ttf')
    #logging.debug(dir)
    #logging.debug(sys.path.append(os.path.join(os.path.dirname(__file__),'/../../../static/fonts')))
    img=img.resize((320,320),Image.ANTIALIAS)
    #img=resize_and_crop(img,(640,640),'top')
    if type==0:
        skin=Image.open(ROOT_PATH+"/valentine_stamp3.png")
        img=watermark2(img,skin,'tile',1)
        img=watermark(image=img,text=time,color=(55,62,20),opacity=1,font_path=FONTS[2],font_scale=0.1,margin=(0,-140))
    else:
        skin=Image.open(ROOT_PATH+"/valentine_stamp2.png")
        img=watermark2(img,skin,'tile',1)
        if days>0:
            img=watermark(image=img,text="%sD"%days,color=(255,255,255),opacity=1,font_path=FONTS[3],font_scale=0.1,margin=(0,-100))
        img=watermark(image=img,text=time,color=(255,255,255),opacity=1,font_path=FONTS[3],font_scale=0.1,margin=(0,-140))
    #img=watermark(image=img,text=time,color=(255,255,255),opacity=1, font_path=FONTS[1], font_scale=0.1, margin=(0,0))
    return img.save(response,'PNG')
def resize_and_crop(img,size,crop_type='top'):
    # If height is higher we resize vertically, if not we resize horizontally
    #img = Image.open(img_path)
    # Get current and desired ratio for the images
    img_ratio = img.size[0] / float(img.size[1])
    ratio = size[0] / float(size[1])
    #The image is scaled/cropped vertically or horizontally depending on the ratio
    if ratio > img_ratio:
        img = img.resize((size[0], size[0] * img.size[1] / img.size[0]),
                Image.ANTIALIAS)
        # Crop in the top, middle or bottom
        if crop_type == 'top':
            box = (0, 0, img.size[0], size[1])
        elif crop_type == 'middle':
            box = (0, (img.size[1] - size[1]) / 2, img.size[0], (img.size[1] + size[1]) / 2)
        elif crop_type == 'bottom':
            box = (0, img.size[1] - size[1], img.size[0], img.size[1])
        else :
            raise ValueError('ERROR: invalid value for crop_type')
        img = img.crop(box)
    elif ratio < img_ratio:
        img = img.resize((size[1] * img.size[0] / img.size[1], size[1]),
                Image.ANTIALIAS)
        # Crop in the top, middle or bottom
        if crop_type == 'top':
            box = (0, 0, size[0], img.size[1])
        elif crop_type == 'middle':
            box = ((img.size[0] - size[0]) / 2, 0, (img.size[0] + size[0]) / 2, img.size[1])
        elif crop_type == 'bottom':
            box = (img.size[0] - size[0], 0, img.size[0], img.size[1])
        else :
            raise ValueError('ERROR: invalid value for crop_type')
        img = img.crop(box)
    else :
        img = img.resize((size[0], size[1]),
                Image.ANTIALIAS)
        # If the scale is the same, we do not need to crop
    return img
def reduce_opacity(im, opacity):
    """returns an image with reduced opacity"""
    assert opacity >= 0 and opacity <= 1
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    else:
        im = im.copy()
    alpha = im.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    im.putalpha(alpha)
    return im
def watermark2(im, mark, position, opacity=1):
    """adds a watermark to an image"""
    if opacity < 1:
        mark = reduce_opacity(mark, opacity)
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    # create a transparent layer the size of the image and draw the
    # watermark in that layer.
    layer = Image.new('RGBA', im.size, (0,0,0,0))
    if position == 'tile':
        for y in range(0, im.size[1], mark.size[1]):
            for x in range(0, im.size[0], mark.size[0]):
                layer.paste(mark, (x, y))
    elif position == 'scale':
        # scale, but preserve the aspect ratio
        ratio = min(
            float(im.size[0]) / mark.size[0], float(im.size[1]) / mark.size[1])
        w = int(mark.size[0] * ratio)
        h = int(mark.size[1] * ratio)
        mark = mark.resize((w, h))
        layer.paste(mark, ((im.size[0] - w) / 2, (im.size[1] - h) / 2))
    else:
        layer.paste(mark, position)
    # composite the watermark with the layer
    return Image.composite(layer, im, layer)