# Sources and attribution

Reviewed on 2026-11-10. This is an adapted method for `inkayat/skills`, not an official release from any source author. These references record provenance and design choices; they do not add runtime instructions.

## Immutable source points

- **K** — [multica-ai/andrej-karpathy-skills: skills/karpathy-guidelines/SKILL.md](https://github.com/multica-ai/andrej-karpathy-skills/blob/2c606141936f1eeef17fa3043a72095b4765b9c2/skills/karpathy-guidelines/SKILL.md). Commit `2c606141936f1eeef17fa3043a72095b4765b9c2`; file blob `6a62d0441753157ca6ca50479e490c2948033adb`.
- **P** — [DietrichGebert/ponytail: skills/ponytail/SKILL.md](https://github.com/DietrichGebert/ponytail/blob/96608e078b2d5ea607c5c3b8b5a54d1c1fba6846/skills/ponytail/SKILL.md). Commit `96608e078b2d5ea607c5c3b8b5a54d1c1fba6846`; file blob `d64edd32265ba21cbf5270158f04e97d96925f27`.
- **T** — [cursor/plugins: pstack/skills/principle-test-behavior-not-implementation/SKILL.md](https://github.com/cursor/plugins/blob/de8ee15dd1194627d21eb5fcd41cb1873208dabb/pstack/skills/principle-test-behavior-not-implementation/SKILL.md). Commit `de8ee15dd1194627d21eb5fcd41cb1873208dabb`; file blob `78c9389bfe707d6d56485ade32c59150958228f9`.
- **S** — [cursor/plugins: pstack/skills/principle-subtract-before-you-add/SKILL.md](https://github.com/cursor/plugins/blob/de8ee15dd1194627d21eb5fcd41cb1873208dabb/pstack/skills/principle-subtract-before-you-add/SKILL.md). Commit `de8ee15dd1194627d21eb5fcd41cb1873208dabb`; file blob `b8740ba6f06922d8e7ef3b23f9fb16e0fc4a876f`.

- **K:** sections 1–4 supply assumptions, scope discipline, focused changes, and observable completion criteria. This is Multica's interpretation of Karpathy's observations, not a claim that Karpathy authored this skill.
- **P:** “Before you write,” “The smallest complete change,” and “Never cut” supply impact tracing, reuse preferences, completeness, and safeguards. Session modes and formatting constraints are omitted.
- **T:** the two imagined edits inform behavior-focused verification: catch a behavioral break while allowing an equivalent internal refactor.
- **S:** inspected as a competing approach; broad subtraction-first cleanup is not adopted.

Our consequential-ambiguity rule, allowance for justified single-use abstractions, explicit-options protection, risk-based checks, and host-neutral scope are adaptation decisions. Their expected benefits are reasoned hypotheses. The user-facing discussion and scenario review live in the repository's decision record; the installed skill needs only this folder.

## License observations

K's pinned skill frontmatter and repository README say MIT. The pinned root listing has no standalone LICENSE file. No copyright holder or missing notice has been invented. Its principles are restated; the upstream package is not vendored.

P and pstack provide the MIT notices below. They are retained with this adaptation. These observations describe the inspected files, not an independent legal determination.

### Ponytail notice

Source: [LICENSE](https://github.com/DietrichGebert/ponytail/blob/96608e078b2d5ea607c5c3b8b5a54d1c1fba6846/LICENSE); blob `715d483338cea4365f0d91a27799cf61226d6bcf`.

MIT License

Copyright (c) 2026 DietrichGebert

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

### pstack notice

Source: [LICENSE](https://github.com/cursor/plugins/blob/de8ee15dd1194627d21eb5fcd41cb1873208dabb/pstack/LICENSE); blob `6b5400237fdf6545be0b8fae370d6f2fcff8fb25`.

MIT License

Copyright (c) 2026 Lauren Tan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
