import git
import shutil




def print_information_from_(commit):
    print('\n-------------------------------------------------')

    # Ignore merge branch information
    if 'Merge branch' in commit.summary:
        print(commit.summary)
        return

    # Print commit message
    print(commit.committed_datetime, '[{}]'.format(commit.hexsha), commit.committer)
    print(commit.parents)
    print(commit.summary)
    print(" ", "\n  ".join(list(commit.stats.files)))


def print_modify_file_path_from_(file_list):
    print("\n=================================================")
    for file_path in sorted(file_list):
        print(file_path)


if __name__ == '__main__':
    # Repository path
    repository_path = '~/Program/ocean-acs-portal-ui/'

    # Commit range
    start_commit_hex = '015c8b3028e2f9fc09e6339d81d7af52ac9cd9bc'
    end_commit_hex = '43147fa625096bb5c91c4abbc14a7d8f23c4367c'

    # File zip export path
    export_path = '~/tmp/'

    repo = git.Repo(repository_path)
    commits = list(repo.iter_commits(start_commit_hex))
    file_list = set()

    for commit in commits:
        if len(commit.stats.files) == 0:
            continue

        print_information_from_(commit)

        # Record modify file
        file_list.update(commit.stats.files)

        # Check is last run
        if commit.hexsha == end_commit_hex:
            break


    print_modify_file_path_from_(file_list)


    for file_path in sorted(file_list):
        folder = file_path[:-len(file_path.split('/')[-1])]
        print(folder)
        try:
            shutil.copytree(repository_path + file_path, export_path)
        except Exception as e:
            print(e)


