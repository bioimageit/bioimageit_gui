import git
import os
import platform
from subprocess import Popen, PIPE

from bioimageit_core.core.observer import Observable


class GitUpdater(Observable):
    def __init__(self, conda_dir, env_name, local_repo_path, remote_repo_url):
        self.local_repo_path = local_repo_path
        self.remote_repo_url = remote_repo_url
        self.env_name = env_name
        self.conda_dir = conda_dir

    def get_newer_tags(self):
        current_branch = self.git_branch()
        print('current_branch is:', current_branch)
        self.git_checkout_main()
        self.git_pull()
        tags = self.ls_remote_tags()
        print('tags are:', tags)
        
        # find the tags after the current branch
        position = -1
        for i,tag in enumerate(tags):
            if tag in current_branch:
                position = i 
        print('position:', position)        
        return tags[position+1:]        

    def lsremote(self):
        remote_refs = {}
        g = git.cmd.Git()
        for ref in g.ls_remote(self.remote_repo_url).split('\n'):
            hash_ref_list = ref.split('\t')
            remote_refs[hash_ref_list[1]] = hash_ref_list[0]
        return remote_refs

    def ls_remote_tags(self):
        remote_refs = self.lsremote()
        tags = []
        for ref in remote_refs:
            if ref.startswith('refs/tags/'):
                tags.append(ref.replace('refs/tags/', '').replace(' ', ''))
        return tags     

    def git_pull(self):
        repo = git.Repo(self.local_repo_path)
        print(repo.git.pull('origin'))
        print(repo.git.status())

    def git_checkout_main(self):
        repo = git.Repo(self.local_repo_path)
        repo.git.checkout('main')

    def git_checkout_tag(self, tag):
        repo = git.Repo(self.local_repo_path)
        repo.git.checkout(f'tags/{tag}')

    def git_branch(self):
        repo = git.Repo(self.local_repo_path)
        branch = repo.git.branch().split('\n')
        print('active branch:', branch[0])   
        return branch[0]     

    def update_to_tag(self, tag):
        self.git_checkout_tag(tag)   

        if platform.system() == 'Windows':
            condaexe = os.path.join(self.conda_dir, 'condabin', 'conda.bat')
            args_str = '"' + condaexe + '"' + ' activate '+self.env_name+' && python -m pip install ' + self.local_repo_path
            self.notify(f"Conda exec cmd: {args_str}")
            with Popen(args_str, stdout=PIPE, bufsize=1, universal_newlines=True) as p:
                for b in p.stdout:
                    self.notify(b.strip())
            if p.returncode != 0:
                raise Exception(f'return code: {p.returncode}, for command: {p.args}')
        else:    
            condash = os.path.join(self.conda_dir, 'etc', 'profile.d', 'conda.sh')
            args_str = '. "' + condash + '"' + ' && conda activate '+self.env_name+' && pip install ' + self.local_repo_path
            self.notify(f"Conda exec cmd: {args_str}")
            with Popen(args_str, shell=True, executable='/bin/bash', stdout=PIPE, bufsize=1,
                       universal_newlines=True) as p:
                for b in p.stdout:
                    self.notify(b.strip())
            if p.returncode != 0:
                raise Exception(f'return code: {p.returncode}, for command: {p.args}') 
