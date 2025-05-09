import os
import json
import shutil
from datetime import datetime


class Project:
    def __init__(self, name, description, source_language, target_languages,
                 file_path, use_memory,memory_path, use_termbase,termbase_path):
        self.name = name
        self.description = description
        self.source_language = source_language
        self.target_languages = target_languages
        self.file_path = file_path  # 用户上传的原始文件路径
        self.use_memory = use_memory
        self.memory_path = memory_path
        self.use_termbase = use_termbase
        self.termbase_path = termbase_path
        self.project_dir = os.path.join("projects", self.name)
        self.meta_file = os.path.join(self.project_dir, "meta.json")

    def create(self):
        try:
            # 创建项目目录
            os.makedirs(self.project_dir, exist_ok=True)


            # 复制文件到项目目录的source_files子目录
            source_files_dir = os.path.join(self.project_dir, "source_files")
            os.makedirs(source_files_dir, exist_ok=True)
            #翻译文件路径
            target_files_dir = os.path.join(self.project_dir, "target_files")
            os.makedirs(target_files_dir, exist_ok=True)

            if self.file_path and os.path.isfile(self.file_path):
                filename = os.path.basename(self.file_path)
                dest_path = os.path.join(source_files_dir, filename)
                shutil.copy(self.file_path, dest_path)
                stored_file_path = dest_path  # 存储复制后的路径
            else:
                stored_file_path = ""

            # 创建元数据
            info = {
                "name": self.name,
                "description": self.description,
                "source_language": self.source_language,
                "target_languages": self.target_languages,
                "original_file": self.file_path,
                "stored_source_file": stored_file_path,
                "target_files_dir": target_files_dir,
                "use_memory": self.use_memory,
                "memory_path": self.memory_path,
                "use_termbase": self.use_termbase,
                "termbase_path": self.termbase_path,
                "created_at": datetime.now().isoformat()
            }

            # 保存元数据
            with open(self.meta_file, "w", encoding="utf-8") as f:
                json.dump(info, f, ensure_ascii=False, indent=4)

            return True
        except Exception as e:
            print(f"创建项目时出错: {str(e)}")
            return False

    @staticmethod
    def open_all_projects():
        projects_root = "projects"
        projects = []

        if not os.path.exists(projects_root):
            return projects  # 返回空列表

        for project_name in os.listdir(projects_root):
            project_path = os.path.join(projects_root, project_name)
            meta_file = os.path.join(project_path, "meta.json")

            if os.path.isdir(project_path) and os.path.isfile(meta_file):
                try:
                    with open(meta_file, "r", encoding="utf-8") as f:
                        info = json.load(f)

                    project = Project(
                        name=info["name"],
                        description=info["description"],
                        source_language=info["source_language"],
                        target_languages=info["target_languages"],
                        file_path=info.get("original_file", ""),
                        use_memory=info.get("use_memory", False),
                        memory_path=info.get("memory_path", ""),
                        use_termbase=info.get("use_termbase", False),
                        termbase_path=info.get("termbase_path", "")
                    )
                    projects.append(project)
                except Exception as e:
                    print(f"读取项目 {project_name} 时出错: {str(e)}")

        return projects

    # 其余方法保持不变...
