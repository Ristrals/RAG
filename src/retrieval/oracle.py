# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

import torch
from functools import lru_cache
from tqdm import tqdm
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM, PreTrainedTokenizerFast

from src.lib import (
    MinSrc,
    MinSrchRes,
    StuSrchRes,
    MinAns,
    StuSrchResAns,
    DocSrc,
    Tc,
    ErrType
)
from src.utils import PathFinder
from src.retrieval import OracleError


class Oracle:
    """Generate answers from retrieved sources using a causal language model.

    Attributes:
        path_finder: Path helper exposing dataset and result locations.
        doc_store: Document source map keyed by document id.
        k: Number of retrieval results expected per question.
        tokenizer: Tokenizer used to format and encode prompts.
        model: Causal language model used for answer generation.
    """

    def __init__(
        self, path_finder: PathFinder,
        doc_store: dict[str, DocSrc],
        k: int = 10,
        model_name: str = "Qwen/Qwen3-0.6B"
    ) -> None:
        """Initialize tokenizer and model for answer generation.

        Args:
            path_finder: Path helper exposing required file locations.
            doc_store: In-memory document source map.
            k: Number of sources associated with each query.
            model_name: Pretrained model identifier.

        """

        self.path_finder: PathFinder = path_finder
        self.doc_store: dict[str, DocSrc] = doc_store
        self.k: int = k
        self.tokenizer: PreTrainedTokenizerFast = AutoTokenizer.from_pretrained(model_name)  # type: ignore[assignment]
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
            device_map="auto"
        )

    def answer(self, minimal_srch_res: MinSrchRes) -> MinAns:
        """Generate an answer for one retrieved-question payload.

        Args:
            minimal_srch_res: Search result containing question and sources.

        Returns:
            Answer payload with generated text.
        """
        snippets: list[str] = []

        for minimal_source in minimal_srch_res.retrieved_sources:
            snippets.append(self._recover_snippets(minimal_source))
        combined_snippets: str = "\n\n".join(snippets)

        model_prompt_role: str = (
            "You are a precise vLLM code analysis assistant."
            "Answer the question using ONLY the provided code/doc snippets."
            "Keep the output concise and factual.")

        model_prompt_context: str = (f"""
            QUESTION:
            {minimal_srch_res.question}

            CODE CONTEXT FROM MOST RELEVANT TO LESS RELEVANT:
            {combined_snippets}

            ANSWER:""").strip()

        messages = [
            {"role": "system", "content": model_prompt_role},
            {"role": "user", "content": model_prompt_context}
        ]

        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False
        )

        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
        try:
            with torch.no_grad():
                generated_ids = self.model.generate(  # type: ignore[misc]
                    **model_inputs,
                    max_new_tokens=512,
                    temperature=0.0,  # Deterministic output
                    do_sample=False
                )

            output_ids = generated_ids[0][len(model_inputs.input_ids[0]):]
            decoded = self.tokenizer.decode(output_ids, skip_special_tokens=True)
            answer_text = decoded.strip() if isinstance(decoded, str) else decoded[0].strip()
        except Exception as e:
            raise OracleError(ErrType.CRIT, e)

        return MinAns(
            **minimal_srch_res.model_dump(),
            answer=answer_text
        )

    def answer_set(self) -> StuSrchResAns:
        """Generate answers for every question in student results.

        Returns:
            Dataset answer payload for all questions.
        """
        answer_list: list[MinAns] = []
        result = self._load_student_result()

        for minimal_srch_res in tqdm(
            result.search_results,
            desc=f"[{Tc.mag}[Processing dataset answers]{Tc.clr}]",
            unit="query",
            colour="magenta"
        ):
            answer_list.append(self.answer(minimal_srch_res))
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

        return StuSrchResAns(
            search_results=answer_list,
            k=self.k
        )

    @staticmethod
    def _recover_snippets(minimal_source: MinSrc) -> str:
        """Recover a source snippet from indexed character boundaries.

        Args:
            minimal_source: Minimal source metadata with file path and range.

        Returns:
            Sliced text snippet from the referenced file.
        """
        return Oracle._cached_file_slice(
            str(minimal_source.file_path),
            minimal_source.first_character_index,
            minimal_source.last_character_index
        )

    @staticmethod
    @lru_cache(maxsize=1024)
    def _cached_file_slice(file_path: str, start: int, end: int) -> str:
        """Cache file slicing to reduce repeated disk I/O.

        Args:
            file_path: Source file path.
            start: Inclusive start character offset.
            end: Exclusive end character offset.

        Returns:
            Extracted text segment.
        """
        path = Path(file_path)
        with open(path, "r", encoding="utf-8") as f:
            file_text = f.read()
        return file_text[start:end]

    def _load_student_result(self) -> StuSrchRes:
        """Load and validate student search results from disk.

        Returns:
            Parsed student search results payload.
        """
        try:
            assert isinstance(self.path_finder.student_search_results_path, Path)
            with open(self.path_finder.student_search_results_path, "r", encoding="utf-8") as f:
                raw_result = f.read()
            result = StuSrchRes.model_validate_json(raw_result)
        except Exception as e:
            raise OracleError(ErrType.CRIT, e)
        return result
