#!/usr/bin/python3
import argparse, os

def copyfile_tool(source, dest):
    head, tail = os.path.split(source)
    # tail = source.split('/')[-1]
    print(head)
    if dest.endswith('/'):
        dest = dest + tail

    with open(source, 'rb') as src, open(dest, 'wb') as dst:
        copyfileobj_example(src, dst)
    return 1

def copyfileobj_example(source, dest, buffer_size=1024*1024):
    """
    Copy a file from source to dest. source and dest
    """
    while True:
        copy_buffer = source.read(buffer_size)
        if not copy_buffer:
            break
        dest.write(copy_buffer)
    return 1

def set_time():
    destination = './NEW100'
    source = './NEW1'
    os.utime(destination, (os.stat(source).st_atime, os.stat(source).st_mtime))
    # print('A ',os.stat(source).st_mtime,' ','B ', os.stat(destination).st_mtime)
    return 1

def set_permission():
    destination = './NEW99'
    source = './NEW1'
    os.chmod(destination, os.stat(source).st_mode)
    return 1

def is_symlink(source):
    return os.path.islink(source)


def set_symlink(source, destination):
    # destination = './NEW99'
    # source = './NEW1'
    os.symlink(os.readlink(source), destination)
    return 1


def is_hardlink(source):
    # source = './NEW1'
    return (os.stat(source).st_nlink > 1 )

def set_hard_link():
    destination = './NEW95'
    source = './NEW1'
    os.link(source, destination)

def process_inputs():
    parser = argparse.ArgumentParser()
    parser.add_argument('index', nargs = '+', help = 'some ids')
    parser.add_argument('-u', action='store_true', help='sum the integers (default: find the max)')
    parser.add_argument('-c', action='store_true', help='sum the integers (default: find the max)')

    mode = []
    input = parser.parse_args()
    # print(input.u, input.c)
    if input.u:
        mode.append('-u')
    if input.c:
        mode.append('-c')

    data = input.index[:]
    # print(len(data))
    t = len(data) - 1
    source = data[0:t]
    destination = data[-1]
    print('...Process_inputs...')
    # print(source, destination)
    return source, destination, mode


def check_source_file(source):
    source_type = 0
    source_attribute = ''
    if os.path.exists(source):
        if is_symlink(source):
            source_type = 1
        elif is_hardlink(source):
            source_type = 2
        else:
            source_type = 3
        if os.path.isfile(source):
            source_attribute = 'isfile'
        else:
            source_attribute = 'isdir'
        return source_type, source_attribute
    return False

def check_destitaion_file(destination):
    print('...Check_destitaion_file')
    destination_attribute = ''
    if os.path.exists(destination):
        if os.path.isfile(destination):
            destination_attribute = 'isfile'
        else:
            destination_attribute = 'isdir'
        return destination_attribute
    return False

def create_directory(destination):
    print('...CREATE directory...')
    os.makedirs(destination)



def process_destination(destination):
    print('...Existent_directory...')
    if destination.endswith('/'):
        if os.path.exists(destination):
            return 'existing_dir'
        else:
            destination = create_directory(destination)
            return 'non_existing_dir'

    else:
        if os.path.isfile(destination):
            return 'existing_file'
        else:
            return 'non_existing_file'


if __name__ == '__main__':
    print('WELCOME BACK')
    # is_symlink('ABC')

    sources, destination, mode = process_inputs()
    # create_directory(destination)
    # existent_directory(destination)
    # create_directory(destination)
    # for source in sources:
    #     print(is_hardlink(source))

    source_types = []
    source_attributes = []
    for source in sources:
        if check_source_file(source):
            source_type, source_attribute = check_source_file(source)
            source_types.append(source_type)
            source_attributes.append(source_attribute)

    destination_attribute = process_destination(destination)

    if destination_attribute is ['existing_file']:
        if is_hardlink(destination):
            print('is_hardlink')
            os.unlink(destination)
        elif is_symlink(destination):
            print('is_symlink')
            os.unlink(destination)

    copyfile_tool(source, destination)


    #PRINT
    print(source_types, source_attributes, destination_attribute)
