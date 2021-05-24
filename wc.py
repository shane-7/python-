import os
import argparse
import chardet
import easygui
import sys


def get_arg():  # 读取命令行参数，如果没附加参数的话取默认值
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-c", '--count_char', action="store_true")  # 返回文件 file.c 的字符数
    group.add_argument("-w", '--count_words', action="store_true")  # 返回文件 file.c 的词的数目
    group.add_argument("-l", '--count_lines', action="store_true")  # 返回文件 file.c 的行数
    group.add_argument("-a", '--all_data', action="store_true")  # 返回更复杂的数据（代码行 / 空行 / 注释行）
    group.add_argument("-f", '--file_type', action="store_true")  # 是哪一种语言,如看不出属于任何语言，就输出 TXT

    parser.add_argument("-s", '--sub_dir', action="store_true")  # 在目录及子目录里找文件
    parser.add_argument("-n", '--disp_num', default=5, type=int)  # 显示的个数，默认5个，值为-1时全部显示
    parser.add_argument('path')  # 路径（文件名）
    opt = parser.parse_args()
    return opt


def open_file(file_name):  # 读取代码文件
    sample_len = min(100, os.path.getsize(file_name))  # 采样长度,最长采样长度为100，可调节
    raw = open(file_name, 'rb').read(sample_len)  # 读取片段
    detect = chardet.detect(raw)  # 检测编码
    code = open(file_name, 'r', encoding=detect['encoding'], errors='ignore')  # 根据检测到的编码方式打开code
    return code


def read_code(file_name):  # 读取指定代码文件中的字符串
    code = open_file(file_name)  # 打开代码文件
    strs = code.read()  # 文本读入字符串，全变成小写
    code.close()  # 关code
    strs = strs.lower()  # 全变成小写
    return strs  # 作为一个字符串返回


def is_number(s):  # 判断是不是数字
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


def is_code_file(filename):  # 判断是不是代码文件
    return any(filename.endswith(extension) for extension in ['.c', '.h', '.py', '.java', '.md', '.txt'])


def count_char(file_name):  # 返回文件 file.c 的字符数
    strs = read_code(file_name)  # 读文件
    print('Num of char:', len(strs))
    return len(strs)


def count_words(file_name, disp_num):  # 返回文件 file.c 的词的数目
    strs = read_code(file_name)  # 读文件
    letters = ['a', 'b', 'c', 'd', 'e',  # 字母表
               'f', 'g', 'h', 'i', 'j',
               'k', 'l', 'm', 'n', 'o',
               'p', 'q', 'r', 's', 't',
               'u', 'v', 'w', 'x', 'y', 'z']
    word_frequency = {}

    for letter in strs:  # 如果不是字母，也不是空格的字符，也不是数字，就全变成空格
        if letter not in letters and letter != ' ' and not is_number(letter):
            strs = strs.replace(letter, ' ')
    words = strs.split()  # 用空格分词

    for word in words:
        count = word_frequency.get(word, 0)  # 记录词出现的频率
        word_frequency[word] = count + 1

    result = sorted(word_frequency.items(), key=lambda k: k[1], reverse=True)  # sorted排序

    print('\nTotal words:', len(words))
    print('Num of word types:', len(result))
    print('The most frequent words:')  # 显示出现频率最高的词
    if disp_num == -1:  # 显示的个数，值为-1就全显示
        for item in result:
            print('{}:{}'.format(item[0], item[1]))
    else:
        if disp_num > len(result):  # 如果disp_num比单词个数还多，则全显示了好了
            disp_num = len(result)
        for i in range(disp_num):
            print('{}:{}'.format(result[i][0], result[i][1]))


def count_lines(file_name):  # 返回文件 file.c 的行数
    code = open_file(file_name)  # 打开txt
    count = len(code.readlines())
    print('Lines:', count)


def file_type(file_name):  # 说明这个文件是哪一种语言的
    code = open_file(file_name)  # 打开txt
    lines = code.readlines()  # 以行的形式读代码
    c_feature_count = 0  # C语言特征的个数
    python_feature_count = 0
    for i in range(5):  # 通过前5行判断是哪个语言
        if 'include' in lines[i]:  # 带include就当是c，带import就当是Python
            c_feature_count += 1
        if 'import' in lines[i]:
            python_feature_count += 1
    if c_feature_count != 0 or python_feature_count != 0:  # 啥都不带就当是txt
        if c_feature_count > python_feature_count:
            code_type = 'c'
        else:
            code_type = 'python'
    else:
        code_type = 'txt'

    print('Code type is:', code_type)
    return code_type


def all_data(file_name):  # 返回更复杂的数据（代码行 / 空行 / 注释行）
    code = open_file(file_name)  # 打开txt
    code_type = file_type(file_name)
    lines = code.readlines()
    num_lines = len(lines)  # 总行数
    code_line_count = 0  # 代码行数
    blank_line_count = 0  # 空行数
    comment_line_count = 0  # 注释行数
    comment_symbol_count_1 = 0  # 块注释符计数 '''
    comment_symbol_count_2 = 0  # 块注释符计数 """
    comment_block_flag = False  # 块注释标志位
    for line in lines:  # 逐行判断
        if len(line) <= 1:  # 如果这行字符数小于等于1，则认为是空白行
            blank_line_count += 1
        else:
            comment_flag = False  # 注释标志位，默认是false
            if code_type == 'c':  # 根据语言类型分别判断
                if '//' in line:  # 单行注释
                    comment_flag = True
                if '/*' in line:  # 多行注释的开头和结尾所在行都认为是注释行
                    comment_block_flag = True
                if '*/' in line:
                    comment_block_flag = False
                    comment_flag = True
                if comment_block_flag is True:  # 多行注释中的行都认为是注释行
                    comment_flag = True
                if comment_flag is True:
                    comment_line_count += 1
                else:  # 不是空白行，不是注释行，就是代码行
                    code_line_count += 1
            if code_type == 'python':
                if '#' in line:
                    comment_flag = True

                if '\'\'\'' in line:  # Python的块注释根据注释符出现次数判断是不是多行注释
                    comment_symbol_count_1 += 1
                    comment_flag = True
                if '\"\"\"' in line:
                    comment_symbol_count_2 += 1
                    comment_flag = True

                if comment_symbol_count_1 % 2 == 1 or comment_symbol_count_2 % 2 == 1:  # 如果注释符不成对就是多行注释
                    comment_block_flag = True
                else:
                    comment_block_flag = False

                if comment_block_flag is True:
                    comment_flag = True

                if comment_flag is True:
                    comment_line_count += 1
                else:
                    code_line_count += 1

    print('Total lines:', num_lines)
    print('Code line count:', code_line_count)
    print('Blank line count:', blank_line_count)
    print('Comment line count:', comment_line_count)


def choose_mode_arg(file_name):  # 选择模式
    opt = get_arg()
    disp_num = opt.disp_num
    if opt.count_char:  # 返回文件 file.c 的字符数
        count_char(file_name)
    if opt.count_words:  # 返回文件 file.c 的词的数目
        count_words(file_name, disp_num)
    if opt.count_lines:  # 返回文件 file.c 的行数
        count_lines(file_name)
    if opt.all_data:  # 返回更复杂的数据（代码行 / 空行 / 注释行）
        all_data(file_name)
    if opt.file_type:  # 说明这个文件是哪一种语言的
        file_type(file_name)


def choose_mode_gui(mode, file_name):  # 选择模式
    disp_num = 5
    if mode == 'count_char':  # 返回文件 file.c 的字符数
        count_char(file_name)
    if mode == 'count_words':  # 返回文件 file.c 的词的数目
        count_words(file_name, disp_num)
    if mode == 'count_lines':  # 返回文件 file.c 的行数
        count_lines(file_name)
    if mode == 'all_data':  # 返回更复杂的数据（代码行 / 空行 / 注释行）
        all_data(file_name)
    if mode == 'file_type':  # 说明这个文件是哪一种语言的
        file_type(file_name)


def gui_mode():
    load_mode_list = ['file', 'folder']
    load_mode = easygui.ccbox(msg='load a file or folder?', title=' ', choices=load_mode_list)

    choicess_list = ['count_char', 'count_words', 'count_lines', 'all_data', 'file_type']
    mode = easygui.buttonbox(msg='choose mode:', title=load_mode, choices=choicess_list)

    if load_mode == 0:  # 递归遍历目录下的所有子目录
        path = easygui.diropenbox(msg='please choose a path')
        os.chdir(path)
        for dirpath, dirs, files in os.walk('.'):  # 递归遍历当前目录和所有子目录的文件和目录
            for name in files:  # files保存的是所有的文件名
                if is_code_file(name):
                    print('--------------------{}--------------------'.format(name))
                    file_name = os.path.join(dirpath, name)  # 加上路径，dirpath是遍历时文件对应的路径
                    choose_mode_gui(mode, file_name)
    else:
        file_name = easygui.fileopenbox(msg='please choose a file')
        choose_mode_gui(mode, file_name)


def arg_mode():
    opt = get_arg()
    path = opt.path
    if opt.sub_dir:  # 递归遍历目录下的所有子目录
        os.chdir(path)
        for dirpath, dirs, files in os.walk('.'):  # 递归遍历当前目录和所有子目录的文件和目录
            for name in files:  # files保存的是所有的文件名
                if is_code_file(name):
                    print('--------------------{}--------------------'.format(name))
                    file_name = os.path.join(dirpath, name)  # 加上路径，dirpath是遍历时文件对应的路径
                    choose_mode_arg(file_name)
    else:
        choose_mode_arg(path)


def main():
    gui_mode()
    # arg_mode()


if __name__ == "__main__":
    main()
