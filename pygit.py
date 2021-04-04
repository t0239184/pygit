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

enable_verbose = False


def print_log(msg):
    global enable_verbose
    if enable_verbose:
        if isinstance(msg, list):
            print(" ".join(msg))
        else:
            print(str(msg))


def print_information_from_(commit):
    print_log('\n-------------------------------------------------')

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
    # print_log(commit.parents)
    print_log(commit.summary)
    print_log(['   ', '\n    '.join(list(commit.stats.files))])


def print_modify_file_path_from_(file_list):
    print_log('\nModify File List')
    print_log("=================================================")
    for f_path in sorted(file_list):
        print_log(f_path)


def print_help():
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


def is_not_blank(value):
    return bool(value)


def has_value(index):
    return len(sys.argv) > index and sys.argv[index]


def is_dir(path: str):
    if is_base_on_home(path):
        path = convert_home_path(path)
    return os.path.isdir(str(path))


def folder_not_exist(path):
    return not os.path.exists(str(path))


def check(value: object, func: Callable, err_msg: str):
    if not func(value):
        raise SystemExit(err_msg)


def is_base_on_home(path):
    return str(path).startswith('~')


def convert_home_path(path):
    return str(path).replace('~', os.environ['HOME'])


def main():
    if len(sys.argv) <= 1:
        print_help()
        sys.exit()

    repository_path = ''
    start_commit_hex = ''
    end_commit_hex = ''

    # File zip export path
    export_path = ''

    for i, arg in enumerate(sys.argv[1:], 1):
        if not arg.startswith('-'):
            continue

        if arg in ('--repo', '-r'):
            index = i+1
            check(index, has_value, err_msg='Repository path not be blank.')
            check(sys.argv[index], is_dir,
                  err_msg='The repository path is not a folder.')
            if not sys.argv[index].endswith('/'):
                repository_path = convert_home_path(sys.argv[index]) + '/'
            else:
                repository_path = convert_home_path(sys.argv[index])

        elif arg in ('--verbose', '-v'):
            global enable_verbose
            enable_verbose = True

        elif arg in ('--start', '-s'):
            index = i+1
            check(index, has_value, err_msg='Start commit hex not be blank.')
            check(sys.argv[index], is_not_blank,
                  err_msg='Start commit hex not be blank.')
            start_commit_hex = sys.argv[index]

        elif arg in ('--end', '-e'):
            index = i+1
            check(index, has_value, err_msg='End commit hex not be blank.')
            check(sys.argv[index], is_not_blank,
                  err_msg='End commit hex not be blank.')
            end_commit_hex = sys.argv[index]

        elif arg in ('--out', '-o'):
            index = i+1
            check(index, has_value, err_msg='Export path not be blank.')
            check(sys.argv[index], is_not_blank,
                  err_msg='Export path is not a folder.')
            if not sys.argv[index].endswith('/'):
                export_path = sys.argv[index] + '/'
            else:
                export_path = sys.argv[index]

        else:
            raise SystemExit(f'Invalid argument. arg: {arg}')

    print('Input argument')
    print('------------------------------')
    print('repo  : ', repository_path)
    print('start : ', start_commit_hex)
    print('end   : ', end_commit_hex)
    print('out   : ', export_path)

    if (not repository_path or not start_commit_hex
            or not end_commit_hex or not export_path):
        sys.exit()

    repo = git.Repo(repository_path)
    commits = list(repo.iter_commits(start_commit_hex))
    file_list = set()

    for commit in commits:
        if not commit.stats.files:
            continue

        print_information_from_(commit)

        # Record modify file
        file_list.update(commit.stats.files)

        # Check is last run
        if commit.hexsha == end_commit_hex:
            break

    print_modify_file_path_from_(file_list)

    print_log('\nOutput File folder')
    print_log("=================================================")
    uni_folder_list = set()
    for file_path in sorted(file_list):
        folder = file_path[:-len(file_path.split('/')[-1])]
        uni_folder_list.add(export_path + folder)

    print_log([('\n'.join(uni_folder_list)), '\n'])

    for folder in uni_folder_list:
        if folder_not_exist(folder):
            cmd = f'mkdir -p {str(folder)}'
            print_log(cmd)
            subprocess.call(cmd, shell=True)

    for file in file_list:
        cmd = f'cp {repository_path + str(file)} {export_path + str(file)}'
        print_log(cmd)
        subprocess.call(cmd, shell=True)


if __name__ == '__main__':
    main()
