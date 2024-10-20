@echo off
 
title GIT一键提交
color 2
echo 当前目录是：%cd%
echo;

echo git状态：git status
git status
echo;

TIMEOUT /T 10

echo 开始添加变更：git add .
git add .
echo;

set d=%date:~0,10%
set t=%time:~0,8%
echo %d%-%t%

set /p declation=输入提交的commit信息:
git commit -m "%d% %t%  备注:%declation%"
echo;

 
echo 本地主分支拉取远程主分支：git pull origin main
git pull origin main
echo;
 
echo 将变更情况提交到远程自己分支：git push origin main
git push -u origin main
echo;

echo 执行完毕！
echo;
 
pause