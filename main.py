import subprocess
import traceback
from pathlib import Path
import gitlab
import argparse


def process(project, REPOS_PATH):
    url = project.ssh_url_to_repo
    try:
        print(f'processing: {url}')
        # if 'gitlab.alberblanc.com' not in url:
        #     print('skipping')
        #     return

        path = project.path_with_namespace
        repo_path = REPOS_PATH / path
        if repo_path.is_dir():
            print('already cloned')

        name = repo_path.name
        result = subprocess.run(
            # clone last commit, pack, remove dir
            # f'git clone --depth 1 --recursive {url} {repo_path} && cd {repo_path.parent} && zip -r -9 {name}.zip {name} >> /dev/null && rm -rf {name}',
            # clone repo
            f'git clone --recursive {url} {repo_path}',
            shell=True)
        result.check_returncode()

        with Path('processed.txt').open('a') as fp:
            fp.write(f'{url}\n')

    except Exception:
        print(f'Error procesing {url}')
        traceback.print_exc()


def main():
    parser = argparse.ArgumentParser(description='Get all projects from gitlab download and pack al with zip.')
    parser.add_argument('--url', default='https://gitlab.alberblanc.com/', help='Gitlab url')
    parser.add_argument('--token', help='Gitlab private token', required=True)

    args = parser.parse_args()

    gl = gitlab.Gitlab(url=args.url, private_token=args.token)
    REPOS_PATH = Path(__file__).parent / 'repos'

    for i in range(1,10):
        for project in gl.projects.list(per_page=100, page=i, as_list=True, order_by='last_activity_at'):
            print(project.name)
            process(project, REPOS_PATH)


if __name__ == '__main__':
    main()