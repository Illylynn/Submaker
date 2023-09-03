import requests
import json
import os
import shutil
import stat
import time

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
    last_updated = current_version_info[2] if len(current_version_info) > 2 else time.time()

    if distribution == "dev":
        latest_version_info = requests.get("https://raw.githubusercontent.com/Illylynn/Submaker/master/version.txt").text.split(" ")
        latest_version = float(latest_version_info[0])
    else:
        raise ValueError("Invalid distribution type")
    
    return current_version, latest_version, last_updated

def update():
    
    for f in os.listdir(os.getcwd()):
        if not f == ".git":
            if os.path.isdir(os.path.join(os.getcwd(), f)):
                shutil.rmtree(os.path.join(os.getcwd(), f), onerror=make_dir_writable)
            else:
                os.remove(os.path.join(os.getcwd(), f))
        
    files = [repo_file["path"] for repo_file in json.loads(requests.get("https://api.github.com/repos/Illylynn/Submaker/git/trees/master?recursive=1").text)["tree"] if "size" in repo_file]
            
    for path in files:
        for directory in range(path.count("/")):
            if not os.path.isdir(os.path.join(os.getcwd(), path.split("/")[directory])):
                os.makedirs(os.path.join(os.getcwd(), path.split("/")[directory]))
                        
        split = path.split("/")
        corrected_path = ""

        for sub in split:
            corrected_path = os.path.join(corrected_path, sub)
                    
        if "mp3" in corrected_path or "wav" in corrected_path:
            content = requests.get("https://raw.githubusercontent.com/Illylynn/Submaker/master/%s" % path).content
            f = open(corrected_path, "ab")
        else:
            content = requests.get("https://raw.githubusercontent.com/Illylynn/Submaker/master/%s" % path).text
            f = open(corrected_path, "a", encoding="utf-8")
            
        f.write(content)
        f.close()
        
    update_last_updated_info()
    
def update_last_updated_info():
    version_file = open("version.txt", "r")
    
    version_info = version_file.read().split(" ")[0:2]  
    
    time_string = str(time.time())
    
    version_info.append(time_string)
    
    new_contents = " ".join(version_info)
    
    version_file.close()
    
    version_file = open("version.txt", "w")
    version_file.write(new_contents)
    version_file.close()

