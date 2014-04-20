#coding:utf-8
#####################################################
# Requires MediaInfo Cli (prefer) or ffmpeg (linux) #
#####################################################
import os
import stat
import time
import re
import subprocess

def get_usable_decoder(cmd):
    try:
        v = '--Version' if cmd == 'mediainfo' else '-version'
        p = subprocess.Popen([cmd, v], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        vers = out.split('\n')[0].split(' ')
        assert (vers[0] == 'MediaInfo') or (vers[0] == 'avconv') or (vers[0] == 'ffmpeg')
        return cmd
    except:
        return None

DECODER = get_usable_decoder('mediainfo') or get_usable_decoder('avconv') or get_usable_decoder('ffmpeg')

def _get_media_info(absname):
    if not DECODER:
        return {'duration': -1} # not supported
    if DECODER == 'mediainfo':
        cmnd = ['mediainfo', r'--Output=General;%Duration%', absname]
    else:
        cmnd = ['ffprobe', '-show_format', '-loglevel', 'quiet', absname]
    p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err =  p.communicate()
    if err or not out:
        return {'duration': -1} # bad media
    if DECODER == 'mediainfo':
        return {'duration': float(out) / 1000}
    else:
        p = re.compile(r'.*duration=(\S+)')
        m = p.search(out)
        return {'duration': float(m.groups()[0])}

def pretty_size(size):
    if size <= 1024:
        return {'size': size, 'unit': 'B'}
    elif 1024 * 1024 > size > 1024:
        return {'size': (size / 1024), 'unit': 'K'}
    else:
        return {'size': (size / (1024 * 1024)), 'unit': 'M'}

def isvalid_weixin_media(ftype, size, duration=-1):
    '''0:bad, 1:good, >1:not good for thumb'''
    if ftype == 'jpg':
        if size > 128 * 1024:
            return 0
        if size > 64 * 1024:
            return 3 # good for image, not for thumb
        else:
            return 1
    if ftype == 'amr' or ftype == 'mp3':
        if (size <= 256 * 1024) and (0 <= duration <= 60):
            return 1
        return 0
    if ftype == 'mp4':
        if size > 1024 * 1024:
            return 0
        return 1
    # by default, not supported
    return 0

def media_info(absname):
    '''sample:
    {'duration': 0, 'valid_weixin_media': 1, 'mtime': '2013-03-21 21:59:46', 'type': 'jpg', 'size': '61.3 K'}
    '''
    ftype = os.path.splitext(absname)[1]
    if not ftype:
        {'errcode': 1, 'errmsg': 'Invalid filename'}
    # common attributes
    ftype = ftype[1:]
    state = os.stat(absname)
    info = {}
    info['type'] = ftype
    info['size'] = state[stat.ST_SIZE]
    #info['ctime'] = time.strftime("%Y-%m-%d %X", time.localtime(state[stat.ST_CTIME]))
    info['mtime'] = time.strftime("%Y-%m-%d %X", time.localtime(state[stat.ST_MTIME]))
    # media info
    if ftype in ['amr', 'mp3', 'mp4']:
        info['duration'] = _get_media_info(absname)['duration']
    else:
        info['duration'] = 0
    # is valid weixin media
    info['valid_weixin_media'] = isvalid_weixin_media(
        info['type'], info['size'], info['duration'])
    psize = pretty_size(info['size'] * 1.0)
    info['size'] = '%.1f %s' % (psize['size'], psize['unit'])
    return info

def walk(path):
    #三个参数：分别返回1.父目录 2.所有文件夹名字（不含路径） 3.所有文件名字
    for parent,dirnames,filenames in os.walk(path):
        #输出文件夹信息
        for dirname in  dirnames:
            print "parent is:" + parent
            print  "dirname is:" + dirname

        #输出文件信息
        for filename in filenames:
            #print "parent is:" + parent
            print "文件名:" + filename
            #输出文件路径信息
            absname = os.path.join(parent,filename)
            print "完整路径:", os.path.abspath(absname)
            print "======= media info ========"
            print media_info(absname)
            print ""

if __name__ == "__main__":
    walk(".")
