# s3_runlog.json (verbatim)

> Raw audit artifact, wrapped in Markdown for fast-track-eligible tracking. Content below is byte-for-byte the original `s3_runlog.json`. To extract: delete this header and the surrounding fence lines.

```json
[
  {
    "cmd": "pip install -e \".[dev]\"",
    "purpose": "install",
    "code": 0,
    "tail": "st-packages (from aiv-protocol==1.0.0) (0.25.2)\nRequirement already satisfied: types-pyyaml>=6.0 in /usr/local/lib/python3.11/dist-packages (from aiv-protocol==1.0.0) (6.0.12.20260518)\nRequirement already satisfied: typing_extensions>=4.6.0 in /usr/local/lib/python3.11/dist-packages (from mypy<2.0,>=1.0->aiv-protocol==1.0.0) (4.15.0)\nRequirement already satisfied: mypy_extensions>=1.0.0 in /usr/local/lib/python3.11/dist-packages (from mypy<2.0,>=1.0->aiv-protocol==1.0.0) (1.1.0)\nRequirement already satisfied: pathspec>=1.0.0 in /usr/local/lib/python3.11/dist-packages (from mypy<2.0,>=1.0->aiv-protocol==1.0.0) (1.1.1)\nRequirement already satisfied: librt>=0.8.0 in /usr/local/lib/python3.11/dist-packages (from mypy<2.0,>=1.0->aiv-protocol==1.0.0) (0.11.0)\nRequirement already satisfied: annotated-types>=0.6.0 in /usr/local/lib/python3.11/dist-packages (from pydantic<3.0,>=2.0->aiv-protocol==1.0.0) (0.7.0)\nRequirement already satisfied: pydantic-core==2.46.4 in /usr/local/lib/python3.11/dist-packages (from pydantic<3.0,>=2.0->aiv-protocol==1.0.0) (2.46.4)\nRequirement already satisfied: typing-inspection>=0.4.2 in /usr/local/lib/python3.11/dist-packages (from pydantic<3.0,>=2.0->aiv-protocol==1.0.0) (0.4.2)\nRequirement already satisfied: python-dotenv>=0.21.0 in /usr/local/lib/python3.11/dist-packages (from pydantic-settings<3.0,>=2.0->aiv-protocol==1.0.0) (1.2.2)\nRequirement already satisfied: iniconfig>=1 in /usr/local/lib/python3.11/dist-packages (from pytest<9.0,>=7.0->aiv-protocol==1.0.0) (2.3.0)\nRequirement already satisfied: packaging>=20 in /usr/lib/python3/dist-packages (from pytest<9.0,>=7.0->aiv-protocol==1.0.0) (24.0)\nRequirement already satisfied: pluggy<2,>=1.5 in /usr/local/lib/python3.11/dist-packages (from pytest<9.0,>=7.0->aiv-protocol==1.0.0) (1.6.0)\nRequirement already satisfied: pygments>=2.7.2 in /usr/local/lib/python3.11/dist-packages (from pytest<9.0,>=7.0->aiv-protocol==1.0.0) (2.20.0)\nRequirement already satisfied: coverage>=5.2.1 in /usr/local/lib/python3.11/dist-packages (from coverage[toml]>=5.2.1->pytest-cov<6.0,>=4.0->aiv-protocol==1.0.0) (7.14.1)\nRequirement already satisfied: execnet>=2.1 in /usr/local/lib/python3.11/dist-packages (from pytest-xdist<4.0,>=3.0->aiv-protocol==1.0.0) (2.1.2)\nRequirement already satisfied: markdown-it-py>=2.2.0 in /usr/local/lib/python3.11/dist-packages (from rich<14.0,>=13.0->aiv-protocol==1.0.0) (4.2.0)\nRequirement already satisfied: shellingham>=1.3.0 in /usr/local/lib/python3.11/dist-packages (from typer<1.0,>=0.9->aiv-protocol==1.0.0) (1.5.4)\nRequirement already satisfied: annotated-doc>=0.0.2 in /usr/local/lib/python3.11/dist-packages (from typer<1.0,>=0.9->aiv-protocol==1.0.0) (0.0.4)\nRequirement already satisfied: mdurl~=0.1 in /usr/local/lib/python3.11/dist-packages (from markdown-it-py>=2.2.0->rich<14.0,>=13.0->aiv-protocol==1.0.0) (0.1.2)\nChecking if build backend supports build_editable: started\nChecking if build backend supports build_editable: finished with status 'done'\nBuilding wheels for collected packages: aiv-protocol\n  Building editable for aiv-protocol (pyproject.toml): started\n  Building editable for aiv-protocol (pyproject.toml): finished with status 'done'\n  Created wheel for aiv-protocol: filename=aiv_protocol-1.0.0-py3-none-any.whl size=18390 sha256=6c60a225339d97a6f080fc6fdf711f76e8168774aeb52841a890c277c2ccbdcf\n  Stored in directory: /tmp/pip-ephem-wheel-cache-ha94kmcr/wheels/c3/9a/7b/f95dbbf34f90376002fb4eb224215229f11917fac315c1e4f3\nSuccessfully built aiv-protocol\nInstalling collected packages: aiv-protocol\n  Attempting uninstall: aiv-protocol\n    Found existing installation: aiv-protocol 1.0.0\n    Uninstalling aiv-protocol-1.0.0:\n      Successfully uninstalled aiv-protocol-1.0.0\nSuccessfully installed aiv-protocol-1.0.0\n\nWARNING: Running pip as the 'root' user can result in broken permissions and conflicting behaviour with the system package manager. It is recommended to use a virtual environment instead: https://pip.pypa.io/warnings/venv\n"
  },
  {
    "cmd": "pytest --cov=aiv --cov-report=term-missing --junitxml=artifacts/junit.xml",
    "purpose": "test",
    "code": 4,
    "tail": "\nERROR: usage: pytest [options] [file_or_dir] [file_or_dir] [...]\npytest: error: unrecognized arguments: --cov=aiv --cov-report=term-missing\n  inifile: /home/user/aiv-protocol/pyproject.toml\n  rootdir: /home/user/aiv-protocol\n\n"
  },
  {
    "cmd": "pytest --cov=aiv --cov-report=term-missing --junitxml=artifacts/junit.xml",
    "purpose": "coverage",
    "code": 4,
    "tail": "\nERROR: usage: pytest [options] [file_or_dir] [file_or_dir] [...]\npytest: error: unrecognized arguments: --cov=aiv --cov-report=term-missing\n  inifile: /home/user/aiv-protocol/pyproject.toml\n  rootdir: /home/user/aiv-protocol\n\n"
  }
]
```
