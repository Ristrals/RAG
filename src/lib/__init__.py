# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

"""Public exports for shared data models, enums, and interface payloads."""

from src.lib.data_lib import (
    TextColors as Tc,
    CodeNode,
    HeaderNode,
    Chunk,
    ResearchType as RsrchType,
    ErrorType as ErrType,
    StopWords as StopWord
)
from src.lib.mandatory_contracts import (
    MinimalSource as MinSrc,
    UnansweredQuestion as UnansQ,
    AnsweredQuestion as AnsQ,
    RagDataset,
    MinimalSearchResults as MinSrchRes,
    MinimalAnswer as MinAns,
    StudentSearchResults as StuSrchRes,
    StudentSearchResultsAndAnswer as StuSrchResAns
)
from src.lib.contracts import (
    DocumentSource as DocSrc,
    GroundTruthQuestion as GrndTruthQ,
    GroundTruthDataset as GrndTruthDs,
    FileState,
    ProjectState,
    RAGState,
    InterfaceIndex,
    InterfaceQuery,
    InterfaceEvaluate,
    InterfaceDatasetSearch,
    InterfaceDatasetAnswer
)

__all__ = [
    "Tc", "CodeNode", "HeaderNode", "Chunk", "RsrchType", "ErrType", "StopWord",
    "DocSrc", "GrndTruthQ", "GrndTruthDs", "FileState", "ProjectState", "RAGState",
    "InterfaceIndex", "InterfaceQuery", "InterfaceEvaluate", "InterfaceDatasetSearch", "InterfaceDatasetAnswer",
    "MinSrc",
    "UnansQ",
    "AnsQ",
    "RagDataset",
    "MinSrchRes",
    "MinAns",
    "StuSrchRes",
    "StuSrchResAns",
]
