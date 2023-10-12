from schema_merger import OverrideStrategy, ExtensionStrategy
from json_utils import get_json, resolve_path


merge_strategy = ExtensionStrategy()


def load(path: str, strategy=merge_strategy, referrer_path=None, catalog_file=None) -> dict:
    """
    Loads the schema json object from the given path. In addition to vanilla schema loading, recursively merges declared
     base schemas according to the specified import strategy (extend/override).
    :param path: file path or web url of the schema
    :param strategy: (optional) schema merge strategy (extend/override). Default strategy is extension
    :param referrer_path: (optional) path of the referring schema. Used for resolving the relative paths.
    :param catalog_file: catalog file to locally resolve web urls. This is useful for local development and testing.
    Paths in the catalog file are relative to the catalog file itself.
    :return: merged schema
    """
    # TODO add cyclic import prevention logic
    schema = get_json(path, referrer_path, catalog_file)

    merged_base = None
    if "allOf" in schema:
        for base_schema_declaration in schema["allOf"]:
            base_ref = base_schema_declaration["$ref"]
            abs_path = resolve_path(path, referrer_path, catalog_file)
            if merged_base is None:
                merged_base = load(base_ref, strategy, abs_path, catalog_file)
            else:
                merged_base = strategy.merge(merged_base, load(base_ref, strategy, abs_path, catalog_file))

    if merged_base is not None:
        schema = strategy.merge(merged_base, schema)
        del schema['allOf']

    return schema
