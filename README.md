# DGLAB-DOTA2

英雄受伤检测，联动郊狼输出波形

使用方法:

    1.本地准备好python环境
    2.运行setup.py安装依赖
    3.运行main.py，扫码链接郊狼
    4.启动dota2,启动项带-gamestateintegration


实现参考:

    https://github.com/antonpup/Dota2GSI    # dota2自带的gsi工具
    https://pydglab-ws.readthedocs.io/zh/stable/    # pydglab-ws库，集成了郊狼websocket常用操作
    https://github.com/kobopi/CS2-DG_LAB    # cs2与郊狼的联动项目

实现原理：

    1.使用v社自带的gsi工具可快速获取监听并获取游戏内英雄数据
    2.使用pydglab-ws库可快速建立狼与本地PC的websocket链接
    3.不断获取英雄数据，计算受到的伤害并向郊狼发送波形
