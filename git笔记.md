下载客户端git，配置环境变量
设置用户名 邮箱

把公钥上传到github

新建文件夹 

文件夹目录打开命令窗，输入git init，把它变成Git仓库

提交代码到远程仓库之前，要先pull拉取

项目复制到这个文件夹里面，再通过git add .把项目添加到仓库

再通过git commit -m "注释内容"把项目提交到仓库

在Github上设置好SSH密钥后，新建一个远程仓库，通过git remote add origin https://github.com/guyibang/TEST2.git将本地仓库和远程仓库进行关联

最后通过git push -u origin master（分支名字）把本地仓库的项目推送到远程仓库（也就是Github）上



解除ssl认证git config --global http.sslVerify "false"



删除仓库 再添加远程仓库

git remote rm origin

git remote add origin git@gitee.com:ferry18829517728/vue_shop.git

https://github.com/mohaha98/test.git

查看命令   git config --local --list

查看当前用户名  git config user.name

查看邮箱  git config user.email

修改用户名  git config user.name xxx   git config user.email xxx

执行`ssh-keygen –t rsa –C "git仓库邮箱"`，重新生成[密钥]

执行`git config --global user.name "git用户名"`，重新配置本地用户名

执行`git config --global user.email "git登录邮箱"`，重新配置本地邮箱



```
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin git@github.com:mohaha98/ApiTest.git
git push -u origin main
```

git@github.com:mohaha98/spider.git



<<<<<<< HEAD
切换分支

git checkout branchName
=======
学习啊 记得
>>>>>>> eb4f93e7b05e074b94c04fe3abb8d784c85a19e5
