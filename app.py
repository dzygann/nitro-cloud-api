import os
import docker
from subprocess import Popen, PIPE
from werkzeug.utils import secure_filename
from flask import Flask, request, Response

app = Flask(__name__)

#upload_folder = "uploads/"
upload_folder = "./"
if not os.path.exists(upload_folder):
    os.mkdir(upload_folder)

client = docker.client.from_env()

app.config['UPLOAD_FOLDER'] = upload_folder


ERROR_MESSAGE_PREFIX = 'Something went wrong\n'


@app.route('/docker-build', methods=['POST'])
def docker_build():
    """
    :return:
    curl -X POST "Content-type: application/json" -d "{\"eif-path\":\"hello.eif\"}" http://localhost:5000/docker-build
    """

    if request.headers.get('Content-Type') == 'application/json':
        request_json = request.json
    else:
        return 'Not supported Content Type'

    if request_json.get('tag') is None:
        return 'Not supported tag is missing'

    # os.getcwd()

    docker_image = client.images.build(path=os.getcwd(),
                                       tag=request_json.get('tag'))

    return "docker created successfully"


@app.route('/docker-images', methods=['GET'])
def docker_images():
    """
    :return:
    curl http://localhost:5000/docker-images
    """

    proc = Popen(
        [
            "docker", "images"
        ],
        stdout=PIPE,
        stderr=PIPE
    )

    out, err = proc.communicate()

    if out:
        return out
    else:
        return "Something went wrong\n" + err.decode('utf-8')


@app.route('/upload', methods=['POST'])
def upload_docker_files():
    """
    :return:
    curl -X POST -H "Content-Type: multipart/form-data" -F "file=@/home/ec2-user/Dockerfile" http://localhost:5000/upload
    """

    files = request.files.getlist("file")
    for file in files:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
    return 'files uploaded successfully'


@app.route('/nitro-build', methods=['POST'])
def build_enclave():
    """
    Run the start command for the prepared enclave
    nitro-cli build-enclave --docker-uri repository:tag
    --docker-dir /path_to/dockerfile_directory
    --output-file enclave_image_filename
    --private-key key.pem
    --signing-certificate certificate.pem

    Example call
    nitro-cli build-enclave --docker-uri sample:latest --output-file sample.eif


    Command returns
    Enclave Image successfully created.
    {
      "Measurements": {
        "HashAlgorithm": "Sha384 { ... }",
        "PCR0": "EXAMPLE59044e337c00068c2c033546641e37aa466b853ca486dd149f641f15071961db2a0827beccea9cade3EXAMPLE",
        "PCR1": "EXAMPLE7783d0c23167299fbe5a69622490a9bdf82e94a0a1a48b0e7c56130c0c1e6555de7c0aa3d7901fbc58EXAMPLE",
        "PCR2": "EXAMPLE4b51589e8374b7f695b4649d1f1e9b528b05ab75a49f9a0a4a1ec36be81280caab0486f660b9207ac0EXAMPLE"
      }
    }

    :return:

    curl -X POST -H "Content-type: application/json" -d "{\"docker-uri\":\"hello-world:latest\", \"output-file\":\"hello-world.eif\"}" http://127.0.0.1:5000/nitro-build

    """

    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        request_json = request.json
    else:
        return 'Not supported'

    if request_json.get('docker-uri') is None \
            or request_json.get('output-file') is None:
        return 'Not supported'

    proc = Popen(
        [
            "/usr/bin/nitro-cli", "build-enclave",
            "--docker-uri", request_json.get('docker-uri'),
            "--output-file", app.config['UPLOAD_FOLDER'] + request_json.get('output-file'),
                             ],
        stdout=PIPE,
        stderr=PIPE
    )

    out, err = proc.communicate()

    if out:
        return out
    else:
        return "Something went wrong\n" + err.decode('utf-8')


@app.route('/nitro-run', methods=['POST'])
def run_enclave():
    """
    Run the start command for the prepared enclave
    nitro-cli run-enclave [--enclave-name enclave_name] [--cpu-count number_of_vcpus | --cpu-ids list_of_vcpu_ids]
    --memory amount_of_memory_in_MiB --eif-path path_to_enclave_image_file [--enclave-cid cid_number] [--debug-mode]

    nitro-cli run-enclave --config config_file.json
    {
        "enclave_name": enclave_name,
        "cpu_count": number_of_vcpus,
        "cpu_ids": list_of_vcpu_ids,
        "memory_mib": amount_of_memory_in_MiB,
        "eif_path": "path_to_enclave_image_file",
        "enclave_cid": cid_number,
        "debug_mode": true|false
    }

    Example Call
    nitro-cli run-enclave --enclave-name my_enclave --cpu-count 2 --memory 1600 --eif-path sample.eif --enclave-cid 10
    nitro-cli run-enclave --cpu-count 2 --memory 512 --enclave-cid 16 --eif-path hello.eif --debug-mode
    or

    nitro-cli run-enclave --config enclave_config.json

    {
        "enclave_name": "my_enclave",
        "cpu_count": 2,
        "memory_mib": 1600,
        "eif_path": "sample.eif",
        "enclave_cid": 10,
        "debug_mode": true
    }

    Command Response

    Start allocating memory...
    Started enclave with enclave-cid: 10, memory: 1600 MiB, cpu-ids: [1, 3]
    {
        "EnclaveName": "my_enclave",
        "EnclaveID": "i-abc12345def67890a-enc9876abcd543210ef12",
        "ProcessID": 12345,
        "EnclaveCID": 10,
        "NumberOfCPUs": 2,
        "CPUIDs": [
            1,
            3
        ],
        "MemoryMiB": 1600
    }

    :return:
     curl -X POST -H "Content-type: application/json" -d "{\"eif-path\":\"hello-world.eif\"}" http://127.0.0.1:5000/nitro-run
    """

    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        request_json = request.json
    else:
        return 'Not supported Content Type'

    if request_json.get('eif-path') is None:
        return 'Not supported'

    proc = Popen(
        [
            "/usr/bin/nitro-cli", "run-enclave",
            "--cpu-count", "2",
            "--memory", "512",
            "--eif-path", app.config['UPLOAD_FOLDER'] + request_json.get('eif-path'),
            "--debug-mode"
        ],
        stdout=PIPE,
        stderr=PIPE
    )

    out, err = proc.communicate()

    if out:
        return out
    else:
        return ERROR_MESSAGE_PREFIX + err.decode('utf-8')


@app.route('/nitro-describe')
def describe_enclave():
    """
    Run the start command for the prepared enclave
    nitro-cli describe-enclaves


    Command response
    [
        {
            "EnclaveName": "my_enclave",
            "EnclaveID": "i-abc12345def67890a-enc9876abcd543210ef12",
            "ProcessID": 12345,
            "EnclaveCID": 10,
            "NumberOfCPUs": 2,
            "CPUIDs": [
                1,
                3
            ],
            "MemoryMiB": 1600,
            "State": "RUNNING",
            "Flags": "NONE"
        }
    ]

    :return:
    curl http://127.0.0.1:5000/nitro-describe
    """
    proc = Popen(
        [
            "/usr/bin/nitro-cli", "describe-enclaves"
        ],
        stdout=PIPE,
        stderr=PIPE
    )

    out, err = proc.communicate()

    if out:
        return out
    else:
        return "Something went wrong\n" + err.decode('utf-8')


@app.route('/nitro-console', methods=['POST'])
def console_enclave():
    """
    Run the start command for the prepared enclave
    nitro-cli console [--enclave-name enclave_name | --enclave-id enclave_id] [--disconnect-timeout number_of_seconds]

    Example Call
    nitro-cli console --enclave-id i-05f6ed443ae428c95-enc173dfe3e2b1c87b --disconnect-timeout 60

    :return:
    """

    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        request_json = request.json
    else:
        return 'Not supported content type'

    if request_json.get('enclave-id') is None:
        return 'Not supported enclave-id'
    proc = Popen(
        [
            "/usr/bin/nitro-cli", "console",
            "--enclave-id", request_json.get('enclave-id')
        ],
        stdout=PIPE,
        stderr=PIPE
    )

    return Response(proc.stdout.readlines(), mimetype='text/event-stream')


@app.route('/nitro-describe-eif', methods=['POST'])
def describe_eif():
    """
    Run the start command for the prepared enclave
    nitro-cli describe-eif --eif-path path_to_enclave_image_file

    Example Call
    nitro-cli describe-eif --eif-path image.eif

    Example Response
    {
      "Measurements": {
        "HashAlgorithm": "Sha384 { ... }",
        "PCR0": "EXAMPLE59044e337c00068c2c033546641e37aa466b853ca486dd149f641f15071961db2a0827beccea9cade3EXAMPLE",
        "PCR1": "EXAMPLE7783d0c23167299fbe5a69622490a9bdf82e94a0a1a48b0e7c56130c0c1e6555de7c0aa3d7901fbc58EXAMPLE",
        "PCR2": "EXAMPLE4b51589e8374b7f695b4649d1f1e9b528b05ab75a49f9a0a4a1ec36be81280caab0486f660b9207ac0EXAMPLE"
      }
    }

    :return:
    curl -X POST -H "Content-type: application/json" -d "{\"eif-path\":\"hello.eif\"}" http://127.0.0.1:5000/nitro-describe-eif
    """

    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        request_json = request.json
    else:
        return 'Not supported'

    if request_json.get('eif-path') is None:
        return 'Not supported'
    proc = Popen(
        [
            "/usr/bin/nitro-cli", "describe-eif",
            "--eif-path", app.config['UPLOAD_FOLDER'] + request_json.get('eif-path')
        ],
        stdout=PIPE,
        stderr=PIPE
    )

    out, err = proc.communicate()

    if out:
        return out
    else:
        return "Something went wrong\n" + err.decode('utf-8')


@app.route('/nitro-terminate', methods=['POST'])
def terminate_enclave():
    """
    Run the start command for the prepared enclave
    nitro-cli terminate-enclave [--enclave-id enclave_id | --enclave-name enclave_name | --all]

    Example Call
    nitro-cli terminate-enclave --enclave-id i-abc12345def67890a-enc9876abcd543210ef12

    Example Response
    Successfully terminated enclave i-abc12345def67890a-enc9876abcd543210ef12.
    {
      "EnclaveID": "i-abc12345def67890a-enc9876abcd543210ef12",
      "Terminated": true
    }

    :return:
    curl -X POST -H "Content-Type: application/json" -d "{\"enclave-id\":\"i-0d757c67e9b9f900d-enc18688a7b17c7c4f\"}" http://127.0.0.1:5000/nitro-terminate
    """

    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        request_json = request.json
    else:
        return 'Not supported'

    if request_json.get('enclave-id') is None:
        return 'Not supported'
    proc = Popen(
        [
            "/usr/bin/nitro-cli", "terminate-enclave",
            "--enclave-id", request_json.get('enclave-id')
        ],
        stdout=PIPE,
        stderr=PIPE
    )

    out, err = proc.communicate()

    if out:
        return err
    else:
        return "Something went wrong\n" + err.decode('utf-8')


@app.route('/stream')
def stream():

    out, err = Popen(['ls', '-l'], stdout=PIPE, stderr=PIPE).communicate()
    return Response(out.splitlines(), mimetype='text/plain')


if __name__ == '__main__':
    app.run(debug=True)