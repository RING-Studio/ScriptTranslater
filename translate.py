from typing import Callable, Optional
import os
import json


def pattern_match(pattern: str, template: str, words: list[str]) -> Optional[str]:
    var_map = dict()
    for r in pattern.split(" "):
        word = words.pop(0)
        if r.startswith("$"):
            var_map[r] = word
        elif r != word:
            return None
    if len(words) != 0:
        return None
    ret = ""
    while (t := template.find("$")) != -1:
        matched = False
        for var in var_map.keys():
            if template[t:].startswith(var):
                ret += template[:t]
                ret += var_map[var]
                template = template[t:].removeprefix(var)
                matched = True
                break
        if not matched:
            raise SyntaxError(pattern, template)
    ret += template
    return ret


class Rule:
    f: Callable[[list[str]], Optional[str]]

    @staticmethod
    def compile(pattern: str, template: str) -> Callable[[list[str]], Optional[str]]:
        return lambda words: pattern_match(pattern, template, words)

    def __init__(self, pattern: str, template: str):
        self.f = Rule.compile(pattern, template)

    def match(self, words: list[str]) -> Optional[str]:
        return self.f(words)


if __name__ == "__main__":
    with open("./script.md", "r", encoding="utf-8") as fp:
        content = fp.read().splitlines()
    with open("./rules.json", "r", encoding="utf-8") as fp:
        rule_map: dict[str, str] = json.load(fp)

    rules = list(map(lambda kv: Rule(kv[0], kv[1]), rule_map.items()))
    print(rule_map)
    print(content)

    res = []
    for line in content:
        flag = False
        for rule in rules:
            ret = rule.match(line.split(" "))
            if ret != None:
                flag = True
                res.append(ret)
                break
        if not flag:
            raise SyntaxError(line)
    print(res)
