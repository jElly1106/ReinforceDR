# backend

backend</br>
├── __init__.py                             # 项目后端初始化文件</br>
├── README.md                               # 项目后端说明文档</br>
├── main.py                                 # 项目后端入口文件</br>
├── requirements.txt                        # 项目后端依赖包</br>
├── app.py                                  # 项目后端创建文件</br>
├── api                                     # 项目后端API接口文件夹</br>
│   ├── __init__.py                         # API接口初始化文件</br>
│   ├── user.py                             # 用户相关API接口</br>
│   └── ......                              # 其他API接口</br>
├── common                                  # 项目后端工具文件夹</br>
│   ├── __init__.py                         # 工具文件初始化</br>
│   ├── config.py                           # 项目配置文件</br>
│   ├── decorators.py                       # 项目装饰器文件</br>
│   ├── extensions.py                       # 项目扩展工具文件</br>
│   ├── response.py                         # 项目响应文件</br>
│   └── utils.py                            # 项目工具文件</br>
├── core                                    # 项目后端模型推理文件夹</br>
│   ├── __init__.py                         # 模型推理文件初始化</br>
│   ├── model.py                            # 项目模型推理文件</br>
│   └── ......                              # 其他模型推理文件</br>
├── database                                # 项目后端数据库文件夹</br>
│   ├── __init__.py                         # 数据库初始化文件</br>
│   ├── models.py                           # 数据库模型文件</br>
│   └── ......                              # 其他数据库文件</br>
├── static                                  # 项目后端静态文件夹</br>
│   ├── __init__.py                         # 静态文件初始化</br>
│   ├── default                             # 默认静态文件夹</br>
│   │   ├── default.jpg                     # 默认图片</br>
│   │   └── ......                          # 其他默认图片</br>
│   ├── upload                              # 上传文件夹</br>
│   │   ├── sth                             # 上传图片子文件夹</br>
│   │   │   ├── sth.jpg                     # 上传图片</br>
│   │   │   └── ......                      # 其他上传图片</br>
|   └── └── ......                          # 其他静态文件</br>
└── ......                                  # 其他文件</br>
