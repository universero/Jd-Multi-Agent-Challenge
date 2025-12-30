def purify_json(raw: str) -> str:
    """
    去除 JSON 响应中的 markdown 格式
    """
    # 去除可能的 ```json 或 ``` 开头和结尾
    raw = raw.strip()
    if raw.startswith('```json'):
        raw = raw[7:]  # 移除 ```json
    elif raw.startswith('```'):
        raw = raw[3:]  # 移除 ```

    if raw.endswith('```'):
        raw = raw[:-3]  # 移除结尾的 ```

    return raw.strip()
