#!/bin/sh
# Fetch the Hobbit BeBox board photographs listed in MANIFEST.md into this
# directory and check them against SHA256SUMS.  The images stay out of git
# (.gitignore): none of their sources shows redistribution terms.
#
#   cd hobbit/docs/bebox_photos && sh fetch.sh     # fetch what is missing, check all
#   sh fetch.sh --check                            # check only
set -eu
cd "$(dirname "$0")"

fetch_jpeg() {
    url=$1
    output=$2
    if [ -f "$output" ]; then
        return 0
    fi
    temporary="${output}.part"
    # Flickr's image host refuses curl's default user agent.
    curl --fail --location --proto '=https' --retry 3 \
        --user-agent 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)' \
        --output "$temporary" "$url"
    test "$(head -c 3 "$temporary" | od -An -tx1 | tr -d ' ')" = 'ffd8ff'
    mv "$temporary" "$output"
}

if [ "${1:-}" != "--check" ]; then
    # Fumihiko Shibata, BeBox GuideBook, photos 5-8, as posted to the Haiku
    # forum on 2020-10-08 (larger copies were at lorezan.free.fr/BeBoxHobbit/)
    H=https://discuss.haiku-os.org/uploads/default/original/2X
    fetch_jpeg "$H/4/4f471d6588b82a1bea5c1d619e58b82b65d04933.jpeg" shibata_motherboards.jpeg
    fetch_jpeg "$H/b/bb78211eb75496dea683d53c3b3f626cd3c229e9.jpeg" shibata_rev1.jpeg
    fetch_jpeg "$H/9/97db8a1cb9d1f56c06175c292babc74f0952cfae.jpeg" shibata_rev2.jpeg
    fetch_jpeg "$H/f/f428c207b7ff88de96b3fbd3202f01d178633cac.jpeg" shibata_rev4.jpeg
    # Colin M. Strickland, Flickr album "Original BeBox", 2011-06-17
    # (S/N 9308000017, Rev. A), the "_b" (1024 px) size
    F=https://live.staticflickr.com
    fetch_jpeg "$F/2505/5841494811_bcaab9902a_b.jpg" strickland_5841494811_b.jpg
    fetch_jpeg "$F/5070/5841550383_6a4d4ed42b_b.jpg" strickland_5841550383_b.jpg
    fetch_jpeg "$F/5157/5841616027_f61d4c6498_b.jpg" strickland_5841616027_b.jpg
    fetch_jpeg "$F/3579/5841616289_2a2c587d2f_b.jpg" strickland_5841616289_b.jpg
    fetch_jpeg "$F/2436/5842009852_d3cf117f29_b.jpg" strickland_5842009852_b.jpg
    fetch_jpeg "$F/3420/5842090860_d51f804fb5_b.jpg" strickland_5842090860_b.jpg
fi

shasum -a 256 -c SHA256SUMS
