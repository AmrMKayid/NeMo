# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os

import pytorch_lightning as pl
from omegaconf import DictConfig, OmegaConf

from nemo.collections.nlp.models import TextNormalizationModel
from nemo.core.config import hydra_runner
from nemo.utils import logging
from nemo.utils.exp_manager import exp_manager


@hydra_runner(config_path="conf", config_name="text_normalization_config")
def main(cfg: DictConfig) -> None:
    logging.info(f'Config: {cfg.pretty()}')
    trainer = pl.Trainer(**cfg.trainer)
    exp_dir = exp_manager(trainer, cfg.get("exp_manager", None))

    if not cfg.pretrained_model:
        logging.info(f'Config: {OmegaConf.to_yaml(cfg)}')
        model = TextNormalizationModel(cfg.model, trainer=trainer)
    else:
        logging.info(f'Loading pretrained model {cfg.pretrained_model}')
        model = TextNormalizationModel.from_pretrained(cfg.pretrained_model)
        if cfg.do_training:
            model.setup_training_data(train_data_config=cfg.model.train_ds)
            model.setup_validation_data(val_data_config=cfg.model.validation_ds)

    if cfg.do_training:
        trainer.fit(model)

    if hasattr(cfg.model, 'test_ds') and cfg.model.test_ds.file is not None:
        trainer.test(model)


if __name__ == '__main__':
    main()
