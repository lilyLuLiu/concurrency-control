from flask import Flask, render_template, jsonify, request, redirect, url_for
import configmap
import log
import control

app = Flask(__name__)

def get_log_contents():
    try:
        with open(log.INFO_LOG_FILE, 'r') as f:
            lines = f.readlines()
            return ''.join(lines[-100:])
    except FileNotFoundError:
        return "Log file not found."

@app.route('/')
def machine_status():
    statuses = configmap.get_all_machine_statuses()
    wait_finish_runs = configmap.get_wait_finish_runs()
    log_contents = get_log_contents()
    project_name = app.config.get("PROJECT_NAME", "Unknown")

    machine_to_run = {machine: run for run, machine in wait_finish_runs}
    machine_info = {}
    for machine, status in statuses.items():
        machine_info[machine] = {
            'status': status,
            'run': machine_to_run.get(machine)
        }

    return render_template(
        'status.html', 
        machine_info=machine_info, 
        wait_finish_runs=wait_finish_runs, 
        log_contents=log_contents, 
        project_name=project_name
    )

@app.route('/manage_machine', methods=['POST'])
def manage_machine():
    action = request.form.get('action')
    machine_name = request.form.get('machine_name')
    user_name = request.form.get('user_name')

    if action == 'reserve' and machine_name and user_name:
        status = control.get_machine_status(machine_name)
        if status == 'free':
            control.change_machine_status(machine_name, f"busy (reserved by {user_name})")
    elif action == 'return' and machine_name:
        status = control.get_machine_status(machine_name)
        if status and 'reserved by' in status:
            control.change_machine_status(machine_name, 'free')

    return redirect(url_for('machine_status'))

@app.route('/log')
def log_data():
    return jsonify(log=get_log_contents())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)