from dataclasses import dataclass, field
from logging import Logger
from typing import Any, Self, TypeAlias

import numpy as np
import pandas as pd
from pystac import Collection, Item
from pystac_client import Client

from ....utils._cli import get_counter_message
from ....utils.decorator import retry
from ....utils.parse import get_file_info_from_str
from ....utils.time import time_to_str
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
    _logger: Logger | None = field(default=None, init=False, repr=False)

    def get_datetime(self: Self) -> tuple[str | None, str | None] | None:
        if not isinstance(self.params, Params):
            return None
        params = self.params

        if params.start_time is None and params.end_time is None:
            return None

        format: str = "%Y-%m-%dT%H:%M:%SZ"

        return (
            None if params.start_time is None else time_to_str(params.start_time, format=format),
            None if params.end_time is None else time_to_str(params.end_time, format=format),
        )

    def get_filter(self: Self, properties: dict[str, Any]) -> str | None:
        if not isinstance(self.params, Params):
            return None
        return create_filter(properties=properties, params=self.params)

    def get_catalog(self) -> Client:
        if isinstance(self._catalog, Client):
            return self._catalog

        @retry(n=5, backoff=1.5, jitter=0.2)
        def _get_catalog() -> Client:
            return get_catalog(self._logger)

        self._catalog = _get_catalog()
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
        self._collections = get_collections(self.get_catalog(), logger=self._logger)
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

        @retry(n=5, backoff=1.5, jitter=0.2)
        def _get_queryables() -> dict[str, Any]:
            return get_queryables(self.get_catalog(), collection, logger=self._logger)

        self._queryables_dict[collection] = _get_queryables()
        return self._queryables_dict[collection]

    def set_queryables(self, collection: Collection | str, queryables: dict[str, Any]) -> None:
        collection = get_collection_name(collection)
        self._queryables_dict[collection] = queryables

    def get_properties(self, collection: Collection | str) -> dict[str, Any]:
        collection = get_collection_name(collection)
        if isinstance(self._properties_dict, dict) and collection in self._properties_dict:
            return self._properties_dict[collection]
        self._properties_dict[collection] = get_properties(
            self.get_queryables(collection), logger=self._logger
        )
        return self._properties_dict[collection]

    def set_properties(self, collection: Collection | str, properties: dict[str, Any]) -> None:
        collection = get_collection_name(collection)
        self._properties_dict[collection] = properties

    def clear_cache(self) -> None:
        self._catalog = None
        self._collections = None
        self._queryables_dict = dict()
        self._properties_dict = dict()

    def search_items(
        self,
        collection: Collection | str,
        params: Params | None = None,
        logger: Logger | None = None,
        total_count: int | None = None,
        counter: int | None = None,
    ) -> list[Item]:
        if isinstance(params, Params):
            self.params = params

        if isinstance(logger, Logger):
            self._logger = logger

        if not isinstance(self.params, Params):
            return []

        collection = get_collection_name(collection)

        count_msg, _ = get_counter_message(counter=counter, total_count=total_count)

        @retry(n=5, backoff=1.5, jitter=0.2, logger=logger, prefix=f" {count_msg} ")
        def _search(collection: str, params: Params) -> list[Item]:
            catalog = self.get_catalog()
            properties = self.get_properties(collection)
            filt = self.get_filter(properties)
            kwargs = dict(
                collections=[collection],
                filter=filt,
                limit=params.max_items,
                datetime=self.get_datetime(),
                bbox=params.bbox,
                intersects=params.intersects,
                filter_lang="cql2-text",
                method="POST",
            )
            kwargs = {k: v for k, v in kwargs.items() if v is not None}

            if logger:
                logger.info(f"*{count_msg} Search request: {kwargs}")

            search = catalog.search(
                collections=[collection],
                filter=filt,
                limit=params.max_items,
                datetime=self.get_datetime(),
                bbox=params.bbox,
                intersects=params.intersects,
                filter_lang="cql2-text",
                method="POST",
            )

            return get_sorted_items(get_unique_items(list(search.items())))

        # NOTE: X-JSG and X-MET workaround -------------------------
        # > As of 2026-07-16, MAAP does not seem to support STAC parameter
        #   'sat:absolute_orbit' for 'AUX_JSG_1D'.
        # > As of 2026-07-16, MAAP does not seem to support geometry search
        #   for 'AUX_JSG_1D' and 'AUX_MET_1D'.
        is_xjsg: bool = self.params.product_type == "AUX_JSG_1D"
        is_xmet: bool = self.params.product_type == "AUX_MET_1D"
        if (
            is_xjsg
            and (
                self.params.orbit_numbers
                or self.params.start_orbit_number
                or self.params.end_orbit_number
                or self.params.intersects
                or self.params.bbox
            )
            or (is_xmet and (self.params.intersects or self.params.bbox))
        ):
            orig_params = self.params.replace()
            items: list[Item] = []

            # Search for A-NOM
            self.params = orig_params.replace(
                product_type="ATL_NOM_1B",
                product_version=None,
            )
            _items = get_sorted_items(
                get_unique_items(_search("EarthCAREL1Validated_MAAP", self.params))
            )

            _format: str = "%Y-%m-%dT%H:%M:%SZ"
            for _item in _items:
                _timestamp = time_to_str(
                    pd.Timestamp(get_file_info_from_str(_item.id)["start_sensing_time"])
                    + pd.Timedelta("00:06:00"),
                    _format,
                )
                # Search for X-JSG
                self.params = orig_params.replace(
                    start_time=_timestamp,
                    end_time=_timestamp,
                    orbit_numbers=None,
                    start_orbit_number=None,
                    end_orbit_number=None,
                    intersects=None,
                    bbox=None,
                )
                items.extend(get_sorted_items(get_unique_items(_search(collection, self.params))))
        else:
            # NOTE: End of X-JSG workaround -------------------------
            items = _search(collection, self.params)

        items = get_unique_items(items)
        items = get_sorted_items(items)

        if logger:
            logger.info(f" {count_msg} Results: {len(items)}")

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
                new_items = self.search_items(
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
