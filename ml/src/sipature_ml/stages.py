"""Stable names and order for reproducible pipeline stages."""

from enum import Enum


class Stage(str, Enum):
    INVENTORY = "inventory"
    CLEAN = "clean"
    RESOLVE_ENTITIES = "resolve-entities"
    SAMPLE_ANNOTATIONS = "sample-annotations"
    SPLIT = "split"
    TRAIN_KEYWORD = "train-keyword"
    TRAIN_TFIDF = "train-tfidf"
    TRAIN_INDOBERT = "train-indobert"
    CALIBRATE = "calibrate"
    EVALUATE = "evaluate"
    INFER = "infer"
    AGGREGATE = "aggregate"
    PRIORITIZE = "prioritize"
    EXPORT_APP = "export-app"


PIPELINE_ORDER = tuple(Stage)
