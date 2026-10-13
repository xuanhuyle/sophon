# Prior-art gate (bounded: 4 primary candidates, ≈1 page; checked 2026-10-13 via web search, not exhaustively)

| Candidate | What it predicts | Family / law / section path / whole-document boundaries | Licence / reproducibility (as found) |
|---|---|---|---|
| **ClauseRec** (Aggarwal et al., EMNLP 2021; [ACL](https://aclanthology.org/2021.emnlp-main.691), [arXiv 2110.15794](https://arxiv.org/abs/2110.15794)) | Two stages: (1) whether a **clause type is relevant** to a contract given its context; (2) recommending or generating clause text of that type. Uses ContractBERT. | Works at contract level, with context from the contract's other content. Governing-law conditioning and section-path structure were not checked. | Paper public; code and data availability not verified. |
| **LEDGAR** (Tuggener et al., LREC 2020; [ACL](https://aclanthology.org/2020.lrec-1.155)) | **Provision classification**: about 100k provisions from more than 60k SEC-filed contracts, about 12k labels derived semi-automatically from provision headings. | Provision-level labels from EDGAR. Whether whole-document identity and section nesting survive in the release was **not verified**. No law or family dimension. | CC BY-NC 4.0 (per ACL / ZHAW record). |
| **CUAD** (Atticus Project; [HF](https://huggingface.co/datasets/theatticusproject/cuad)) | Expert-labeled spans for **41 clause categories** in 510 EDGAR commercial contracts, used for presence/extraction QA. | Whole contracts with presence labels per category. Contract types are commercial (licence, distribution, etc.); credit agreements and SLAs not verified. Governing law is one of the 41 categories. | Licence not confirmed directly (LegalBench-derived tasks list CC BY 4.0). |
| **Material Contracts Corpus** ([arXiv 2504.02864](https://arxiv.org/html/2504.02864v1)) | A corpus, not a predictor: about 1.25M EDGAR material-contract exhibits. | Whole exhibits (so document boundaries are available). It would need family filtering and structure parsing. | Not checked. |

**Assessment:**
- Clause-type *presence/relevance* prediction from contract context is an existing task family (ClauseRec). LEDGAR shows that heading-derived provision labels are an established, noisy labeling method, as used here.
- So **no novelty is claimed** for "predict which clause types a contract should contain".
- None of the four, as far as checked, directly offers a ready benchmark for the specific question here:
  - **hierarchical** priors (family → section function → provision type inside that section),
  - **masked heading and body**,
  - **document-level** train/test separation,
  - an explicit evidenced-law/`UNKNOWN` dimension,
  - evaluation as a *search/review* queue for a governed contract-to-semantic pipeline.
- **Reuse candidates for a scaled follow-up:** CUAD (whole-document presence labels, including governing law) and the Material Contracts Corpus (document boundaries at scale). Neither was used here, because the pilot needed credit agreements and SLAs with source section paths.
- **Sophon-specific question that remains:** whether such priors measurably reduce omissions in the *governed* interpretation step (the later Jev/verification gate). Prior art on clause recommendation does not answer it, and this pilot does not either.
