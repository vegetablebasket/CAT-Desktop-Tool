# CAT-Desktop-Tool

## 项目规划
第一阶段：需求工程  
目标：  
·梳理功能需求  
·使用场景建模  
·数据建模(ER图等)  
最后要求输出文档：  
《功能需求文档》 项目功能清单+简单说明  
《典型用户使用流程》 从用户视角描述一次完整翻译任务  
《用例图》 展示用户可以执行哪些操作  
《数据结构设计文档》 包括主要数据表、字段、关系图  
《界面流程图》 展示用户界面的操作流程/模块切换  
《调研分析报告》 介绍某款已有CAT软件的核心功能、界面截图、可借鉴功能  
分工：  
A:  
1、总结功能需求  
2、写一个典型用户使用流程  
3、初步模块划分  
B:  
1、写出用户操作流程  
2、绘制1、2个用例图或界面流程图草图  
C:  
1、设计数据库中有哪些表  
2、写出字段设计和关系  
D：  
1、调研一个已有CAT软件  
2、比较功能，是否可以借鉴  
3、提出1、2个可能的扩展功能  

第二阶段：软件设计  
目标：  
·系统模块划分与接口定义  
·GUI原型设计（PyQt界面框架）  
·GitHub分支结构、命名约定制定  
该阶段输出：  
系统模块划分图：图示或表格形式，明确模块边界  
模块接口定义文档：每个模块的主要方法说明、输入输出说明  
PyQt界面原型代码：主界面+项目详情+翻译页等原型界面(可跳转，假数据)  
GitHub仓库结构说明文档：分支命名规则、提交规范、协作方式说明  
分工：  
A:  
系统模块划分图绘制:明确各模块边界与调用关系  
接口规范文档撰写:定义各模块对外暴露的函数/接口、参数、返回值等  
主界面框架搭建:PyQt主窗口 + 菜单栏 + 页面跳转结构  
GitHub协作结构设计:分支命名、目录结构、协作规则文档  
整合设计说明文档  
预期产出物:  
main_window.py  
module_structure.png  
interface_spec.md  
README.md  
B:  
翻译界面原型:段落翻译输入区（源文/译文）、跳段按钮、保存草稿  
术语提示逻辑:实时匹配术语并在界面中标记提示  
术语库管理界面:添加术语、修改、删除、导入导出、搜索术语等功能页  
预期产出物：  
translation_editor.py  
term_manager.py  
term_match.py  
术语匹配逻辑说明  
C：  
记忆库管理界面:展示翻译对表格，支持添加、编辑、删除、导入导出  
记忆匹配逻辑:编写匹配接口（支持模糊匹配、上下文可拓展）  
翻译界面中记忆区域设计:显示匹配结果（匹配度、历史译文等）  
预期产出物:  
tm_manager.py  
tm_match.py  
翻译记忆接口文档.md  
D:  
项目管理界面:创建项目、删除项目、修改项目状态  
文档管理界面:上传文档、删除文档、状态显示、跳转翻译界面  
导入导出逻辑结构：添加导入翻译文档 & 导出译文按钮及其界面逻辑框架（可假数据）  
预期产出物:  
project_manager.py  
document_manager.py  
import_export_stub.py  
文档导入导出流程说明.md  

注：优先完成接口定义文档和主界面框架搭建，再后面进行并行开发，最后进行合并协同，检查界面交互是否正常  

第三阶段：  
·编码与模块开发  
待开发功能：  
翻译项目管理模块  
文档管理模块  
翻译管理模块  
术语库管理模块  
翻译记忆库管理模块  
（前端和对应后端一起开发，避免产生错误）
数据库暂时想不到什么好的办法来同步  

第四阶段：测试与集成  
目标：  
·编写并运行测试用例  
·整合所有模块，修复Bug  

## 项目结构说明
docs/ :项目所有设计类文档，包括需求分析、用例图、ER图、调研报告  
src/ :主程序代码主目录  
——dao/ :数据库操作相关文件  
————__init__.py :空，仅作为识别软件包的标识  
————document_dao.py :文档管理相关数据库操作  
————project_dao.py :翻译项目管理模块  
——data/ :数据库  
——pages/ :各种页面  
————__init__.py :同上  
————document_page.py :翻译文档管理页面  
————project_page.py :翻译项目管理页面  
————term_page.py :术语库管理页面  
————tm_page.py :翻译记忆库管理页面  
————translation_page.py :翻译编辑页面  
data/ :项目运行所需的初始数据或演示项目  
tests/ :用于跑自动化测试  
README.md :项目入口说明，展示功能  
requirements.txt :安装依赖