# coding: utf-8
###############################################################
# Requires MediaInfo Cli (prefer) OR ffmpeg & ffprobe (linux) #
###############################################################
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
        assert (vers[0] == 'MediaInfo') or (vers[0] == 'avprobe') or (vers[0] == 'ffprobe')
        return cmd
    except:
        return None

DECODER = get_usable_decoder('mediainfo') or get_usable_decoder('avprobe') or get_usable_decoder('ffprobe')

def _get_media_info(absname):
    '''Only supports media duration by now, in seconds'''
    if not DECODER:
        return {'duration': -1} # not supported
    if DECODER == 'mediainfo':
        cmnd = [DECODER, r'--Output=General;%Duration%', absname]
    else:
        cmnd = [DECODER, '-show_format', '-loglevel', 'quiet', absname]
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

def _sort_dirs(dirs, ignoreDirs=[]):
    '''将目录按名称归类，分隔符-'''
    for d in ignoreDirs:
        if d in dirs:
            dirs.remove(d)
    res = {}
    for dirname in dirs:
        findex = dirname.find('-')
        if findex < 1:
            res[dirname] = ''
        else:
            y, m = dirname[0:findex], dirname[findex+1:]
            if y in res:
                res[y].append(m)
            else:
                res[y] = [m]
    return res

def walk(path, fileOnly=False, ignoreDirs=[]):
    '''返回指定路径下的目录列表和文件信息。
    参数path：路径名
    参数fileOnly：可选， True则目录列表为空, 默认False
    参数ignoreDirs：可选，需过滤的目录列表，默认[]
    '''
    res = {}
    res['root'] = path
    res['files'] = []
    path = os.path.normpath(path)
    #三个参数：1.父目录 2.所有文件夹名字（不含路径） 3.所有文件名字
    for root,dirs,files in os.walk(path):
        #输出文件夹信息
        res['dirs'] = _sort_dirs(dirs, ignoreDirs) if not fileOnly else {}
        depth = root[len(path) + len(os.path.sep):].count(os.path.sep)
        if depth == 0: #不遍历子目录
            #res += [os.path.join(root, d) for d in dirs]
            dirs[:] = []
        #输出文件信息
        for filename in files:
            absname = os.path.join(root,filename)
            info = media_info(absname)
            info['name'] = filename
            res['files'].append(info)
    #done
    return res

if __name__ == "__main__":
    res = walk(".")
    print res
