from ftplib import FTP
import os
import sys

titleIdLookup = {
    "US": '0100000000010000'
}

def listdirs(connection,_path):

    file_list, dirs, nondirs = [], [], []
    try:
        connection.cwd(_path)
    except:
        return []

    connection.retrlines('LIST', lambda x: file_list.append(x.split()))
    for info in file_list:
        ls_type, name = info[0], info[-1]
        if ls_type.startswith('d'):
            dirs.append(name)
        else:
            nondirs.append(name)
    return dirs

def folderUpload(path):
    for name in os.listdir(path):
        localpath = os.path.join(path, name)
        if os.path.isfile(localpath):
            print("STOR", name, localpath)
            ftp.storbinary('STOR ' + name, open(localpath,'rb'))
        elif os.path.isdir(localpath):
            print("MKD", name)

            try:
                ftp.mkd(name)

            # ignore "directory already exists"
            except error_perm as e:
                if not e.args[0].startswith('550'): 
                    raise

            print("CWD", name)
            ftp.cwd(name)
            folderUpload(localpath)
            print("CWD", "..")
            ftp.cwd("..")



def ensuredirectory(connection,root,path):
    print(f"Ensuring {os.path.join(root, path)} exists...")
    if path not in listdirs(connection, root):
        connection.mkd(f'{root}/{path}')


consoleIP = sys.argv[1]
if '.' not in consoleIP:
    print(sys.argv[0], "ERROR: Please specify with `IP=[Your console's IP]`")
    sys.exit(-1)

consolePort = 5000

projName = sys.argv[2]
try:
    username = sys.argv[3]
    password = sys.argv[4]
except:
    username = ""
    password = ""

curDir = os.curdir

ftp = FTP()

print(f'Connecting to {consoleIP}... ', end='')
ftp.connect(consoleIP, consolePort)
print('logging into server...', end='')
ftp.login(username, password)
print('Connected!')

patchDirectories = []

root, dirs, _ = next(os.walk(curDir))

for dir in dirs:
    if dir.startswith("starlight_patch_"):
        patchDirectories.append((os.path.join(root, f'{dir}/atmosphere/exefs_patches/{projName}'), projName))

ensuredirectory(ftp, '', 'atmosphere')
ensuredirectory(ftp, '/atmosphere', 'exefs_patches')

for patchDir in patchDirectories:
    dirPath = patchDir[0]
    dirName = patchDir[1]
    ensuredirectory(ftp, '/atmosphere/exefs_patches', patchDir[1])
    _, _, files = next(os.walk(dirPath))
    for file in files:
        fullPath = os.path.join(dirPath, file)
        if os.path.exists(fullPath):
            sdPath = f'/atmosphere/exefs_patches/{projName}/{file}'
            print(f'Sending "{sdPath}" to {consoleIP}.')
            ftp.storbinary(f'STOR {sdPath}', open(fullPath, 'rb'))

ensuredirectory(ftp, '/atmosphere', 'contents')
ensuredirectory(ftp, '/atmosphere/contents', '0100000000010000')
ensuredirectory(ftp, f'/atmosphere/contents/0100000000010000', 'exefs')

binaryPath = f'starlight_patch_100/atmosphere/contents/0100000000010000/exefs/subsdk1'

if os.path.isfile(binaryPath):
    sdPath = f'/atmosphere/contents/0100000000010000/exefs/subsdk1'
    print(f'Sending "{sdPath}" to {consoleIP}.')
    ftp.storbinary(f'STOR {sdPath}', open(binaryPath, 'rb'))

ensuredirectory(ftp, f'/atmosphere/contents/0100000000010000', 'romfs')

path = f'romfs/'
ftp.cwd(f'/atmosphere/contents/0100000000010000/romfs')
folderUpload(path)