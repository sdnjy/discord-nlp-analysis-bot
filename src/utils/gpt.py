import numpy as np
import pandas as pd
import logging
from langchain import PromptTemplate, LLMChain
from langchain.llms import GPT4All
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler

from langchain.llms import GPT4All
from functools import partial
from typing import Any, List
from langchain.callbacks.manager import AsyncCallbackManagerForLLMRun
from langchain.llms.utils import enforce_stop_tokens

# https://github.com/langchain-ai/langchain/issues/5210#issuecomment-1646581246
class AGPT4All(GPT4All):
    async def _acall(self, prompt: str, stop: List[str] | None = None, run_manager: AsyncCallbackManagerForLLMRun | None = None, **kwargs: Any) -> str:
        text_callback = None
        if run_manager:
            text_callback = partial(run_manager.on_llm_new_token, verbose=self.verbose)
        text = ""
        params = {**self._default_params(), **kwargs}
        for token in self.client.generate(prompt,streaming = True, **params):
            if text_callback:
                await text_callback(token)
            text += token
        if stop is not None:
            text = enforce_stop_tokens(text, stop)
        return text


async def run_prediction(llm_chain: LLMChain, text: str, prompt_ask: str):
    input_dict = {"text": text, "prompt_ask": prompt_ask}
    return await llm_chain.arun(input_dict)

def prepare_model(llm: AGPT4All):
    prompt_template = """
    I will give you an internet discussion as a text.
    Text: \"{text}\"
    You are a helpful, respectful and honest assistant. {prompt_ask}
    """    
    prompt = PromptTemplate(template=prompt_template, input_variables=["text", "prompt_ask"])
    
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    return llm_chain

def launch_model(model_local_path: str):
    # Callbacks support token-wise streaming
    callbacks = [AsyncIteratorCallbackHandler()]
    
    # Verbose is required to pass to the callback manager
    llm = AGPT4All(
        model=model_local_path,
        callbacks=callbacks,
        n_threads=8,
        n_predict=100,
        max_tokens=500,
        verbose=True
    )
    return llm

async def gpt_pipeline_predict(model_local_path: str, prompt_ask: str, text: str):
    llm = launch_model(model_local_path)
    llm_chain = prepare_model(llm)
    return await run_prediction(llm_chain, text, prompt_ask)