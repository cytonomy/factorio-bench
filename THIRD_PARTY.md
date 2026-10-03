# Third-party references and materials

Factorio-Bench is independently developed. The projects below inform the proposed design; their implementation code has not been incorporated into this repository. A citation is neither a dependency declaration nor permission to relicense someone else's work.

## Design references

| Reference | Reviewed material | Licensing boundary |
| --- | --- | --- |
| [MapleBench](https://github.com/dmarzzz/maplebench) | Architecture and evaluation patterns at `59682f0abad6469713079ffa6807237949248e3f` | The reviewed repository uses [AGPLv3](https://github.com/dmarzzz/maplebench/blob/59682f0abad6469713079ffa6807237949248e3f/LICENSE). Its covered code cannot simply be copied into this project and relabeled with this project's license. |
| [RuneBench](https://github.com/MaxBittker/RuneBench) | Task packaging and verifier behavior on `main`, reviewed 3 October 2026 | The [README states MIT](https://github.com/MaxBittker/RuneBench#license). Before incorporating any material, verify the exact revision, applicable terms, and required notices. |
| [Factorio Learning Environment](https://github.com/JackHopkins/factorio-learning-environment) | Public environment documentation and tool behavior on `main`, reviewed 3 October 2026 | Its [MIT license](https://github.com/JackHopkins/factorio-learning-environment/blob/main/LICENSE) covers its code and documentation, not Factorio game code or assets. Any future reuse must preserve the applicable notices. |
| [Factorio API](https://lua-api.factorio.com/) | Public API documentation and candidate native control mechanisms | Documentation access does not grant rights to distribute the game, its assets, or proprietary implementation. |

## Independent implementation

Use public documentation, documented interfaces, and observations from authorized runs to define behavioral requirements and tests. Cite the source and record the relevant version. Implement our harness and infrastructure from those requirements, keeping reference observations separate from our implementation choices.

Do not paste upstream implementation, translate it into another language, or make superficial rewrites as a substitute for a license review. Before incorporating third-party source, obtain the necessary rights, record its origin and exact revision, identify the affected files, preserve notices, and assess compatibility with our licensing plans. Separate commercial permission for Factorio-Bench covers only rights we control.

This policy describes the intended development process. It does not assert that a legally audited clean-room process has occurred. Source availability also does not authorize bypassing access controls or disregarding applicable terms.

## Development tools

GitHub Actions uses [actions/checkout](https://github.com/actions/checkout) and downloads [Gitleaks](https://github.com/gitleaks/gitleaks) for repository checks. The workflow records the selected revisions and download checksum. These tools are run as separate development dependencies; their source and executables are not vendored here and remain governed by their upstream terms. Git, Make, and Python are also separately installed tools.

The [LICENSE](LICENSE) file is the unchanged [official PolyForm Noncommercial 1.0.0 text](https://polyformproject.org/licenses/noncommercial/1.0.0.txt). The project's required notice is in [NOTICE](NOTICE).

## Game and deployment rights

Factorio and Space Age are Wube Software products. Factorio-Bench is not affiliated with or endorsed by Wube Software and does not distribute their executable, proprietary source, art, audio, or other game assets. Operators must obtain the permissions required for their deployment under the applicable [Factorio terms](https://www.factorio.com/terms-of-service). A separate commercial agreement for this harness does not replace those permissions.
