# RAGAgainstTheMachine - 42Luxembourg 2026 - kmalfois

import torch
import json
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM, PreTrainedTokenizerFast

from src.lib import (
    MinSrc,
    MinSrchRes,
    StuSrchRes,
    MinAns,
    StuSrchResAns,
    RsrchType
)
from src.utils import PathFinder
from src.retrieval.retriever import Retriever


class Oracle:
    def __init__(
        self, dataset_path: str,
        save_directory: str,
        mode: RsrchType,
        k: int = 10,
        model_name: str ="Qwen/Qwen3-0.6B") -> None:
        self.mode: RsrchType = mode
        self.k: int = k
        self.path_finder: PathFinder = PathFinder(save_directory=Path(save_directory), dataset=Path(dataset_path))
        self.tokenizer: PreTrainedTokenizerFast = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
            device_map="auto"
        )
        self.doc_store: dict[str, dict]  = {}
        self._load_doc_store()
        self.retriever = Retriever(self.path_finder, k, self.doc_store, self.mode)
        self.research_results: StuSrchRes = self.retriever.research_set()

    def answer(self, minimal_srch_res: MinSrchRes) -> MinAns:
        snippets: list[str] = []

        for minimal_source in minimal_srch_res.retrieved_sources:
            snippets.append(self._recover_snippets(minimal_source))
        combined_snippets: str = "\n\n".join(snippets)

        model_prompt_role: str = (
            "You are a precise vLLM code analysis assistant."
            "Answer the question using ONLY the provided code/doc snippets."
            "Keep the output concise, direct, and factual.")

        model_prompt_context: str = (f"""
            QUESTION:
            {minimal_srch_res.question}

            CODE CONTEXT:
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
                generated_ids = self.model.generate(
                    **model_inputs,
                    max_new_tokens=512,
                    temperature=0.0,  # Deterministic output
                    do_sample=False
                )

            output_ids = generated_ids[0][len(model_inputs.input_ids[0]):]
            answer_text = self.tokenizer.decode(output_ids, skip_special_tokens=True).strip()
        except Exception as e:
            answer_text = f"[Error generating answer: {e}]"  # TO BE MANAGED

        return MinAns(
            **minimal_srch_res.model_dump(),
            answer=answer_text
        )

    def answer_set(self, student_research_result: StuSrchRes) -> StuSrchResAns:
        answer_list: list[MinAns] = []

        for minimal_srch_res in student_research_result.search_results:
            answer_list.append(self.answer(minimal_srch_res))

        return StuSrchResAns(
            search_results=answer_list,
            k=self.k
        )

    @staticmethod
    def _recover_snippets(minimal_source: MinSrc) -> str:
        file_path = Path(minimal_source.file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            file_text = f.read()
        return file_text[minimal_source.first_character_index:minimal_source.last_character_index]

    def _recover_model_answer(self) -> None:
        pass

    def _load_doc_store(self) -> None:
        with open(self.path_finder.processed_dir / "std_index.json", "r", encoding="utf-8") as f:
            raw_docs = json.load(f)
            self.doc_store = {doc["id"]: doc for doc in raw_docs}