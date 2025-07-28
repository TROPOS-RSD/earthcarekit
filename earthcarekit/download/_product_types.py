from ._types import CollectionStr, ProductTypeStr, ProductTypeVersion


def get_collection_names_matching_product_availability(
    product: ProductTypeVersion,
    collection_product_type_dict: dict[CollectionStr, list[ProductTypeStr]],
) -> list[CollectionStr]:
    """Returns names of collections that contain the desired product according to the given `dict`."""
    return [k for k, v in collection_product_type_dict.items() if product.type in v]
