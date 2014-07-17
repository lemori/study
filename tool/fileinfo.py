# coding: utf-8
##################################################################
# Requires MediaInfo Cli (preferred) OR ffmpeg & ffprobe (linux) #
##################################################################
import os
import stat
import subprocess

ROOT = ''
MEDIA_FILE_TYPES = ['amr', 'mp3', 'mp4', 'ogg', 'ogv']

def _decoder(cmd):
    try:
        v = '--Version' if cmd == 'mediainfo' else '-version'
        p = subprocess.Popen([cmd, v], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        vers = out.split('\n')[0].split(' ')
        assert (vers[0] == 'MediaInfo') or (vers[0] == 'avprobe') or (vers[0] == 'ffprobe')
        return cmd
    except:
        return None

DECODER = _decoder('mediainfo') or _decoder('avprobe') or _decoder('ffprobe')

def mediainfo(files):
    '''对给定的文件列表，读取每个文件的播放时长（如果有）
       如果当前解码器是mediainfo，支持多个文件，返回值为整型字符串数组
       如果当前解码器是ffmpeg，仅支持单个文件，返回值为浮点型字符串
    '''
    if DECODER == 'mediainfo':
        cmnd = [DECODER, r'--Inform=General;%Duration%-'] + files
        p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elif len(files) == 1:
        cmnd = '%s -show_format -loglevel quiet "%s" |grep duration' % (DECODER, files[0])
        p = subprocess.Popen(cmnd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        return None
    out, err =  p.communicate()
    if err or not out:
        print 'err:', err
        return None
    if DECODER == 'mediainfo':
        return out.split('-') # int value list
    else:
        return out.split('=')[1].strip() # float value

def isvalid_weixin_media(ftype, size, duration=-1):
    '''0:bad, 1:good, 2:not good for thumb'''
    duration = int(duration)
    if ftype == 'jpg':
        if size > 1024 * 1024:
            return 0
        if size > 64 * 1024:
            return 2 # good for image, not for thumb
        return 1
    if ftype == 'amr' or ftype == 'mp3':
        if (size <= 1024 * 1024 * 2) and (0 <= duration <= 60):
            return 1
        return 0
    if ftype == 'mp4':
        if size > 1024 * 1024 * 10:
            return 0
        return 1
    # by default, not supported
    return 0

def fileinfo(absname):
    '''sample:
    {'mtime': 1400735085, 'type': 'jpg', 'size': 53, duration: -1}
    '''
    ftype = os.path.splitext(absname)[1].lower()
    state = os.stat(absname)
    info = {}
    info['type'] = ftype[1:]
    info['size'] = state[stat.ST_SIZE]
    info['mtime'] = state[stat.ST_MTIME]
    info['duration'] = -1
    return info

def _sort_dirs(dirs, ignoreDirs=[]):
    '''将目录按名称归类，分隔符-
    注意：如果有两个目录A，A-B，则A将不可见（被同名覆盖）。
    '''
    for d in ignoreDirs:
        if d in dirs:
            dirs.remove(d)
    res = {}
    for dirname in dirs:
        findex = dirname.find('-')
        if findex < 1:
            res[dirname] = [] #可能重名
        else:
            y, m = dirname[0:findex], dirname[findex+1:]
            if y in res:
                res[y].append(m)
            else:
                res[y] = [m]
    return res

def _setinfos(res, mids, mfiles):
    c = 0
    if DECODER == 'mediainfo':
        ds = mediainfo(mfiles)
        if not ds:
            return
        for i in mids:
            f = res['files'][i]
            f['duration'] = int(ds[c]) / 1000.0 if ds[c] else -1
            f['weixin'] = isvalid_weixin_media(
                f['type'], f['size'], f['duration'])
            c += 1
    else:
        for i in mids:
            duration = mediainfo([mfiles[c]])
            if duration:
                f = res['files'][i]
                f['duration'] = float(duration)
                f['weixin'] = isvalid_weixin_media(
                    f['type'], f['size'], f['duration'])
            c += 1

def walk(path, fileOnly=False, ignoreDirs=[]):
    '''返回指定路径下的目录列表和文件信息。
    参数path：路径名
    参数fileOnly：可选， True则目录列表为空, 默认False
    参数ignoreDirs：可选，需过滤的目录列表，默认[]
    '''
    res = { 'root' : path, 'files' : [] }
    mids = []
    mfiles = []
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
        for filename in sorted(files):
            absname = os.path.join(root,filename)
            info = fileinfo(absname)
            info['name'] = filename
            if info['type'] in MEDIA_FILE_TYPES:
                info['weixin'] = 0
                mids.append( len(res['files']) )
                mfiles.append( absname )
            else:
                info['weixin'] = isvalid_weixin_media(
                    info['type'], info['size'], info['duration'])
            res['files'].append( info )
    # 添加媒体信息
    if mfiles and DECODER:
        _setinfos(res, mids, mfiles)
    #done
    return res

def walk_files(path, filters, limit=500):
    '''返回指定路径下的图片文件的（相对）路径列表。
    filters: 指定的文件扩展名列表
    limit: 数量限制，默认500个
    '''
    res = []
    count = 1
    path = os.path.normpath(path).replace('\\\\', '/')
    #三个参数：1.父目录 2.所有文件夹名字（不含路径） 3.所有文件名字
    for root,dirs,files in os.walk(path):
        if count > limit:
            break
        depth = root[len(path) + len(os.path.sep):].count(os.path.sep)
        if depth == 1: #不遍历子目录的子目录
            #res += [os.path.join(root, d) for d in dirs]
            dirs[:] = []
        #输出文件信息
        for filename in sorted(files):
            ext = os.path.splitext(filename)[1].lower()
            if ext and ext[1:] in filters:
                res.append(root[len(ROOT):] + "/" + filename)
                count += 1
                if count > limit:
                    break
    #done
    return res

if __name__ == '__main__':
    fpath = '/path/to/sample'
    print fpath
    val = walk(fpath)
    for v in val['files']:
        print v['name'], v['size'], v['duration'], v['weixin']
