自动批量安装squid代理
===

## 安装过程
### 生成认证用户与密码
```
htpasswd -c passwords authorized_user
```
输入两次密码后在当前目录生成passwords文件。
```
htpasswd -v passwords authoried_user
```
输入密码验证账号密码是否可用

### squid安装与配置
```
安装squid
yum install squid -y
```

配置高匿代理与强制刷新(防止缓存)参见配置文件[squid.conf](files/squid.conf)


参考:
[squid 高匿设置](https://www.cnblogs.com/vijayfly/p/5800038.html)
