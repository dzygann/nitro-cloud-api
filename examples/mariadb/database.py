import io
import subprocess
import shlex

program_mariadb = "mariadb"
host_arg = "-h"
host_value = "localhost"
user_arg = "-u"
user_value = "user"
pass_arg = "-p"
pass_value = "password"
exec_arg = "-e"
exec_value = "select current_user()"

# args = "-h localhost -u user -ppassword -e \"select_current_user()\""
# commandCreateSchema = 'mariadb -h localhost -u user -ppassword -e \"CREATE SCHEMA testdb2 DEFAULT CHARACTER SET utf8 COLLATE utf8_bin;\"'
# commandString = 'mariadb -h localhost -u user -ppassword -e \"select current_user()\"'
commandString = 'GRANT ALL PRIVILEGES ON testdb2.* TO \'user\'@\'localhost\';'

command = shlex.split(commandString)
#proc = subprocess.run(commandString, shell=True, capture_output=True, text=True, check=True)
proc = subprocess.run(commandString, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True, check=True)
for line in proc.stdout.splitlines():
    print("stdout:", line)

for line in proc.stderr.splitlines():
    print("stderr: ", line)

# result = subprocess.Popen([program_mariadb, host_arg, host_value, user_arg, user_value, pass_arg, pass_value, exec_arg, exec_value],
#                           shell=True, text=True)
# print(result.communicate()[0])
#
# print("stdout:", result.stdout)
# print("stderr:", result.stderr)