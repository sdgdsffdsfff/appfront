#!/usr/bin/python
#coding: utf-8
#print "Content-type: text/html\n" 
import re
import os
import time

#Image file dir
image_path = 'D:\\IntPassion\\Documents\\workspace\\Deal_uploadfile\\Project\\test\\readme.txt'

#File folder dir
dir_path = 'D:\\IntPassion\\Documents\\workspace\\Deal_uploadfile\\Project\\test\\liph'

#Txt file dir
file_abs_path = 'D:\\IntPassion\\Documents\\workspace\\Deal_uploadfile\\Project\\test\\liph\\note.txt'

#Get current dir
def getcwd():
    return os.getcwd()

#Get all files and file folders in the designated dir
#If not exist, return reminder info
def listdir(dir_path):
    if os.path.exists(dir_path):
        return os.listdir(dir_path)
    else:
        return 'Dir '+ dir_path + 'Not exist'

def isfile(file_path):
    if os.path.exists(file_path):
        return os.path.isfile(file_path)
    else:
        return 'File '+ dir_path + 'Not exist'


if __name__ == '__main__':
    print('Current workspace is ：{0}'.format(getcwd()))
    print('The files and dirs in the current workspace ：',listdir(getcwd()))
    print('#' * 40)
    print(listdir('c:\\test'))
    print('#' * 40)
    print(isfile(image_path))
    print('#' * 40)
    array = os.path.split(image_path)
    print(array)
    #文件全名：20130627_140132Hongten.jpg
    file_full_name = array[1]
    name = os.path.splitext(file_full_name)
    #文件名：20130627_140132Hongten
    file_name = name[0]
    #文件后缀：.jpg
    file_ext = name[1]
    print('File full name:{0},filename：{1},postfix：{2}'.format(file_full_name,file_name,file_ext))
    print('#' * 40)
    #创建空文件夹
    #os.mkdir('E:\\mydir')
    #创建多级目录
    #os.makedirs(r'E:\\bb\\cc')
    print('#' * 40)
    #打开一个文件
    fp = open(file_abs_path,'w+')
    #print('读取文件：{0}的第一行：{1}'.format(file_abs_path,fp.readline()))
    #把文件每一行作为一个list的一个成员，并返回这个list。其实它的内部是通过循环调用readline()来实现的。
    #如果提供size参数，size是表示读取内容的总长，也就是说可能只读到文件的一部分。
    #print('读取文件：{0}所有内容：{1}'.format(file_abs_path,fp.readlines()))
    content = 'this is a test message!!\ngood boy!\ngogo......\nhello,I\'m Hongten\nwelcome to my space!'
    fp.write(content)
    fp.flush()
    fp.close()
    fp = open(file_abs_path,'r+')
    print('Read file：{0} All content：{1}'.format(file_abs_path,fp.readlines()))