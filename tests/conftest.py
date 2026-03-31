import random

import pytest
from syrupy.extensions.json import JSONSnapshotExtension

from tests.factories.base import Factory


@pytest.fixture(autouse=True)
def reset_all_factory_sequences() -> None:
    Factory._reset_all_sequences()


@pytest.fixture(autouse=True)
def set_random_seed():
    random.seed(3)


@pytest.fixture
def snapshot_json(snapshot):
    return snapshot.use_extension(JSONSnapshotExtension)
