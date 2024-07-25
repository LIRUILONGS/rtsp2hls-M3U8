from PyInstaller.__main__ import run
#### 打包文件直接执行
if __name__ == '__main__':
    opts = ['main.py',  # 主程序文件
            '--add-data=templates/*;templates',  # 打包包含的html页面
            '--add-data=config.yaml;.',  # 打包包含的html页面
            ]

    run(opts)

