"""
批量登录服务器(ssh)并安装带认证的squid代理服务
"""

from logging_conf import logger
from paramiko import client
import paramiko
from paramiko.client import SSHClient
import pandas as pd

AUTH_FILE = 'files/passwords'
SSH_SERVER_FILE = 'files/server.tsv'
SQUID_CONF = 'files/squid.conf'

ssh = SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())


def load_servers(tsv_file):
    """
    从tsv文件中加载要连接ssh服务器
    """
    df = pd.read_csv(tsv_file, sep='\t', header=0, quoting=3, dtype=str)
    for i in range(df.shape[0]):
        yield i, df.loc[i].to_dict()


for i, server in load_servers(SSH_SERVER_FILE):
    logger.info('No.%d, ip: %s' % (i, server['hostname']))
    try:
        # 1. 建立ssh连接
        ssh.connect(**server)
        logger.debug(">>> 1. 建立ssh连接")
        # 2. 安装squid
        stdin, stdout, stderr = ssh.exec_command('yum install squid -y')
        if stdout.channel.recv_exit_status() == 0:
            logger.debug(">>> 2. 安装squid完成")
            with ssh.open_sftp() as sess:
                # 3. 添加认证账号
                sess.put(AUTH_FILE, '/etc/squid/passwords')
                logger.debug(">>> 3. 上传auth文件完成")
                # 4. 更新squid.conf配置文件
                sess.put(SQUID_CONF, '/etc/squid/squid.conf')
                logger.debug(">>> 4. 上传squid.conf完成")
            # 5. systemctl start squid启动服务
            stdout = ssh.exec_command('systemctl start squid')[1]
            if stdout.channel.recv_exit_status() == 0:
                logger.debug('>>> 5. squid服务已启动')
            else:
                logger.error("squid服务启动失败: " + ''.join(stdout.readlines()))
        else:
            logger.error("安装squid失败, ip: %s" % server['hostname'])
    except Exception as err:
        logger.error('处理%s失败', server['hostname'])
    ssh.close()
