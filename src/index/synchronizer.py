# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois
import json
from pathlib import Path
from hashlib import sha256

from src.utils import PathFinder
from src.operators import BM25Op, VectorOp
from src.lib import FileState, ProjectState, RAGState, DocSrc


class Synchronizer:
    def __init__(self,
        path_finder: PathFinder,
        document_sources: dict[str, DocSrc],
        state_path: Path,
        operator: BM25Op | VectorOp | None = None
    ) -> None:
        self.path_finder: PathFinder = path_finder
        self.operator: BM25Op | VectorOp | None = operator
        self.docsrc_store: dict[str, DocSrc] = document_sources
        self.state_path: Path = state_path

        self.rag_state: RAGState = RAGState(rag_states=[])
        self.load_rag_state()

        self.py_files_to_process: dict[str, list[Path]] = {}
        self.md_files_to_process: dict[str, list[Path]] = {}
        self.txt_files_to_process: dict[str, list[Path]] = {}
        self.remove_from_docsrc: list[Path] = []

    def load_rag_state(self) -> None:
        """load current rag state or creat a new empty rag state when first use"""

        if self.state_path.exists():
            with open(self.state_path, "r", encoding="utf-8") as f:
                raw_state = json.load(f)
            self.rag_state = RAGState(**raw_state)

    def export_rag_state(self) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_path, "w", encoding="utf-8") as f:
            f.write(self.rag_state.model_dump_json(indent=4))

    def check_projects(self) -> None:
        current_projects_set: set[Path] = set()
        rag_project_set: set[Path] = set()

        # recovers projects currently in data/raw folder
        if not self.path_finder.raw_dir.exists():
            raise FileNotFoundError()  # TO BE HANDLED
        for project in self.path_finder.raw_dir.iterdir():
            if project.is_dir() and not project.name.startswith("."):
                current_projects_set.add(project)

        # recovers projects registered in current RAG state
        for project in self.rag_state.rag_states:
            rag_project_set.add(project.project)

        proj_to_remove: set[Path] = rag_project_set.difference(current_projects_set)
        proj_to_add: set[Path] = current_projects_set.difference(rag_project_set)
        proj_to_scan: set[Path] = current_projects_set.intersection(rag_project_set)

        for deleted_project in proj_to_remove:
            self._remove_project(deleted_project)
        for new_project in proj_to_add:
            self._add_project(new_project)
        for project in proj_to_scan:
            self._sync_project(project)

        self.export_rag_state()

    def _add_project(self, project_to_add: Path) -> None:
        self.py_files_to_process[project_to_add.name] = []
        self.md_files_to_process[project_to_add.name] = []
        self.txt_files_to_process[project_to_add.name] = []
        filestate_list: list[FileState] = []

        py_f, md_f, txt_f = self._recover_project_files(project_to_add)
        self.py_files_to_process[project_to_add.name].extend(py_f)
        self.md_files_to_process[project_to_add.name].extend(md_f)
        self.txt_files_to_process[project_to_add.name].extend(txt_f)

        all_files: list[Path] = py_f + md_f + txt_f
        for file_path in all_files:
            self._add_file(project_to_add, file_path)

    def _remove_project(self, project_to_remove: Path) -> None:
        proj: ProjectState = next((p for p in self.rag_state.rag_states if p.project == project_to_remove))

        files_to_remove = [file.file_path for file in proj.files]
        self._remove_files(files_to_remove)
        self.rag_state.rag_states = [
            p for p in self.rag_state.rag_states
            if p.project != project_to_remove
        ]

    def _sync_project(self, project_to_sync: Path) -> None:
        rag_project: ProjectState | None = self.rag_state.get_project_state(project_to_sync)
        if not rag_project:
            return
        rag_project_files: dict[Path, str] = {f.file_path: f.content_hash for f in rag_project.files}
        py_f, md_f, txt_f = self._recover_project_files(project_to_sync)

        rag_files_set: set[Path] = set(rag_project_files.keys())
        current_files_set: set[Path] = set(py_f + md_f + txt_f)

        file_to_remove: set[Path] = rag_files_set.difference(current_files_set)
        file_to_add: set[Path] = current_files_set.difference(rag_files_set)
        file_to_scan: set[Path] = current_files_set.intersection(rag_files_set)

        if file_to_remove:
            self._remove_files(list(file_to_remove))

        for new_file in file_to_add:
            self._add_file(project_to_sync, new_file)

        files_to_reprocess: list[Path] = []
        for file in file_to_scan:
            with open(file, "r", encoding="utf-8") as f:
                current_f = f.read()
            current_file_hash = sha256(current_f.encode("utf-8")).hexdigest()

            rag_file_hash = self.rag_state.get_file_state(project_to_sync.name, file).content_hash
            if rag_file_hash != current_file_hash:
                files_to_reprocess.append(file)

        if files_to_reprocess:
            self._remove_files(files_to_reprocess)
            for file in files_to_reprocess:
                self._add_file(project_to_sync, file)

    def _add_file(self, project: Path, file: Path) -> None:
        if project.name not in self.py_files_to_process:
            self.py_files_to_process[project.name] = []
        if project.name not in self.md_files_to_process:
            self.md_files_to_process[project.name] = []
        match file.suffix.lower():
            case ".py": self.py_files_to_process[project.name].append(file)
            case ".md": self.md_files_to_process[project.name].append(file)
            case ".txt": self.txt_files_to_process[project.name].append(file)

        # RAG State update
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
        f_hash = sha256(content.encode("utf-8")).hexdigest()
        file_state = FileState(
            file_path=file,
            content_hash=f_hash
        )
        self.rag_state.add_file_state(project, file_state)

    def _remove_files(self, files: list[Path]) -> None:
        if not files:
            return
        for file in files:
            self.remove_from_docsrc.append(file)
        self._update_std()
        if self.operator is not None:
            self.operator.delete(files)
        self.rag_state.remove_file_states(files)

    @staticmethod
    def _recover_project_files(project_path: Path) -> tuple[list[Path], list[Path], list[Path]]:
        py_files: list[Path] = []
        md_files: list[Path] = []
        txt_files: list[Path] = []
        for file_path in project_path.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith("."):
                ext = file_path.suffix.lower()
                if ext == ".py":
                    py_files.append(file_path)
                elif ext == ".md":
                    md_files.append(file_path)
                elif ext == ".txt":
                    txt_files.append(file_path)
        return py_files, md_files, txt_files

    def _update_std(self) -> None:
        paths_to_remove = {Path(p) for p in self.remove_from_docsrc}

        remaining_docs = {
            doc_id: doc for doc_id, doc in self.docsrc_store.items()
            if Path(doc.file_path) not in paths_to_remove
        }

        self.docsrc_store.clear()
        self.docsrc_store.update(remaining_docs)
        self.remove_from_docsrc.clear()
