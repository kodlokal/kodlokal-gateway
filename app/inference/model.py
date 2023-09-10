import time, uuid, os
from ctransformers import AutoModelForCausalLM
from app.kodlokal_app import app
from app.log import log

class Model():
  """
  The model class.

  :param category: the category of the model, one of "TEXT", "CODE"
  :category version: str
  """

  def __init__(self, category):
      self.category = category
      if self.exist():
        self.load()
        log.info(f"Started {self.category} model for {self.name()}")
      else:
        log.warning(f"{self.category} model does not exist in config")

  def __str__(self):
      return f'Model category: {self.category}'

  def config(self, key):
      return app.config[f"{self.category}_{key}"]

  def name(self):
      return f"{app.config['MODELS_FOLDER']}{self.config('MODEL')}"

  def exist(self):
    return f"{self.category}_MODEL" in app.config

  def load(self):
      if os.path.exists(self.name()):
        self.model = AutoModelForCausalLM.from_pretrained(self.name(),
                                                          model_type=self.config('MODEL_TYPE'),
                                                          gpu_layers=self.config('GPU_LAYERS'))
      else:
        self.model = None

  def suggest(self, prompt):
    if not self.model is None:
      return self.model(prompt,
                        temperature=self.config('TEMPERATURE'),
                        max_new_tokens=self.config('MAX_NEW_TOKENS'))
    else:
      None

  def prompt_ok(self, prompt):
    return prompt is not None and len(prompt) >= 3

  def present(self, result, prompt):
    response_data = {
      "choices": [
          {
              "finish_reason": "length",
              "index": 0,
              "logprobs": None,
              "text": result
          }
      ],
      "created": int(time.time()),
      "id": str(uuid.uuid4()),
      "model": self.name(),
      "object": "text_completion",
      "usage": {
          "completion_tokens": len(result),
          "prompt_tokens": len(prompt),
          "total_tokens": len(result) + len(prompt)
      }
    }
    return response_data
