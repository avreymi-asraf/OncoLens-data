"""Models under evaluation: anything with `generate(prompts) -> completions`.

`Fixed` proves the wiring without a GPU; `HFModel` is the real backend (Colab/GPU). `load_model`
turns the CLI string into one of them.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol


class Model(Protocol):
    @property
    def name(self) -> str: ...

    def generate(self, prompts: Sequence[str]) -> list[str]:
        """One completion per prompt, same order. Completions contain only newly generated text."""
        ...


@dataclass(frozen=True)
class Fixed:
    """Always answers the same string: a deterministic policy for checking the pipeline end to end."""

    answer: str

    @property
    def name(self) -> str:
        return f"fixed:{self.answer}"

    def generate(self, prompts: Sequence[str]) -> list[str]:
        return [self.answer for _ in prompts]


class HFModel:
    """Greedy Hugging Face causal LM. Needs the `gpu` extra (torch, transformers).

    Instruction-tuned models get their chat template applied; base models see the raw prompt.
    Left padding is required so every row of a batch ends at the generation position.
    """

    def __init__(self, model_id: str, batch_size: int = 8, max_new_tokens: int = 8):
        # Optional `gpu` extra: imported lazily, and unresolved when pyright runs on the light core.
        import torch  # pyright: ignore[reportMissingImports]
        from transformers import (  # pyright: ignore[reportMissingImports]
            AutoModelForCausalLM,
            AutoTokenizer,
        )

        self._name = model_id
        self._batch_size = batch_size
        self._max_new_tokens = max_new_tokens
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        if self._device == "cpu":
            dtype = torch.float32
        else:
            dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
        self._tokenizer = AutoTokenizer.from_pretrained(model_id, padding_side="left")
        if self._tokenizer.pad_token is None:  # many causal LMs ship without one
            self._tokenizer.pad_token = self._tokenizer.eos_token
        self._model = AutoModelForCausalLM.from_pretrained(model_id, dtype=dtype).to(self._device)
        self._model.eval()

    def generate(self, prompts: Sequence[str]) -> list[str]:
        import torch  # pyright: ignore[reportMissingImports]

        completions: list[str] = []
        for start in range(0, len(prompts), self._batch_size):
            texts = [self._render(p) for p in prompts[start : start + self._batch_size]]
            # The chat template already inserts special tokens such as BOS.
            batch = self._tokenizer(
                texts,
                return_tensors="pt",
                padding=True,
                add_special_tokens=not self._has_chat_template,
            ).to(self._device)
            with torch.inference_mode():
                output = self._model.generate(
                    **batch,
                    do_sample=False,
                    max_new_tokens=self._max_new_tokens,
                    pad_token_id=self._tokenizer.pad_token_id,
                )
            new_tokens = output[:, batch["input_ids"].shape[1] :]
            completions += self._tokenizer.batch_decode(new_tokens, skip_special_tokens=True)
        return completions

    @property
    def name(self) -> str:
        return self._name

    @property
    def _has_chat_template(self) -> bool:
        return bool(self._tokenizer.chat_template)

    def _render(self, prompt: str) -> str:
        if not self._has_chat_template:
            return prompt
        return self._tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}], tokenize=False, add_generation_prompt=True
        )


def load_model(spec: str) -> Model:
    """'fixed:A' -> Fixed('A'); anything else is a Hugging Face model id."""
    if spec.startswith("fixed:"):
        return Fixed(spec.removeprefix("fixed:"))
    return HFModel(spec)
