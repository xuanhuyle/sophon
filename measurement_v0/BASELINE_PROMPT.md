# Baseline prompt (frozen, verbatim)

Sent as the first message of a fresh Claude Code cloud session with **no repository attached** (no Sophon code, notes or oracle on its filesystem). The two runs differ only in `<SHA>` and `<LABEL>`; the label is an opaque run name and does not reveal which revision is pre- or post-fix.

- Run `baseline-A`: `<SHA>` = `5152b5f7c325717d84a0b67955594a4b12752dde`
- Run `baseline-B`: `<SHA>` = `5d88007d90b8a8b77987e319875a43bfd6c8d17f`

`<PARENT>` = the orchestrating session id, used only so the run can return its JSON.

---

You are a software engineer doing a compliance review of an open-source rules-as-code system. Work as a competent engineer normally would: read the code and its git history up to the pinned commit, run the native model and its own tests, write small scripts, and reason from the governing text. You may use your own background knowledge.

**System under review:** PolicyEngine-US at commit `<SHA>`. Obtain it only like this:

```
git init pe && cd pe && git fetch --depth 500 https://github.com/PolicyEngine/policyengine-us <SHA> && git checkout FETCH_HEAD
```

Its `uv.lock` lists dependency versions. Python 3.11–3.13 works; for example `pip install policyengine-core==3.30.2 numpy==2.4.1 pandas==3.0.0 spm-calculator==0.3.1 microdf-python==1.2.1 tables==3.11.1 tqdm` in a venv, then run Python with the checkout on `PYTHONPATH`.

**Governing sources (pinned — fetch exactly these and check the sha256):**
- 7 CFR § 273.10, CFR 2025 edition (revised as of 1 January 2025): https://www.govinfo.gov/content/pkg/CFR-2025-title7-vol4/xml/CFR-2025-title7-vol4-sec273-10.xml (sha256 `614a2334b335d953df58323e2728c61eb328fc811ba8d887494f798072659b76`)
- 7 U.S.C. § 2017, U.S. Code 2024 edition: https://www.govinfo.gov/content/pkg/USCODE-2024-title7/html/USCODE-2024-title7-chap51-sec2017.htm (sha256 `6e06aad1a1c3d64df1f01bb90b1a71416ca8ac774dec86c80447879ed396467b`)

**Question.** For an eligible Texas SNAP household of 3 people in a non-initial month (January 2026), does the implementation's computation of the **monthly SNAP allotment from the household's net monthly income** conform to these governing sources? In scope: the step(s) from net monthly income (as determined under 7 CFR 273.10(e)(1)) to the monthly allotment (7 CFR 273.10(e)(2) and 7 U.S.C. 2017(a)). Out of scope: which deductions make up net income, eligibility tests, and the dollar values of the maximum allotment tables. Where a governing provision gives the State a choice, say so rather than assuming Texas's choice.

**Rules.** Do not look at PolicyEngine-US commits, branches, issues, pull requests, releases, changelogs or discussions from after the pinned commit, and do not use web search. Use only the pinned checkout, the two pinned sources, PyPI packages and your own knowledge. Timebox: about 60 minutes. Do not push anything anywhere.

**Output.** Finish with exactly one fenced JSON block (also save it as `baseline_report.json`):

```json
{
  "revision": "<SHA>",
  "overall_verdict": "CONFORMS | DOES_NOT_CONFORM | CANNOT_DETERMINE",
  "findings": [
    {"id": "F1",
     "governing_citation": "exact provision",
     "implementation_location": "file/variable",
     "verdict": "CONFORMS | DOES_NOT_CONFORM | CANNOT_DETERMINE | STATE_OPTION_DEPENDENT",
     "description": "what the source requires vs what the code does",
     "evidence": "commands run and the observed output"}
  ],
  "commands_run": ["..."],
  "limitations": "..."
}
```

List every in-scope requirement you checked, including the ones that conform. When finished, send the same JSON block as a message to session `<PARENT>` using the send_message tool if you have it; then stop.
