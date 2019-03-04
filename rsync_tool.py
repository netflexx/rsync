#!/usr/bin/env python3

import os
import argparse
import hashlib


def get_size(object):
    return os.path.getsize(object)


def check_size(source, destination):
    return get_size(source) == get_size(destination)


def check_time(source, destination):
    return os.stat(source).st_mtime == os.stat(destination).st_mtime


def check_update(source, destination):
    time_source = os.stat(source).st_mtime
    time_destination = os.stat(source).st_mtime
    return time_source < time_destination


def check_sum(source, destination):
    md5_source = hashlib.md5(source.encode()).hexdigest()
    md5_destination = hashlib.md5(destination.encode()).hexdigest()
    return md5_source == md5_destination


def is_hardlink(object):
    return os.stat(object).st_nlink > 1


def is_symlink(object):
    return os.path.islink(object)


def is_directory(object):
    return os.path.isdir(object)


def is_existing(object):
    return os.path.exists(object)


def set_am_time(source, destination):
    source_file_stat = os.stat(source)
    os.utime(destination, (source_file_stat.st_atime,
                           source_file_stat.st_mtime))
    return True


def set_permission(source, destination):
    source_file_stat = os.stat(source)
    os.chmod(destination, source_file_stat.st_mode)
    return True


def destination_path(source, destination):
    return destination + '/' + source.split('/')[-1]


def check_sum(source, destination):
    md5_source = hashlib.md5(source.encode()).hexdigest()
    md5_destination = hashlib.md5(destination.encode()).hexdigest()
    return md5_source == md5_destination


def process_inputs():

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--checksum",
                        action="store_true",
                        help="skip based on checksum, not mod-time & size")
    parser.add_argument("-u", "--update",
                        action="store_true",
                        help='skip files that are newer on the receiver')
    parser.add_argument("-r", "--recursive",
                        action="store_true",
                        help="copy multifile")
    parser.add_argument("source", nargs="+", help="file source")
    parser.add_argument("destination", help='file destination')
    args = parser.parse_args()
    return args


def handle_arguments(args):

    if args.recursive and not os.path.exists(args.destination):
        os.mkdir(args.destination)

    for source in args.source:
        if handling_error(source):
            break

        if args.recursive and os.path.isdir(source):
            recursive(source, args.destination)
        else:
            main(source, args.destination)


def handle_symlink(source, destination):
    '''
    copy_file symlinks as symlinks
    '''
    if is_existing(destination) and not is_directory(destination):
        os.unlink(destination)
    if is_directory(destination):
        os.symlink(os.readlink(source),
                   destination_path(source, destination))
    else:
        os.symlink(os.readlink(source), destination)
    return True


def handle_hardlink(source, destination):
    '''
    Preserve hard links
    '''
    if is_existing(destination) and not is_directory(destination):
        os.unlink(destination)
    if is_directory(destination):
        os.link(source, destination_path(source, destination))
    else:
        os.link(source, destination)
    return True


def handling_error(source):
    '''
    Catch error
    '''
    try:
        file = os.open(source, os.O_RDONLY)
    except FileNotFoundError:
        print('rsync: link_stat "' + os.path.abspath(source) +
              '" failed: No such file or directory (2)')
        return True
    except PermissionError:
        print('rsync: send_files failed to open "' +
              os.path.abspath(source) + '": Permission denied (13)')
        return True
    else:
        os.close(file)
        return False


def copy_file(source, destination):
    '''
    Rewrite content
    '''
    source_file = os.open(source, os.O_RDONLY)
    destination_file = os.open(destination, os.O_CREAT | os.O_WRONLY)
    source_content = os.read(source_file, get_size(source))
    os.write(destination_file, source_content)
    os.close(destination_file)
    os.close(source_file)
    set_default(source, destination)
    return True


def update_content(source, destination):
    '''
    only copy the parts that are different
    between the source file and the destination file
    '''
    # open and read content of 2 file
    source_file = os.open(source, os.O_RDONLY)
    source_content = os.read(source_file, get_size(source))
    destination_file = os.open(destination, os.O_RDWR | os.O_CREAT)
    destination_content = os.read(destination_file, get_size(destination))
    count = 0
    # rewrite the parts that are different
    while count < get_size(source):
        os.lseek(source_file, count, 0)
        os.lseek(destination_file, count, 0)
        if count < len(destination_content):
            if destination_content[count] != source_content[count]:
                os.write(destination_file, os.read(source_file, 1))
        else:
            os.write(destination_file, os.read(source_file, 1))
        count += 1

    os.close(source_file)
    os.close(destination_file)
    set_default(source, destination)
    return True


def set_default(source, destination):
    '''
    Set mod time and permission for the destination
    '''
    set_am_time(source, destination)
    set_permission(source, destination)
    return True


def recursive(source, destination):
    '''
    Recursively create directories
    '''
    for element in list:
        if os.path.isdir(element):
            os.mkdir(destination + '/' + element)
            recursive(element, destination + '/' + element)
        else:
            main(source, destination)
    return True


def main(source, destination):

    '''
    handle main
    '''
    if is_hardlink(source):  # check hard link
        handle_hardlink(source, destination)

    elif is_symlink(source):  # check sym link
        handle_symlink(source, destination)

    elif is_directory(destination):  # if the destination is directory
        copy_file(source, destination_path(source, destination))

    elif args.checksum:  # -c option
        if check_sum(source, destination):
            copy_file(source, destination)

    elif args.update:  # -u option
        if check_update(source, destination):
            copy_file(source, destination)

    # rewrite all or rewrite the parts different
    elif is_existing(destination):
        if not check_size(source, destination) or \
           not check_time(source, destination):
            if get_size(source) >= get_size(destination):
                update_content(source, destination)
            else:
                os.unlink(destination)
                copy_file(source, destination)
    else:
        copy_file(source, destination)


if __name__ == '__main__':

    args = process_inputs()
    handle_arguments(args)
