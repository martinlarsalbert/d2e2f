def pop_index(df):
    if df.index.name == None:
        key = "index"
    else:
        key = df.index.name

    df = df.copy()
    df[key] = df.index
    columns = list(df.columns)
    columns.remove(key)
    columns = [key] + columns
    df = df.copy()
    df.index.name = None

    return df[columns]


def reload_kedro():
    from kedro.framework.session import get_current_session
    from kedro.framework.session import KedroSession

    with KedroSession.create(package_name="d2e2f", project_path="../../") as session:
        key = "item_of_catalog"
        session = get_current_session()
        context = session.load_context()
        catalog = context.catalog

    return catalog
