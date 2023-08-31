import requests
import json
import os
import shutil
import stat

def make_dir_writable(function, path, exception):
    """The path on Windows cannot be gracefully removed due to being read-only,
    so we make the directory writable on a failure and retry the original function.
    """
    os.chmod(path, stat.S_IWRITE)
    function(path)

def get_version_info():
    current_version_info = open("version.txt", "r").read().split(" ")
    current_version = float(current_version_info[0])

    distribution = current_version_info[1]

    if distribution == "dev":
        latest_version_info = requests.get("https://raw.githubusercontent.com/Illylynn/Submaker/main/version.txt").text.split(" ")
        latest_version = float(latest_version_info[0])
    else:
        raise ValueError("Invalid distribution type")
    
    return current_version, latest_version

def update():
    
    for f in os.listdir(os.getcwd()):
        if os.path.isdir(os.path.join(os.getcwd(), f)) and not f == ".git":
            shutil.rmtree(os.path.join(os.getcwd(), f), onerror=make_dir_writable)
        else:
            os.remove(os.path.join(os.getcwd(), f))
        
    files = [repo_file["path"] for repo_file in json.loads(requests.get("https://api.github.com/repos/Illylynn/Submaker/git/trees/main?recursive=1").text)["tree"] if "size" in repo_file]
            
    print(files)
            
    for path in files:
        for directory in range(path.count("/")):
            if not os.path.isdir(os.path.join(os.getcwd(), path.split("/")[directory])):
                os.makedirs(os.path.join(os.getcwd(), path.split("/")[directory]))
                        
        split = path.split("/")
        corrected_path = ""

        for sub in split:
            corrected_path = os.path.join(corrected_path, sub)
                    
        if "mp3" in corrected_path or "wav" in corrected_path:
            print(path)
            content = requests.get("https://raw.githubusercontent.com/Illylynn/Submaker/main/%s" % path).content
            f = open(corrected_path, "ab")
        else:
            print(path)
            content = requests.get("https://raw.githubusercontent.com/Illylynn/Submaker/main/%s" % path).text
            f = open(corrected_path, "a", encoding="utf-8")
            
        f.write(content)
        f.close()

update()

