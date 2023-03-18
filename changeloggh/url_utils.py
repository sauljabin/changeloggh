def url_join(segments):
    return "/".join([segment.strip("/") for segment in segments])
