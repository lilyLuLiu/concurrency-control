import paramiko
import runcmd
import json

def get_machine_secret(secret_name:str):
    cmd = "oc get secret {} -o json | jq '.data |= with_entries(.value |= @base64d)'".format(secret_name)
    code, out, _ = runcmd.run_cmd(cmd)
    if code == 0:
        data = json.loads(out).get("data", {})
        return data
    else:
       raise Exception("failed to get secret of machine {}".format(secret_name))

def set_inform_message(machine:str, piprlinerun: str):
    message = "current machine is occuied by pipelinerun {}\nPlease not modify anything affects testing".format(piprlinerun)
    data = get_machine_secret(machine)
    password= data["password"]
    user = data["username"]
    host = data["host"]
    set_remote_motd(host, user, password, message)

def clean_inform_message(machine:str):
    data = get_machine_secret(machine)
    password= data["password"]
    user = data["username"]
    host = data["host"]
    clear_remote_motd(host, user, password)
    
def set_remote_motd(host, user, password, message):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)

    # red Square 
    lines = message.splitlines()
    max_len = max(len(line) for line in lines)
    border = "#" * (max_len + 6)  # length of Square

    banner = border + "\n"
    for line in lines:
        banner += f"#  \033[1;31m{line.ljust(max_len)}\033[0m  #\n"
    banner += border

    # write message into /etc/motd
    cmd = f'echo -e "{banner}" | sudo tee /etc/motd'
    ssh.exec_command(cmd)
    print("set up motd of {}".format(host))

    cmd = f"""
    for tty in $(who | awk '{{print $2}}'); do
        echo -e "\\033[1;31m{message}\\033[0m" > /dev/$tty
    done
    """
    ssh.exec_command(cmd)
    print("message broadcast to all login user of {}".format(host))
    ssh.close()
    

def clear_remote_motd(host, user, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)

    # clear /etc/motd
    cmd = 'echo "" | sudo tee /etc/motd'
    ssh.exec_command(cmd)
    ssh.close()