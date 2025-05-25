# `Alpha-gfn`: Mining formulaic alpha factors with generative flow networks

This project is came from https://github.com/nshen7/alpha-gfn

---
**Please cite this repository if you utilize any code provided herein.:**
- **APA style:**  Shen, N. (2024). Alpha-gfn: Mining formulaic alpha factors with generative flow networks. [https://github.com/user/my-project-name](https://github.com/nshen7/alpha-gfn)
- **BibTeX style:**
  ```
  @software{shen2024,
            author = {Shen, Ning},
            title = {Alpha-gfn: Mining formulaic alpha factors with generative flow networks},
            year = {2024},
            url = {https://github.com/nshen7/alpha-gfn}
        }
  ```
----
In this repo, I made following changes:

1. Remove the old way to import FEATURE and FEATURE_DATA, and load the features from Duckdb. In this case, you need to setup your own feature database.

the database should be like:

Date,instrument,open,close,feature1, feature2, ...

The forward return is calculated by close and open, so these two columns are necessary.

2. Add more operations.