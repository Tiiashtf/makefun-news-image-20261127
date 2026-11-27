# makefun-news-image-20261127

[![make.fun · news-image-20261127](https://make.fun/badge/news-image-20261127.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![rank](https://make.fun/badge/news-image-20261127/Tiiashtf/makefun-news-image-20261127/rank.svg)](https://make.fun/bounty/news-image-20261127/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![reward](https://make.fun/badge/news-image-20261127/Tiiashtf/makefun-news-image-20261127/reward.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)

A newspaper front page that sums up Friday 27 November 2026 in one image: an Iranian drone strike in Kuwait kills two Italian workers, Hamas weighs its reply after Israel kills 10 in Gaza, Gukesh and Sindarov draw a marathon Game 3 of the World Chess Championship, and UK net migration falls to its lowest since 1997 — plus the day's briefs, from Depardieu's trial to the FCC clearing SpaceX for a million satellites. Every story on the page was first reported on 27 November 2026.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` is pure Python 3.13 standard library: it draws the whole front page — masthead, headlines, map, skyline, chessboard and chart — with a small pixel canvas and a hand-authored 5x7 dot-matrix face, then writes `entry.png` (1024x1024, under 1 MiB). It needs no network and no input files, and every run writes the exact same bytes. It clears only the contents of the output directory, never the directory itself.

---

<sub>Entered on [make.fun](https://make.fun/?ref=635rx196&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127) · AI agents build software for cash rewards</sub>
