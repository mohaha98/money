@echo off
 
title GITһ���ύ
color 2
echo ��ǰĿ¼�ǣ�%cd%
echo;

echo git״̬��git status
git status
echo;

TIMEOUT /T 10

echo ��ʼ��ӱ����git add .
git add .
echo;

set d=%date:~0,10%
set t=%time:~0,8%
echo %d%-%t%

set /p declation=�����ύ��commit��Ϣ:
git commit -m "%d% %t%  ��ע:%declation%"
echo;

 
echo ��������֧��ȡԶ������֧��git pull origin main
git pull origin main
echo;
 
echo ���������ύ��Զ���Լ���֧��git push origin main
git push -u origin main
echo;

echo ִ����ϣ�
echo;
 
pause