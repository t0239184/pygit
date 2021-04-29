"""
This util can help your
generate new feature release note
and export diff file with folder structure
"""
import subprocess
import sys
import os
from collections.abc import Callable

import git

ENABLE_VERBOSE = False
REPOSITORY_PATH = ''
START_COMMIT_HEX = ''
END_COMMIT_HEX = ''
EXPORT_PATH = ''


def print_log(msg):
    """ Print Log By Verbose Flag """
    if ENABLE_VERBOSE:
        if isinstance(msg, list):
            print(" ".join(msg))
        else:
            print(str(msg))


def print_information_from_(commit: object):
    """
    Print Commit Information
    include datetime, hex, author, summary, file list
    """
    print_log('\n\n')

    # Ignore merge branch information
    if 'Merge branch' in commit.summary:
        pass
        # print(commit.summary)
        # return
    if 'Merged in' in commit.summary:
        pass
        # print(commit.summary)
        # return

        # Print commit message
    print_log(f'{commit.committed_datetime}')
    print_log(f'[{commit.hexsha}] {commit.committer}')

    print_log(commit.summary)
    # print_log(commit.message)

    #print_log('type:' + commit.type)
    # print_log(commit.traverse())
    print_log(['   ', '\n    '.join(list(commit.stats.files))])


def print_help():
    """ Print Help Message To Console """
    print('Arguments:')
    print('    -r --repo       repository path')
    print('    -s --start      start commit hex')
    print('    -e --end        end commit hex')
    print('    -o --out        export diff file path')
    print('    -v --verbose    verbose mode')
    print('')
    print('Example:')
    print(['    pygit',
           '--repo ${repo_path}',
           '--start {start_commit_hex}',
           '--end {end_commit_hex}',
           '--export {export_path}'])


def is_not_blank(value: str):
    """ Check Function, Check value is not blank """
    return bool(value)


def has_value(index: int):
    """ Check Function """
    return len(sys.argv) > index and sys.argv[index]


def is_dir(path: str):
    """ Check Function """
    if is_base_on_home(path):
        path = convert_home_path(path)
    return os.path.isdir(str(path))


def folder_exist(path: str):
    """ Check Function """
    return os.path.exists(str(path))


def check(value: object, func: Callable, err_msg: str):
    """ Check by check function """
    if not func(value):
        raise SystemExit(err_msg)


def is_base_on_home(path: str):
    """ determine path is start with home path symble ~ """
    return str(path).startswith('~')


def convert_home_path(path: str):
    """ Convert ~ path to absoulute home path """
    return str(path).replace('~', os.environ['HOME'])


def print_modify_file_path_from_(file_list):
    """ Print All Modify File Path """
    if not file_list:
        return
    print_log('\nModify File List')
    print_log("=================================================")
    for f_path in sorted(file_list):
        print_log(['   ', f_path])


def print_modify_file_folder_from_(file_list):
    """ Print all file folder """
    if not file_list:
        return file_list

    print_log('\nOutput File folder')
    print_log('=================================================')
    uni_folder_list = set()
    for file_path in sorted(file_list):
        folder = file_path[:-len(file_path.split('/')[-1])]
        uni_folder_list.add(EXPORT_PATH + folder)

    print_log(['   ', '\n    '.join(uni_folder_list)])
    return uni_folder_list


def generate_folder_structure_by_(uni_folder_list):
    """ Create taget folder structure """
    if not uni_folder_list:
        return

    print_log('\nGenerate Folder')
    print_log('=================================================')
    for folder in uni_folder_list:
        if folder_exist(folder):
            continue

        cmd = f'mkdir -p {str(folder)}'
        print_log(['   ', cmd])
        subprocess.call(cmd, shell=True)


def copy_file_to_target_by_(file_list):
    """ Copy source file to taget path """
    if not file_list:
        return

    print_log('\nCopy File')
    print_log('=================================================')
    for file in file_list:
        cmd = f'cp {REPOSITORY_PATH + str(file)} {EXPORT_PATH + str(file)}'
        print_log(['   ', cmd])
        subprocess.call(cmd, shell=True)


def command_line(func):
    """ Command Line Args Decorator """
    def wrapper():
        """ Real CLI Checker """
        if len(sys.argv) <= 1:
            print_help()
            sys.exit()

        global REPOSITORY_PATH
        global START_COMMIT_HEX
        global END_COMMIT_HEX
        global EXPORT_PATH
        global ENABLE_VERBOSE

        for i, arg in enumerate(sys.argv[1:], 1):
            if not arg.startswith('-'):
                continue

            if arg in ('--repo', '-r'):
                index = i+1
                check(
                    value=index,
                    func=has_value,
                    err_msg='Repository path not be blank.'
                )
                check(
                    value=sys.argv[index],
                    func=is_dir,
                    err_msg='The repository path is not a folder.'
                )
                REPOSITORY_PATH = (
                    convert_home_path(sys.argv[index])
                    if sys.argv[index].endswith('/')
                    else convert_home_path(sys.argv[index]) + '/'
                )
            elif arg in ('--verbose', '-v'):
                ENABLE_VERBOSE = True

            elif arg in ('--start', '-s'):
                index = i+1
                check(
                    value=index,
                    func=has_value,
                    err_msg='Start commit hex not be blank.'
                )
                check(
                    value=sys.argv[index],
                    func=is_not_blank,
                    err_msg='Start commit hex not be blank.'
                )
                START_COMMIT_HEX = sys.argv[index]

            elif arg in ('--end', '-e'):
                index = i+1
                check(
                    value=index,
                    func=has_value,
                    err_msg='End commit hex not be blank.'
                )
                check(
                    value=sys.argv[index],
                    func=is_not_blank,
                    err_msg='End commit hex not be blank.'
                )
                END_COMMIT_HEX = sys.argv[index]

            elif arg in ('--out', '-o'):
                index = i+1
                check(
                    value=index,
                    func=has_value,
                    err_msg='Export path not be blank.'
                )
                check(
                    value=sys.argv[index],
                    func=is_not_blank,
                    err_msg='Export path is not a folder.'
                )
                EXPORT_PATH = (
                    sys.argv[index]
                    if sys.argv[index].endswith('/')
                    else sys.argv[index] + '/'
                )

            else:
                raise SystemExit(f'Invalid argument. arg: {arg}')

        if (not REPOSITORY_PATH or not START_COMMIT_HEX
                or not END_COMMIT_HEX or not EXPORT_PATH):
            sys.exit()

        print_log('\nInput argument')
        print_log('------------------------------')
        print_log(['    repo  : ', REPOSITORY_PATH])
        print_log(['    start : ', START_COMMIT_HEX])
        print_log(['    end   : ', END_COMMIT_HEX])
        print_log(['    out   : ', EXPORT_PATH])

        return func()
    return wrapper


@command_line
def main():
    """ Main Process """

    repo = git.Repo(REPOSITORY_PATH)
    commits = list(repo.iter_commits(START_COMMIT_HEX, max_count=50))
    file_list = set()

    for commit in commits:
        if not commit.stats.files:
            continue

        print_information_from_(commit)

        # Record modify file
        file_list.update(commit.stats.files)

        # Check is last run
        if END_COMMIT_HEX in (commit.hexsha, commit.hexsha[:8]):
            break

    print_modify_file_path_from_(file_list)
    uni_folder_list = print_modify_file_folder_from_(file_list)

    # Export file
    generate_folder_structure_by_(uni_folder_list)
    copy_file_to_target_by_(file_list)


if __name__ == '__main__':
    main()
