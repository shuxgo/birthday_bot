from string import Formatter


class SafePromptRenderer:
    def render(self, template: str, variables: dict[str, str]) -> str:
        expected = {field for _, field, _, _ in Formatter().parse(template) if field}
        missing = sorted(expected - set(variables))
        if missing:
            raise ValueError(f"В промте не хватает переменных: {', '.join(missing)}")
        return template.format(**variables)

