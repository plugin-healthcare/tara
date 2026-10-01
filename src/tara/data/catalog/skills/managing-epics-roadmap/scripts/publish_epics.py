"""Publish initiatives and epics from one markdown document to GitHub and a project board.

Usage:
  python publish_epics.py CONFIG preview SECTION   # print initiative body and first epics
  python publish_epics.py CONFIG create SECTION... # create missing initiative + epics, link, set fields
  python publish_epics.py CONFIG relink            # rewrite all epic bodies, codes -> #numbers
  python publish_epics.py CONFIG initiatives       # rewrite all initiative bodies

State (code -> issue number) is stored next to CONFIG as <config>.state.json.
"""

import json
import re
import subprocess
import sys
import time
from pathlib import Path

HEAD = re.compile(r"^(\s*[-*>|#]|\s*\d+\. |```|\*\*)")
LIST = re.compile(r"^\s*[-*]|^\s*\d+\. ")


def sh(args):
    """Run a command with retries and return stdout."""
    for attempt in range(4):
        r = subprocess.run(args, capture_output=True, text=True)
        if r.returncode == 0:
            return r.stdout.strip()
        time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"{args}: {r.stderr}")


def reflow(text):
    """Join sentence-per-line paragraphs, because GitHub renders single newlines as line breaks."""
    out = []
    for line in text.split("\n"):
        prev = out[-1] if out else ""
        block, prev_block = HEAD.match(line), HEAD.match(prev)
        if line and not block and prev and not prev_block:
            out[-1] = prev + " " + line
        elif (
            line
            and block
            and prev
            and not prev_block
            and LIST.match(line)
            or line
            and not block
            and prev
            and LIST.match(prev)
        ):
            out += ["", line]
        else:
            out.append(line)
    return "\n".join(out)


class Publisher:
    """Publish sections of the epics document using a JSON config and a state file."""

    def __init__(self, config_path):
        """Load the config and the code-to-issue state."""
        cfg_path = Path(config_path).resolve()
        self.cfg = json.loads(cfg_path.read_text())
        self.src = (cfg_path.parent / self.cfg["source"]).resolve()
        self.state_path = cfg_path.with_suffix(".state.json")
        self.state = (
            json.loads(self.state_path.read_text()) if self.state_path.exists() else {}
        )
        self.sections = self.cfg["sections"]

    def save(self):
        """Write the state file."""
        self.state_path.write_text(json.dumps(self.state, indent=2))

    def parse(self):
        """Split the document into configured sections with their intro and epics."""
        t = self.src.read_text()
        out = {}
        for name, sec in self.sections.items():
            start = t.index(sec["header"] + "\n")
            end = t.find("\n## ", start + 1)
            end = len(t) if end == -1 else end
            parts = re.split(r"^### ", t[start:end], flags=re.M)
            epics = []
            for p in parts[1:]:
                head, body = p.split("\n", 1)
                code, title = head.split(" ", 1)
                epics.append(
                    {"code": code, "title": title.strip(), "body": body.strip()}
                )
            out[name] = {"intro": parts[0].split("\n", 1)[1].strip(), "epics": epics}
        return out

    def convert(self, body):
        """Convert an epic body from the document to a GitHub issue body."""
        body = re.sub(r"^#### ", "## ", body, flags=re.M)
        body = re.sub(
            r"^(Wel|Niet|In scope|Out of scope):$", r"**\1:**", body, flags=re.M
        )
        blob = self.cfg.get("blob_prefix")
        if blob:
            body = re.sub(
                r"\]\((?:\.\./)+(docs/[^)]+)\)",
                lambda m: "](" + blob + m.group(1) + ")",
                body,
            )
        body = re.sub(r"\[([^\]]+)\]\((?!https?://)[^)]+\)", r"\1", body)
        return reflow(body).strip() + "\n"

    def link_codes(self, text):
        """Replace known epic codes with issue references."""
        codes = {k: v for k, v in self.state.items() if ":" not in k}
        if not codes:
            return text
        pat = re.compile(
            r"\b(" + "|".join(sorted(codes, key=len, reverse=True)) + r")\b"
        )
        return pat.sub(lambda m: f"#{codes[m.group(1)]}", text)

    def initiative_body(self, intro):
        """Build the initiative body from the section intro."""
        return reflow(
            f"## Omschrijving\n\n{intro}\n\n{self.cfg.get('initiative_footer', '')}\n"
        )

    def issue(self, title, body):
        """Create an issue and return its number."""
        url = sh(
            [
                "gh",
                "issue",
                "create",
                "--repo",
                self.cfg["repo"],
                "--title",
                title,
                "--body",
                body,
            ]
        )
        return int(url.rsplit("/", 1)[1])

    def set_fields(self, num, issue_type, section):
        """Add the issue to the project and set its issue type and board fields."""
        c, repo = self.cfg, self.cfg["repo"]
        item = json.loads(
            sh(
                [
                    "gh",
                    "project",
                    "item-add",
                    str(c["project_number"]),
                    "--owner",
                    c["owner"],
                    "--url",
                    f"https://github.com/{repo}/issues/{num}",
                    "--format",
                    "json",
                ]
            )
        )["id"]
        node = sh(
            [
                "gh",
                "issue",
                "view",
                str(num),
                "--repo",
                repo,
                "--json",
                "id",
                "-q",
                ".id",
            ]
        )
        sh(
            [
                "gh",
                "api",
                "graphql",
                "-f",
                f'query=mutation{{updateIssueIssueType(input:{{issueId:"{node}",issueTypeId:"{issue_type}"}}){{issue{{number}}}}}}',
            ]
        )
        fields = {**c["default_fields"], **self.sections[section].get("fields", {})}
        for field_id, option_id in fields.items():
            sh(
                [
                    "gh",
                    "project",
                    "item-edit",
                    "--project-id",
                    c["project_id"],
                    "--id",
                    item,
                    "--field-id",
                    field_id,
                    "--single-select-option-id",
                    option_id,
                ]
            )
            time.sleep(0.3)

    def create(self, names):
        """Create missing initiatives and epics for the given sections and link them."""
        data, types = self.parse(), self.cfg["issue_types"]
        for name in names:
            sec, key = self.sections[name], f"INIT:{name}"
            if key not in self.state:
                body = self.link_codes(self.initiative_body(data[name]["intro"]))
                self.state[key] = self.issue(sec["initiative_title"], body)
                self.save()
                self.set_fields(self.state[key], types["initiative"], name)
                print("initiative", name, self.state[key])
            for e in data[name]["epics"]:
                code = e["code"]
                if code not in self.state:
                    title = self.cfg["epic_title"].format(
                        prefix=sec["prefix"], code=code, title=e["title"]
                    )
                    self.state[code] = self.issue(title, self.convert(e["body"]))
                    self.save()
                    self.set_fields(self.state[code], types["epic"], name)
                    print("epic", code, self.state[code])
                if f"LINK:{code}" not in self.state:
                    sh(
                        [
                            "gh",
                            "sub-issue",
                            "add",
                            str(self.state[key]),
                            "--sub-issue-number",
                            str(self.state[code]),
                            "--replace-parent",
                            "--repo",
                            self.cfg["repo"],
                        ]
                    )
                    self.state[f"LINK:{code}"] = True
                    self.save()
                    time.sleep(0.5)

    def relink(self):
        """Rewrite all published epic bodies from the document."""
        for sec in self.parse().values():
            for e in sec["epics"]:
                if e["code"] in self.state:
                    body = self.link_codes(self.convert(e["body"]))
                    sh(
                        [
                            "gh",
                            "issue",
                            "edit",
                            str(self.state[e["code"]]),
                            "--repo",
                            self.cfg["repo"],
                            "--body",
                            body,
                        ]
                    )
                    print("relinked", e["code"])
                    time.sleep(0.3)

    def initiatives(self):
        """Rewrite all published initiative bodies from the document."""
        for name, sec in self.parse().items():
            key = f"INIT:{name}"
            if key in self.state:
                body = self.link_codes(self.initiative_body(sec["intro"]))
                sh(
                    [
                        "gh",
                        "issue",
                        "edit",
                        str(self.state[key]),
                        "--repo",
                        self.cfg["repo"],
                        "--body",
                        body,
                    ]
                )
                print("initiative", name, self.state[key])
                time.sleep(0.3)


if __name__ == "__main__":
    pub, cmd = Publisher(sys.argv[1]), sys.argv[2]
    if cmd == "preview":
        d = pub.parse()[sys.argv[3]]
        print(pub.initiative_body(d["intro"]))
        for e in d["epics"][:2]:
            print("=====", e["code"], e["title"])
            print(pub.convert(e["body"]))
        print([e["code"] for e in d["epics"]])
    elif cmd == "create":
        pub.create(sys.argv[3:])
    elif cmd == "relink":
        pub.relink()
    elif cmd == "initiatives":
        pub.initiatives()
