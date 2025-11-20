import os
import runcmd 
import json 
import time 
import inform

NAMESPACE = os.environ.get("NAMESPACE", "devtoolsqe--pipeline")
TOKEN_PATH = os.environ.get("TOKEN_PATH")
SERVER = os.environ.get("SERVER", "https://api.gpc.ocp-hub.prod.psi.redhat.com:6443")
MACHINE_STATUS_CM = os.environ.get("MACHINE_CM", "machine-status-config")
LABEL_MACHINE_PR = os.environ.get("LABEL_MACHINE_PR", "tester")
LAEBL_MACHINE_TASK = os.environ.get("LAEBL_MACHINE_TASK", "builder")
LABEL_TASK = os.environ.get("LABEL_TASK","")


WAIT_FINISH_RUNS = []
WAIT_TASK_FINISH = []


def set_project():
    cmd = "export KUBECONFIG=/tmp/kubeconfig;oc project {}".format(NAMESPACE)
    code, out, err = runcmd.run_cmd(cmd)
    if code == 0:
        print(out)
    else:
        print(out)
        print(err)
        raise Exception("can't access to project {}".format(NAMESPACE))

def get_pending_runs():
    cmd = "tkn pipelinerun list | grep Pending"
    code, out, err = runcmd.run_cmd(cmd)
    pendings = []
    if code==0 and out != "" :
        lines = out.splitlines()
        pendings = [line.split()[0] for line in lines] 
    else:
        print(out)
        print(err)
        print("Not find any pending pipelinerun")
    return pendings
    
def get_run_lable(run_name: str, label_name: str):
    cmd = "oc get pipelinerun {0} -o json | jq -r '.metadata.labels[\"{1}\"]'".format(run_name, label_name)
    code, out, _ = runcmd.run_cmd(cmd)
    if code==0 and out.strip() != "null" :
        return out.strip()
    else:
        return None

def get_machine_status(machine: str):
    cmd = "oc get cm {} -o json | jq -r '.data[\"{}\"]'".format(MACHINE_STATUS_CM, machine)
    code, out, _ = runcmd.run_cmd(cmd)
    if code==0 and out.strip() != "null" :
        return out.strip()
    else:
        print(f"failed to find {machine} in configmap {MACHINE_STATUS_CM}")
        return None

def change_machine_status(machine: str, status: str):
    patch_body = f'[{{\"op\": \"replace\", \"path\": \"/data/{machine}\", \"value\": \"{status}\"}}]'
    cmd = "oc patch cm {} --type=json --patch '{}'".format(MACHINE_STATUS_CM, patch_body)
    code, out, _ = runcmd.run_cmd(cmd)
    if code == 0:
        print(f"successfully set {machine} to {status}")
        return True
    else:
        print(f"failed to change {machine} status to {status}")
        print(out)
        return False

def check_run_finish(run: str):
    cmd = " oc get pipelinerun {} -o json | jq .status.conditions[0].status".format(run)
    code, out, _ = runcmd.run_cmd(cmd)
    if code==0 and out != "" :
        out = out.strip()
        if out == "\"Unknown\"":
            return False
        elif out == "\"False\"" or out == "\"True\"":
            return True
        else:
            raise Exception("the status of run is {}".format(out))
    else:
        raise Exception("failed to get the status of run {}".format(run))

def monitor_runs_finish():
    new_wait_list = []
    global WAIT_FINISH_RUNS
    if len(WAIT_FINISH_RUNS) > 0:
        print("************** Monitor pipelinerun finish **************")
    for run,machine in WAIT_FINISH_RUNS:
        print(f"--- {run} ---")
        status = check_run_finish(run)
        if status == True:
            print(f"pipelinerun {run} has finished, set {machine} to free")
            change_machine_status(machine, "free")
            inform.clean_inform_message(machine)
        else:
            print(f"pipelinerun {run} is still running, machine {machine} is busy")
            new_wait_list.append((run, machine))
    WAIT_FINISH_RUNS = new_wait_list

def start_pending_run(run: str):
    cmd = "oc get pipelinerun {} -o json  | jq '.spec.status = \"\"' | oc apply -f -".format(run)
    code, out, _ = runcmd.run_cmd(cmd)
    if code == 0:
        print(f"sucessfully start pipelinerun {run}")
    else:
        raise Exception("failed to start pipelinerun {}".format(run))  

def monitor_pending_run():
    pendings = get_pending_runs()
    print("************** Monitor pending run **************")
        
    for pend in pendings:
        print(f"--- {pend} ---")
        use_second_machine = False
        status2 = "free"

        machine1 = get_run_lable(pend, LABEL_MACHINE_PR)
        machine2 = get_run_lable(pend, LAEBL_MACHINE_TASK)
        if machine1 != None:
            status1 = get_machine_status(machine1)
        else:
            print(f"{pend} not correctly config the {LABEL_MACHINE_PR} label")
            continue
        if machine2 != None:
            status2 = get_machine_status(machine2)
            use_second_machine = True
        
        if status1 == "free" and status2 == "free":
            print(f"machine {machine1} is available")
            inform.set_inform_message(machine1, pend)
            change_machine_status(machine1, "busy")
            WAIT_FINISH_RUNS.append((pend, machine1))

            if use_second_machine:
                print(f"machine {machine2} is available")
                inform.set_inform_message(machine2, pend)
                change_machine_status(machine2, "busy")
                WAIT_TASK_FINISH.append((pend, machine2))
            
            print(f"start pipelinerun {pend}")
            start_pending_run(pend)
            continue

        if status1 == "busy":
            print(f"pipelinerun {pend} waits for machine {machine1}")
        elif status2 == "busy":
            print(f"pipelinerun {pend} waits for machine {machine2}")
        else:
            print(f"machine {machine1} status is {status1} !!!")
            if use_second_machine:
                print(f"machine {machine2} status is {status2} !!!")

def check_task_finish(pipelinerun: str, task_name: str):
    cmd = "oc get taskrun -l tekton.dev/pipelineRun={} | grep {}".format(pipelinerun, task_name)
    code, out, _ = runcmd.run_cmd(cmd)
    if code==0 and out != "" :
        status = out.split()[1]
        if status == "True":
            return True
        else:
            return False
    else:
        print(f"task {task_name} in pipelineRun {pipelinerun} not find")
        return False

def monitor_task():
    new_wait_list = []
    global WAIT_TASK_FINISH
    if len(WAIT_TASK_FINISH) > 0:
        print("************** Monitor tasks **************")
    for run, machine in WAIT_TASK_FINISH:
        print(f"--- {run} {machine} ---")
        status =  check_task_finish(run, LABEL_TASK)
        if status == True:
            print(f"task {LABEL_TASK} of pipelinerun {run} has finished, set {machine} to free")
            change_machine_status(machine, "free")
            inform.clean_inform_message(machine)
        else:
            print(f"task {LABEL_TASK} of pipelinerun {run} is not finish, machine {machine} is busy")
            new_wait_list.append((run, machine))
    WAIT_TASK_FINISH = new_wait_list

if __name__ == "__main__":
    set_project()
    
    while True:
        monitor_task()
        monitor_pending_run()
        monitor_runs_finish()      
        print("\nWAIT_FINISH_RUNS:")
        print(WAIT_FINISH_RUNS)
        print("\nWAIT_TASK_FINISH")
        print(WAIT_TASK_FINISH)
        print("\n\nsleep 1 minute\n")
        time.sleep(1*60)