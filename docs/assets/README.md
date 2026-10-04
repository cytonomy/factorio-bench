# Showcase media

The two approved screenshot paths are `showcase-desktop.png` and `showcase-mobile.png`. They show the repository's original synthetic demonstration in a local browser. They are interface captures, not Factorio screenshots, native gameplay, or measured agent results. No game art is included.

`manifest.json` records each approved file's SHA-256 digest, pixel dimensions, provenance, and completed visual review. Its schema is `factorio-bench.public-media.v1`. Each entry in `assets` contains exactly `path`, `sha256`, `width`, `height`, `provenance`, and `reviewed`; paths are relative to the repository root. `reviewed` must be `true` only after a maintainer has inspected the complete image for publication.

## Updating captures

1. Run the synthetic showcase locally and capture only its content area. Keep the synthetic-data label visible. Exclude browser chrome, account details, terminal output, and other applications.
2. Store raw captures outside version control. Export the selected images as 8-bit RGB or RGBA PNGs with only `IHDR`, `IDAT`, and `IEND` chunks. Remove metadata without changing the pixels.
3. Inspect the final exported images visually. Check readability at their intended display size and confirm that every visible detail is appropriate for a public repository.
4. Calculate each exported file's digest and dimensions, then update its manifest entry. Describe the actual capture's origin in `provenance`; do not copy a claim of review without performing it.
5. Stage each image with its corresponding manifest update and run `make check` and `make check-secrets`.

Repository checks permit only these named captures, require 64–4096 pixels per dimension and no more than 8 MiB per file, verify PNG structure and pixel-data length, and reject metadata, trailing payloads, changed digests, and mismatched dimensions. They check both the working files and the exact staged media. This narrow allowance does not permit other binary artifacts. Automated checks cannot determine whether visible pixels disclose private information; manual review remains required by the [sharing policy](../data-sharing.md).
