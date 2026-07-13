import logging
from dataclasses import dataclass, field
from logging import Logger
from typing import Any, Self, TypeAlias

import numpy as np
from pystac import Collection, Item
from pystac_client import Client

from ....utils._cli import get_counter_message
from ....utils.decorator import retry
from ....utils.time import time_to_string
from ._cache import get_default_properties_dict
from .collections import get_candidate_collections
from .core import get_catalog, get_collections, get_properties, get_queryables
from .filter import create_filter
from .items import get_sorted_items, get_unique_items, items_to_product_dataframe
from .params import Params

South: TypeAlias = float
West: TypeAlias = float
North: TypeAlias = float
East: TypeAlias = float

log = logging.getLogger("ecdownload")


def get_collection_name(collection: Collection | str) -> str:
    return collection.id if isinstance(collection, Collection) else collection


@dataclass
class Searcher:
    params: Params | None = field(default=None)
    _catalog: Client | None = field(default=None, init=False, repr=False)
    _collections: list[Collection] | None = field(default=None, init=False, repr=False)
    _queryables_dict: dict[str, dict[str, Any]] = field(
        default_factory=dict, init=False, repr=False
    )
    _properties_dict: dict[str, dict[str, Any]] = field(
        default_factory=get_default_properties_dict, init=False, repr=False
    )

    def get_datetime(self: Self) -> tuple[str | None, str | None] | None:
        if not isinstance(self.params, Params):
            return None
        params = self.params

        if params.start_time is None and params.end_time is None:
            return None

        format: str = "%Y-%m-%dT%H:%M:%SZ"

        return (
            None if params.start_time is None else time_to_string(params.start_time, format=format),
            None if params.end_time is None else time_to_string(params.end_time, format=format),
        )

    def get_filter(self: Self, properties: dict[str, Any]) -> str | None:
        if not isinstance(self.params, Params):
            return None
        return create_filter(properties=properties, params=self.params)

    def get_catalog(self) -> Client:
        if isinstance(self._catalog, Client):
            return self._catalog
        self._catalog = get_catalog()
        return self._catalog

    def set_catalog(self, catalog: Client) -> None:
        if isinstance(catalog, Client):
            self._catalog = catalog
        else:
            raise TypeError(f"Invalid type '{type(catalog).__name__}'; expected 'Client'")

    def get_collections(self) -> list[Collection]:
        if isinstance(self._collections, list) and all(
            isinstance(c, Collection) for c in self._collections
        ):
            return self._collections
        self._collections = get_collections(self.get_catalog())
        return self._collections

    def set_collections(self, collections: list[Collection]) -> None:
        if isinstance(collections, list) and all(isinstance(c, Collection) for c in collections):
            self._collections = collections
        elif isinstance(collections, list):
            subtypes = " | ".join([type(c).__name__ for c in collections])
            raise TypeError(f"Invalid type 'list[{subtypes}]'; expected 'list[Collection]'")
        else:
            raise TypeError(
                f"Invalid type '{type(collections).__name__}'; expected 'list[Collection]'"
            )

    def get_queryables(self, collection: Collection | str) -> dict[str, Any]:
        collection = get_collection_name(collection)
        if isinstance(self._queryables_dict, dict) and collection in self._queryables_dict:
            return self._queryables_dict[collection]
        self._queryables_dict[collection] = get_queryables(self.get_catalog(), collection)
        return self._queryables_dict[collection]

    def set_queryables(self, collection: Collection | str, queryables: dict[str, Any]) -> None:
        collection = get_collection_name(collection)
        self._queryables_dict[collection] = queryables

    def get_properties(self, collection: Collection | str) -> dict[str, Any]:
        collection = get_collection_name(collection)
        if isinstance(self._properties_dict, dict) and collection in self._properties_dict:
            return self._properties_dict[collection]
        self._properties_dict[collection] = get_properties(self.get_queryables(collection))
        return self._properties_dict[collection]

    def set_properties(self, collection: Collection | str, properties: dict[str, Any]) -> None:
        collection = get_collection_name(collection)
        self._properties_dict[collection] = properties

    def clear_cache(self) -> None:
        self._catalog = None
        self._collections = None
        self._queryables_dict = dict()
        self._properties_dict = dict()

    def _search_items(
        self,
        collection: Collection | str,
        params: Params | None = None,
        logger: Logger | None = None,
        total_count: int | None = None,
        counter: int | None = None,
    ) -> list[Item]:
        if isinstance(params, Params):
            self.params = params

        if not isinstance(self.params, Params):
            return []

        params = self.params

        collection = get_collection_name(collection)

        count_msg, _ = get_counter_message(counter=counter, total_count=total_count)

        @retry(n=5, backoff=1.5, jitter=0.2, logger=log)
        def _search() -> list[Item]:
            catalog = self.get_catalog()
            properties = self.get_properties(collection)
            filt = self.get_filter(properties)
            kwargs = dict(
                collections=[collection],
                filter=filt,
                limit=params.max_items,
                datetime=self.get_datetime(),
                filter_lang="cql2-text",
                method="POST",
            )

            if logger:
                logger.info(f"*{count_msg} Search request: {kwargs}")
                logger.debug(f" {count_msg} {self}")

            search = catalog.search(
                collections=[collection],
                filter=filt,
                limit=params.max_items,
                datetime=self.get_datetime(),
                filter_lang="cql2-text",
                method="POST",
            )

            return get_sorted_items(get_unique_items(list(search.items())))

        items = _search()
        items = get_unique_items(items)
        items = get_sorted_items(items)

        if logger:
            logger.info(f" {count_msg} Search results: {len(items)}")

        return items

    def search(
        self,
        params: list[Params] | Params | None = None,
        user_collections: list[Collection] | list[str] = [
            "EarthCAREL0L1Products_MAAP",
            "EarthCAREL2Products_MAAP",
            "JAXAL2Products_MAAP",
            "EarthCAREAuxiliary_MAAP",
            "EarthCAREL1InstChecked_MAAP",
            "EarthCAREL2InstChecked_MAAP",
            "JAXAL2InstChecked_MAAP",
            "EarthCAREL1Validated_MAAP",
            "EarthCAREL2Validated_MAAP",
            "JAXAL2Validated_MAAP",
            "EarthCAREXMETL1DProducts10_MAAP",
            "EarthCAREOrbitData_MAAP",
        ],
        logger: Logger | None = None,
    ) -> list[Item]:
        if params is None and isinstance(self.params, Params):
            params = [self.params]
        elif params is None:
            params = []
        elif isinstance(params, Params):
            params = [params]

        total_count = len(params)

        items: list[Item] = []
        for i, prms in enumerate(params):
            candidate_collections = get_candidate_collections(user_collections, prms.product_type)
            for cand_coll in candidate_collections:
                new_items = self._search_items(
                    cand_coll,
                    prms,
                    logger=logger,
                    total_count=total_count,
                    counter=i + 1,
                )
                items.extend(new_items)
                if len(new_items) > 0:
                    break

        # Filter unique items
        items_uniq = get_unique_items(items)

        # Sort items
        items_uniq_sort = get_sorted_items(items_uniq)

        # Fitler latest items
        df = items_to_product_dataframe(items_uniq_sort)
        df["___item___"] = np.array(items_uniq_sort)
        df_late = df.filter_latest()
        items_uniq_sort_late = df_late.pop("___item___").tolist()

        if logger and len(items_uniq_sort_late) > 0:
            logger.debug(f"Total unfiltered results: {len(items)}")
            logger.debug(f"Unique results: {len(items_uniq_sort)}")
            logger.debug(f"Latest results: {len(items_uniq_sort_late)}")
            logger.info(
                f"Total results (filtered to latest versions per file): {len(items_uniq_sort_late)}"
            )

        return items_uniq_sort_late
